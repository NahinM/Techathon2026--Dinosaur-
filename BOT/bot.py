import os
import discord
from discord.ext import commands, tasks
import google.generativeai as genai
import json
import aiohttp
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# 1. Load the hidden variables from the .env file
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

# 🚨 SECURITY FIRST: The tokens are safely loaded from the hidden .env file
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = os.getenv("API_URL", "http://127.0.0.1:5000/api/devices")

# 2. Initialize Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Setup Bot Intets & Prefix
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True # Needed to find channels for alerts
bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# FETCH DATA FROM MEMBER 3'S BACKEND
# ==========================================
async def fetch_backend_data():
    """Fetches live data from the FastAPI backend"""
    try:
        async with aiohttp.ClientSession() as session:
            # Connects to Member 3's server
            async with session.get(API_URL) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
    except Exception as e:
        print(f"Error connecting to backend: {e}")
        return None

async def get_ai_reply(prompt):
    """Helper function to talk to Gemini"""
    response = model.generate_content(prompt)
    return response.text

# ==========================================
# BONUS FEATURE: PROACTIVE ALERTS (Runs every 5 mins)
# ==========================================
@tasks.loop(minutes=5)
async def check_anomalies():
    """Checks the backend for devices left on after 5 PM or for > 2 hours"""
    data = await fetch_backend_data()
    if not data:
        return # Skip this check if backend is down
    
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # We use Gemini to detect the anomalies to save us from writing complex time-parsing code!
    prompt = f"""
    You are a strict office security AI. 
    The current exact time is: {current_time_str}
    Here is the live office JSON data: {json.dumps(data)}
    
    Check for two rules:
    1. Are any devices currently "ON" while the current time is after 17:00 (5:00 PM)?
    2. Has any device been "ON" for more than 2 hours? (Look at 'last_changed' compared to current time).
    
    If EITHER rule is broken, write a short, urgent 1-sentence warning (e.g., "🚨 ALERT: 2 fans in Work Room 2 are left on and it's past 5 PM!").
    If NO rules are broken, reply EXACTLY with the word: NO_ALERT
    """
    
    reply = await get_ai_reply(prompt)
    
    # If Gemini detected an alert, broadcast it to the server
    if "NO_ALERT" not in reply:
        # Find the first text channel in the server to send the alert to
        for guild in bot.guilds:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    await channel.send(reply)
                    break # Only send to one channel per server

# ==========================================
# BOT EVENTS & COMMANDS
# ==========================================
@bot.event
async def on_ready():
    print(f'✅ SUCCESS! Logged in as {bot.user.name}')
    print('Ready for Hackathon testing: Type !status, !room <name>, or !usage')
    
    # Start the background anomaly checker when the bot boots up
    if not check_anomalies.is_running():
        check_anomalies.start()
        print('🚨 Proactive Anomaly alerts are running in the background.')

@bot.command(name="status")
async def status(ctx):
    """Hackathon Requirement: !status"""
    await ctx.send("🔍 Checking the office sensors...")
    data = await fetch_backend_data()
    
    if not data:
        await ctx.send("❌ Uh oh! I couldn't connect to the backend server. Is Member 3's API running?")
        return
    
    prompt = f"""
    You are a friendly office assistant. The user just asked for the office status.
    Here is the live JSON data from the office sensors: {json.dumps(data)}
    
    Summarize exactly what is turned ON right now in 2-3 short sentences. 
    Format it similar to: "Drawing Room: 1 fan ON, 2 lights ON. Work Room 1: all off."
    Do not use markdown blocks and do not show raw JSON.
    """
    reply = await get_ai_reply(prompt)
    await ctx.send(reply)

@bot.command(name="room")
async def room(ctx, *, room_name: str):
    """Hackathon Requirement: !room <name>"""
    await ctx.send(f"🚪 Peeking into the {room_name}...")
    data = await fetch_backend_data()
    
    if not data:
        await ctx.send("❌ Uh oh! I couldn't connect to the backend server.")
        return
    
    prompt = f"""
    You are a friendly office assistant. The user specifically asked for the status of the room named: '{room_name}'.
    Here is the full office JSON data: {json.dumps(data)}
    
    Find the room they asked about and tell them what devices are currently ON. 
    If all devices are OFF in that room, tell them it's completely off. 
    If the room name doesn't exist in the data at all, politely let them know they made a typo.
    Keep it to exactly 2 sentences and sound conversational.
    """
    reply = await get_ai_reply(prompt)
    await ctx.send(reply)

@bot.command(name="usage")
async def usage(ctx):
    """Hackathon Requirement: !usage"""
    await ctx.send("⚡ Calculating current power consumption...")
    data = await fetch_backend_data()
    
    if not data:
        await ctx.send("❌ Uh oh! I couldn't connect to the backend server.")
        return
    
    prompt = f"""
    You are a smart energy-monitoring assistant. The boss wants to know the power usage.
    Here is the live JSON data: {json.dumps(data)}
    
    Rules for math:
    - Every Fan that is "ON" draws 60 Watts.
    - Every Light that is "ON" draws 15 Watts.
    - Devices that are "OFF" draw 0 Watts.
    
    1. Calculate the total watts currently being used across all rooms.
    2. Estimate a realistic "Today's estimated usage" in kWh based on the current draw (e.g., if total is high, estimate around 4.5 kWh).
    
    Reply conversationally. You MUST include both the current total watts and the estimated daily kWh. 
    Format it similar to: "Total power right now: X Watts. Today's estimated usage: Y kWh. Here is the breakdown: [List rooms]".
    Do not show your math steps, just the final answer.
    """
    reply = await get_ai_reply(prompt)
    await ctx.send(reply)

# Start the bot
if __name__ == "__main__":
    if DISCORD_TOKEN is None:
        print("❌ ERROR: DISCORD_TOKEN is empty! Make sure your .env file is in the same folder as bot.py.")
    else:
        bot.run(DISCORD_TOKEN)