# OxeignBot

OxeignBot is a modular Telegram moderation bot built with [Pyrogram](https://docs.pyrogram.org/).  It provides several moderation utilities with a simple inline control panel and stores its configuration in a local SQLite database.

## Features

- Toggleable edit deletion, auto delete, link filter and bio link filter
- Admin commands: `/ban`, `/kick`, `/mute`, `/approve`
- Inline control panel available via `/start`, `/menu`, `/help`, or `/settings`
- Group metadata logging (title, owner ID, photo URL)
- SQLite persistence using `aiosqlite`

## Setup

The source code is organised into `handlers/` for bot commands and message
handlers, and `utils/` for helper utilities and database access.

1. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file based on `.env.example` and fill in your API credentials.
3. Run the bot
   ```bash
   python main.py
   ```

## License

MIT
