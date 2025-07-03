# Guard

Guard is a simple moderation bot built with Pyrogram. It stores data in MongoDB and requires a few environment variables before running. The bot reads these variables from the environment (or a `.env` file) on startup.

## Required environment variables

- `BOT_TOKEN` – Telegram bot token for your bot.
- `API_ID` – integer API ID from https://my.telegram.org.
- `API_HASH` – API hash from https://my.telegram.org.
- `MONGO_URI` – MongoDB connection string. If the URI does not include a database name, also set `MONGO_DB_NAME`.
- `MONGO_DB_NAME` – *(optional)* name of the MongoDB database when it is not part of `MONGO_URI`. Defaults to `guard`.
- `LOG_CHANNEL_ID` – Telegram channel ID where the bot sends log messages.

## Setup

Install dependencies and create a `.env` file with the required values:

```bash
pip install -r requirements.txt
cat <<EOF > .env
BOT_TOKEN=your_bot_token
API_ID=123456
API_HASH=0123456789abcdef0123456789abcdef
MONGO_URI=mongodb://localhost:27017/guard
# Optional when the URI does not contain a DB name; defaults to "guard"
MONGO_DB_NAME=guard
LOG_CHANNEL_ID=-1001234567890
EOF
```

## Running

Start the bot with:

```bash
python main.py
```

## Usage

The bot offers a few moderation tools:

- `/approve` and `/unapprove` – manage approved users in a group.
- `/viewapproved` – list approved users.
- `/setautodelete <seconds>` – automatically delete messages from non‑admins.
- `/panel` – open an inline control panel with quick toggles.

Only group admins can use these commands.


If you encounter a `ConfigurationError` complaining about the default database,
ensure that the `MONGO_URI` includes a database name or set the `MONGO_DB_NAME`
environment variable. When neither is provided, the bot falls back to a
database named `guard`.
