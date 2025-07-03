# Minimal Telegram Guard

A lightweight Telegram bot built with **Pyrogram 2.x** for basic group moderation. The bot focuses on two features only and stores all data in MongoDB.

## Features

- **Bio Link Filter** – blocks users with Telegram or other invite links in their bio and deletes the join message
- **Spam Link Filter** – deletes messages that contain spam links and warns the sender
- **Auto Delete Timer** – automatically deletes all messages after a configured delay
- Admins manage everything via the `/panel` button menu

## Setup

1. Install Python 3.10+ and clone the repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in `API_ID`, `API_HASH`, `BOT_TOKEN` and `MONGO_URI`.
   Optional: `SUPPORT_LINK`, `DEV_LINK` and `PANEL_HEADER_URL` to change panel links and header image.
4. Run the bot:
   ```bash
   python -m oxeign.main
   ```

## Usage

- Use `/panel`, `/start`, `/help` or `/menu` in a group to open the control panel.
- Admins can `/approve` or `/unapprove` a user by replying to one of their messages.

## Credits

Based on the original project by [@Oxeign](https://t.me/Oxeign).
