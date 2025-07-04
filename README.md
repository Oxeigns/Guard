# Guard

Guard is a modular Telegram bot built with Pyrogram. It stores data in a local SQLite database and automatically initialises the tables on startup. The bot reads its configuration from the environment (or a `.env` file) and runs in polling mode which makes it suitable for platforms such as Render or Railway without any open ports.

## Required environment variables

- `BOT_TOKEN` – Telegram bot token for your bot.
- `API_ID` – integer API ID from https://my.telegram.org.
- `API_HASH` – API hash from https://my.telegram.org.
- `DB_PATH` – *(optional)* path to the SQLite database file. Defaults to `guard.db`.
- `BANNER_URL` – *(optional)* image URL displayed on the settings panel.
- `LOG_LEVEL` – *(optional)* logging level, e.g. `INFO` or `DEBUG`.

## Setup

Install dependencies and create a `.env` file with the required values. An
example is provided in `.env.example`:

```bash
pip install -r requirements.txt
cat <<EOF > .env
BOT_TOKEN=your_bot_token
API_ID=123456
API_HASH=0123456789abcdef0123456789abcdef
# Path to the SQLite database file
DB_PATH=guard.db
# Optional image to display on the settings panel
BANNER_URL=
LOG_LEVEL=INFO
EOF
```

## Running

Start the bot locally with:

```bash
python main.py
```

For hosting platforms such as Heroku or Railway, this repository includes a
`Procfile`, `runtime.txt`, and `start.sh` so the bot can be launched directly
after deployment.

### Render.com

This repository also provides a `render.yaml` describing two services:

- **`guard-web`** – a small Flask app exposing `/health` on port `10000`.
- **`guard-bot`** – the background worker running the Pyrogram bot in polling
  mode.

Deploy the repo on Render using this file so the worker and web service share
the same environment variables.

## Docker

A `Dockerfile` is included for containerized deployments. Build the image and
run the bot with:

```bash
docker build -t guard .
docker run --env-file .env guard
```

## Usage

The bot offers a set of moderation tools:

- `/start` or `/menu` – open the inline control panel.
- `/help` – display available commands.
- `/ping` – simple health check.
- `/approve` and `/unapprove` – manage approved users.
- `/autodelete <seconds>` – automatically delete messages from non‑admins (use `/autodelete` alone to view the current delay). `/setautodelete` remains as an alias.
- `/biolink [on|off]` – toggle the bio link filter.
- `/viewapproved` – list approved users.

Only group admins can use these commands in group chats.

Most commands present inline buttons for quick access to approval actions and
setting toggles.


The bot stores all data in a local SQLite database by default. Set the
`DB_PATH` environment variable to choose a different location.
