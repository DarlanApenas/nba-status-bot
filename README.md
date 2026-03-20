# 🤖 Clancy Discord Bot - NBA Info

This is a Python-based Discord bot that returns detailed information about NBA players and live game scores using the `nba_api`.

  <img width="330" height="415" alt="image" src="https://github.com/user-attachments/assets/c2cf340e-2cfe-4116-b966-94b800811379" />  


## Features

- `!player player name` command returns:
  - Full name, height (in meters), weight (in kg)
  - Current team and position
  - College, draft year and draft pick
  - Latest season stats (PTS, AST, REB)
  - Player's official photo

- `!jogos` command returns:
  - All NBA games scheduled for today
  - Live score and game clock (e.g. `1:58 — Q3`)
  - Home and away team with wins/losses record
  - Both team logos combined in a single image
  - Filter by team tricode (e.g. `!jogos MIA`)


## How to Use

### 1. Clone the repository

```bash
git clone https://github.com/your-username/nba-discord-bot.git
cd nba-discord-bot
```

### 2. Install GTK Runtime (required for logo rendering)

Download and install the GTK3 Runtime for Windows (includes Cairo):  
👉 https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

> Make sure to check **"Add to PATH"** during installation, then restart your terminal.  
> On Linux (e.g. Railway, Render), Cairo is installed automatically via the included `Dockerfile`.

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create a .env file
```bash
ACESS_TOKEN=your_token_here
```

### 5. Run the bot
```bash
python main.py
```

## Deploying with Docker (Linux hosts)

A `Dockerfile` is included for easy deployment on Railway, Render, Fly.io, etc.  
It installs Cairo automatically via `apt`, so no manual setup is needed on Linux hosts.

```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y libcairo2 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

## Available Commands

| Command | Description |
|---|---|
| `!ping` | Responds with Pong! |
| `!player LeBron James` | Fetches complete player data |
| `!jogos` | Shows all NBA games today |
| `!jogos MIA` | Shows only Miami Heat games today |

## Credits

- [nba_api](https://github.com/swar/nba_api) — Official Python client for NBA statistics
- [discord.py](https://github.com/Rapptz/discord.py) — Python library for building Discord bots
- [cairosvg](https://cairosvg.org/) — SVG to PNG conversion for team logos
