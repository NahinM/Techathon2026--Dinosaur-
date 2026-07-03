import os
import discord
from discord.ext import commands
import google.generativeai as genai
import json
from dotenv import load_dotenv # <-- MISSING LINE 1

# Load the hidden variables from the .env file BEFORE getting them
load_dotenv() # <-- MISSING LINE 2

# 🚨 SECURITY FIRST: The tokens are now safely loaded from the hidden .env file
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 1. Initialize Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Change prefix to "!" to match the Hackathon PDF requirements
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# ==========================================
# MOCK DATA (Use this until the backend API is ready)
# ==========================================
def get_mock_data():
    return {
        "Drawing Room": {
            "devices": [
                {"id": "fan_1", "type": "Fan", "power_draw": 60, "status": "ON"},
                {"id": "light_1", "type": "Light", "power_draw": 15, "status": "OFF"}
            ]
        },
        "Work Room 1": {
            "devices": [
                {"id": "fan_2", "type": "Fan", "power_draw": 60, "status": "OFF"},
                {"id": "light_2", "type": "Light", "power_draw": 15, "status": "ON"}
            ]
        }
    }

async def get_ai_reply(prompt):
    """Helper function to talk to Gemini"""
    response = model.generate_content(prompt)
    return response.text

# ==========================================
# BOT EVENTS & COMMANDS
# ==========================================

@bot.event
async def on_ready():
    print(f'✅ SUCCESS! Logged in as {bot.user.name}')
    print('Type !status in your Discord server to test it.')

@bot.command(name="status")
async def status(ctx):
    """Hackathon Requirement: !status"""
    # Send a quick holding message so the user knows the bot is thinking
    await ctx.send("Checking the office sensors...")
    
    # Get the fake data (Later, Member 3 will change this to fetch from their API)
    data = get_mock_data()
    
    # Prompt the AI to act like a friendly assistant
    prompt = f"""
    You are a friendly office assistant. The user just asked for the office status.
    Here is the live JSON data from the office sensors: {json.dumps(data)}
    Summarize what is turned ON right now conversationally in exactly 2 sentences. 
    Sound like a human, do not use markdown, and do not show raw JSON.
    """
    
    reply = await get_ai_reply(prompt)
    await ctx.send(reply)

@bot.command(name="usage")
async def usage(ctx):
    """Hackathon Requirement: !usage"""
    await ctx.send("Calculating power usage...")
    
    # TODO: Add usage logic here! 
    # Try writing a prompt for Gemini that calculates the total watts from the mock data!
    await ctx.send("Usage command is under construction!")

# Run the bot
if DISCORD_TOKEN is None:
    print("❌ ERROR: DISCORD_TOKEN is empty! Make sure your .env file is in the same folder as bot.py and spelled correctly.")
else:
    bot.run(DISCORD_TOKEN)