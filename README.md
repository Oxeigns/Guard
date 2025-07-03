# Telegram Guard Bot

A modern Telegram moderation bot built with Pyrogram and MongoDB. The bot scans user bios for links, issues warnings, and permanently mutes repeat offenders. It also offers message auto-deletion and approval controls via an inline panel.

## Setup
1. Install Python 3.10+
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in values.
4. Run `python main.py`

### Required Environment Variables

- `API_ID` and `API_HASH` from [my.telegram.org](https://my.telegram.org)
- `BOT_TOKEN` from [@BotFather](https://t.me/BotFather)
- `MONGO_URI` connection string to your MongoDB instance
