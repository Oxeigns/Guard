# Oxygen Guard Bot

Oxygen Guard is a Telegram moderation bot built with [Pyrogram](https://docs.pyrogram.org/). It provides a minimal but useful set of moderation utilities with inline controls and stores its state in MongoDB.

## ⚙️ Features
- **BioFilter** – block users whose bio contains links.
- **LinkFilter** – remove messages containing URLs from non‑admins.
- **EditMode** – auto delete edited messages to prevent stealth spam.
- **AutoDelete** – automatically delete messages after a configurable delay.
- **Approval Mode** – restrict messaging to approved users only.
- Full admin commands: `/ban`, `/kick`, `/mute`, `/approve`, `/unapprove`, `/viewapproved`, `/setautodelete`.
- Inline control panel accessible via `/start`, `/menu`, `/help` or `/settings`.

## 🧰 Requirements
- Python 3.10+
- A MongoDB instance
- Telegram API credentials (`API_ID`, `API_HASH`, `BOT_TOKEN`)

## 🖥️ VPS Deployment
1. **Clone the repo and install deps**
   ```bash
   git clone https://github.com/youruser/oxygen-guard.git
   cd oxygen-guard
   pip install -r requirements.txt
   ```
2. **Configuration** – copy `.env.example` to `.env` and fill the variables:
   - `API_ID`, `API_HASH`, `BOT_TOKEN`
   - `MONGO_URI` and `MONGO_DB`
   - optional: `OWNER_ID`, `SUPPORT_CHAT_URL`, `DEVELOPER_URL`
3. **Run the bot**
   ```bash
   python3 main.py
   ```
   Use `screen` or `tmux` to keep it running, or create a `systemd` service:
   ```ini
   [Unit]
   Description=Oxygen Guard Bot
   After=network.target

   [Service]
   WorkingDirectory=/path/to/oxygen-guard
   ExecStart=/usr/bin/python3 main.py
   Restart=always
   Environment="PYTHONUNBUFFERED=1"

   [Install]
   WantedBy=multi-user.target
   ```
   Enable with `sudo systemctl enable --now oxygen-guard.service`.
4. Ensure your firewall allows outbound connections and Telegram ports (usually none need to be opened when running in polling mode).

Optional: run `python3 -m py_compile $(git ls-files '*.py')` to verify the code.

## 📌 Bot Overview
Use `/start` in private chat to see the welcome panel with:
- **📘 Commands** – view admin commands and access module help.
- **⚙️ Settings** – open the group control panel if used in a group.

Use the provided commands to enable or disable features. Support and developer buttons open the URLs you set in `.env`.

## 🚀 Deploying on Render

1. Fork this repo and create a new **Background Worker** on [Render](https://render.com). You can use the provided `render.yaml` for one-click setup.
2. Set the environment variables from `.env.example` in the Render dashboard.
3. The worker command should run `sh start.sh` (same as the provided `Procfile`).
4. Optionally deploy the included `web.py` as a separate web service for simple health checks.

`render.yaml` already defines two services:

```yaml
services:
  - type: worker
    name: guard-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
  - type: web
    name: guard-web
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python web.py
```

Deploy the worker and, if desired, the web service. No ports need to be exposed for the worker since it runs the Telegram bot in polling mode.
