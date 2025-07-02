# Oxeign Telegram Guard

Oxeign Telegram Guard is a modular security bot built with **Pyrogram**. It keeps groups clean using a mix of admin tools, approval flows and message filters powered by the Detoxify model. All persistent data is stored in MongoDB.

## Features

- MongoDB backed storage
- Owner and sudo system
- Long message control: `/setlongmode`, `/setlonglimit`
- Bio link filtering: `/biolink on|off`
- Approval system: `/approve` and `/disapprove`
- Moderation tools: `/mute`, `/unmute`, `/ban`, `/unban`, `/kick`, `/warn`
- Sudo management: `/addsudo`, `/removesudo`
- Broadcast messages: `/broadcast <text>`
- View chat configuration: `/getconfig`

## Setup

1. Install Python 3.10+ and clone the repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your API keys and database URI.
4. Run the bot:
   ```bash
   python -m oxeign.main
   ```

## Credits

Developed by [@Oxeign](https://t.me/Oxeign) with help from [@MajorGameApp](https://t.me/MajorGameApp).
