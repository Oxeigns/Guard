# Telegram Guard Bot

A simple Pyrogram bot using MongoDB for persistence.

## Setup

1. Install Python 3.12 and Docker (optional).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.sample` to `.env` and fill in your credentials.
4. Run the bot:
   ```bash
   python main.py
   ```

The provided `Dockerfile` can be used to build a container image for deployment.
