# OxeignBot

OxeignBot is a modular Telegram moderation bot built with [Pyrogram](https://docs.pyrogram.org/). It provides several moderation utilities with a simple inline control panel and stores its configuration in a local SQLite database.

## Features

- Toggleable edit deletion, auto delete, link filter and bio link filter
- Custom punishments (`delete`, `warn`, `ban`) for link rules
- Admin commands: `/ban`, `/kick`, `/approve`, `/setautodelete`, `/setpunishment`, `/setwarnlimit`
- Inline control panel available via `/start`, `/menu`, `/help`, or `/settings`
- Group metadata logging (title, owner ID, photo URL)
- SQLite persistence using `aiosqlite`

## Setup

1. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file based on `.env.example` and fill in your API credentials.
3. Run the bot
   ```bash
   python oxeignbot.py
   ```

## License

MIT
