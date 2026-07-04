# Techathon2026 - Dinosaur

An office monitoring system with live device updates, a web dashboard, and a Discord bot for checking room status and total power usage.

## Overview

This project monitors office devices in real time. The office has two rooms, and each room contains five devices: three lights and two fans. When any device changes state, the dashboard updates live through WebSocket events, and the Discord bot can report the current office status from the backend.

## System Design

The high-level system design is shown below.

![System diagram](docs/system-diagram.png)

## Web Dashboard

The dashboard presents the live office state, power usage, and alerts in a single view.

![Web dashboard](docs/web-dashboard.png)

## ESP32 Monitoring Circuit

The office devices are monitored through the ESP32 circuit used in the Drawing Room for lights and fans.

![ESP32 Device Monitoring Circuit - Drawing Room (Lights & Fans)](docs/ESP32.png)

## Features

- Live dashboard updates over WebSocket
- Room-by-room device status view
- Current power usage summary
- Discord bot status commands
- Simulator script for pushing device state into the backend

## Project Structure

- `backend/` - Flask API and Socket.IO server
- `frontend/` - Vite + React dashboard UI
- `BOT/` - Discord bot
- `simulator/` - Device state simulator
- `requirements.txt` - Python dependencies for backend, bot, and simulator

## Setup

Install the Python dependencies before running the backend, Discord bot, or simulator.

### Python environment

From the repo root, create and activate a virtual environment if you want one, then install the Python packages:

```bash
pip install -r requirements.txt
```

If you are using Windows PowerShell, a typical virtual environment flow is:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Running the Project

After installing dependencies, start each part of the project from its own folder.

### Frontend

From the `frontend` folder:

```bash
npm i
npm run dev
```

### Backend

From the `backend` folder:

```bash
python app.py
```

### Discord Bot

From the `BOT` folder:

```bash
python bot.py
```

### Simulator

From the `simulator` folder:

```bash
python simulator.py
```

## Environment Variables

If you run into startup issues, check your environment variables and `.env` files.

Set the following values in the appropriate `.env` file(s):

- `DISCORD_TOKEN`
- `GROQ_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_PUBLISHABLE_KEY`

The backend also supports `SUPABASE_SERVICE_ROLE_KEY` if you prefer to use it.

## Discord Bot Commands

- `!status` - Shows the current status of all rooms
- `!room <name>` - Shows the status of a specific room, for example `!room work1`
- `!usage` - Shows the current total power usage

## Dashboard

The dashboard shows a live office view with WebSocket updates, room statistics, alerts, and power usage information.

## Notes

- Make sure the backend is running before starting the frontend dashboard.
- Start the simulator if you want to push device state changes into the backend.
- If the bot cannot connect, double-check the Discord token, Groq key, and Supabase settings in your `.env` file.
