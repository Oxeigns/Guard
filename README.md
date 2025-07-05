# Sirion Guard Bot

Sirion is a Telegram moderation bot built with [Pyrogram](https://docs.pyrogram.org/).
It offers a compact set of tools to keep groups clean while remaining easy to configure via inline buttons.

## Features
- **BioMode** – delete messages from users whose profile bio contains a link.
- **LinkFilter** – remove messages containing URLs from non‑admins.
- **EditMode** – delete edited messages from regular users.
- **AutoDelete** – automatically purge messages after a configurable delay.
- **Approval Mode** – allow only approved users to talk when enabled.
- **Broadcast** – send announcements to all saved users or groups.
- Full admin commands: `/ban`, `/kick`, `/mute`, `/approve`, `/unapprove`, `/approved`, `/warn`, `/resetwarn`, `/biolink`, `/linkfilter`, `/editfilter`, `/setautodelete`.
- Inline control panel available through `/start`, `/help` or `/menu`.

## Requirements
- Python 3.10+
- A running MongoDB instance
- Telegram API credentials

## Setup
1. Clone the repository and install dependencies
   ```bash
   git clone https://github.com/youruser/guard-bot.git
   cd guard-bot
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in the variables:
   - `API_ID`, `API_HASH`, `BOT_TOKEN`
   - `MONGO_URI` and `MONGO_DB`
   - optional: `OWNER_ID`, `SUPPORT_CHAT_URL`, `DEVELOPER_URL`, `LOG_GROUP_ID`
3. Run the bot
   ```bash
   python3 main.py
   ```
   Keep it running using `screen`, `tmux` or a `systemd` service.

## Render Deployment
Create a new **Background Worker** on [Render](https://render.com) and use `render.yaml` for automatic configuration.
Set the environment variables from your `.env` file in the Render dashboard. The worker command runs `sh start.sh`.
Optionally deploy `web.py` as a small web service for health checks.

When running on your own VPS simply execute `sh start.sh` in a screen or
systemd service. On Render the worker type automatically keeps the bot
running in the background.

## Manual Broadcast
Only the owner can use `/broadcast users <text>` or `/broadcast groups <text>` to send a message to all saved users or groups.
The Broadcast button in the control panel shows these instructions as well.

## Notes
The bot works entirely in polling mode and logs important events such as new users and group joins/leaves to the log group if provided.
