# Master Guardian Bot

Master Guardian Bot is a powerful, modular, and production-ready Telegram security bot built using Python and Pyrogram. It is designed to manage and moderate groups and channels with precision.

Key features include:

- MongoDB-backed persistent storage.
- Group/channel administration with an owner-sudo system.
- Advanced long message handling with Telegraph (`/echo`, `/setlongmode`, `/setlonglimit`).
- Bio-based message control (`/biolink on|off`).
- User approval system (`/approve`, `/disapprove`).
- Admin tools for mute, ban, unban, kick, warn, and broadcast.
- Async-safe broadcasting, permission checks, and auto-cleanup for muted or blacklisted users.

The bot is fully configurable using a `.env` file. A sample environment file is provided at `sample.env`.

## Deployment

Follow these steps to deploy the bot on a Linux VPS with Python 3.10+:

```bash
# 1. Update system packages
sudo apt update && sudo apt upgrade -y

# 2. Install Python 3.10+ and pip
sudo apt install python3 python3-pip -y

# 3. Clone the repository
git clone https://github.com/yourusername/master-guardian-bot.git
cd master-guardian-bot

# 4. Install requirements
pip3 install -r requirements.txt

# 5. Copy and edit the environment file
cp sample.env .env
nano .env  # Enter your API_ID, API_HASH, BOT_TOKEN, MONGO_URI, OWNER_ID, etc.

# 6. Run the bot
python3 main.py
```

Ensure you set the required environment variables for API credentials, MongoDB URI, and bot ownership.
