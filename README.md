# Oxeign Telegram Guard

Oxeign Telegram Guard is a modular security bot built with **Pyrogram**. It keeps groups clean using a mix of admin tools, approval flows and optional toxicity filters powered by the Detoxify model (if installed). All persistent data is stored in MongoDB.

## Features

- MongoDB backed storage
- Owner and sudo system
- Long message control: `/setlongmode`, `/setlonglimit`
- Bio link filtering: `/biolink on|off`
- Approval system: `/approve` and `/disapprove`
- Moderation tools: `/mute`, `/unmute`, `/ban`, `/unban`, `/kick`, `/warn`, `/removewarn`
- Sudo management: `/addsudo`, `/rmsudo`
- Broadcast messages with preview: `/broadcast <text>`
- Auto delete timer: `/setautodelete <seconds>`
- Blacklist management: `/blacklist add|remove|list`
- Custom welcome messages: `/setwelcome <text>`
- Custom goodbye messages: `/setgoodbye <text>`
- View chat configuration: `/getconfig`
- Bulk purge messages: `/purge` (reply to a message)
- View and manage settings: `/settings`
- Tag everyone: `/tagall`
- Toggle Anti-Spam, Flood, Captcha and more via buttons

## Setup

1. Install Python 3.10+ and clone the repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your API keys and database URI. If
   your MongoDB URI does not contain a database name, set `MONGO_DB_NAME` as
   well.
4. Run the bot:
   ```bash
   python -m oxeign.main
   ```

### Optional toxicity filtering

To enable Detoxify based toxicity filtering, install the extra packages:
```bash
pip install detoxify torch
```

## Credits

Developed by [@Oxeign](https://t.me/Oxeign). Need help? Visit [@Botsyard](https://t.me/Botsyard).
