# Minimal Telegram Guard

A lightweight Telegram bot built with **Pyrogram 2.x** for basic group moderation. The bot focuses on two features only and stores all data in MongoDB.

## Features

- **Bio Link Filter** – blocks users with Telegram links in their bio unless approved
- **Auto Delete Timer** – automatically deletes all messages after a configured delay
- Admins manage everything via the `/panel` button menu

## Setup

1. Install Python 3.10+ and clone the repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in `API_ID`, `API_HASH`, `BOT_TOKEN` and `MONGO_URI`.
   Optional: `SUPPORT_LINK` and `DEV_LINK` to change panel links.
4. Run the bot:
   ```bash
   python -m oxeign.main
   ```

## Credits

Based on the original project by [@Oxeign](https://t.me/Oxeign).
