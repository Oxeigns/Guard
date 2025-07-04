# OxeignBot

OxeignBot is a modular Telegram moderation bot built with [Pyrogram](https://docs.pyrogram.org/). It provides several moderation utilities with a simple inline control panel and stores its configuration in a MongoDB database.

## Features

- Toggleable edit deletion, auto delete, link filter (with warnings) and bio link filter
- Admin commands: `/ban`, `/kick`, `/mute`, `/approve`
- Inline control panel available via `/start`, `/menu`, `/help`, or `/settings`
- Group metadata logging (title, owner ID, photo URL)
- MongoDB persistence using `motor`

## Setup

1. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in **all** required variables (`API_ID`,
   `API_HASH`, `BOT_TOKEN`). If any of these are missing the bot will exit with a
   clear error message. Ensure `MONGO_URI` points to a reachable MongoDB
   instance.
3. Run the bot
   ```bash
   python main.py
   ```

## License

MIT
