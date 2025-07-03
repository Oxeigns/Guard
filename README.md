# Guard

Guard is a simple moderation bot built with Pyrogram. It stores data in MongoDB and requires a few environment variables before running.

## Required environment variables

- `BOT_TOKEN` – Telegram bot token for your bot.
- `MONGO_URI` – MongoDB connection string. If the URI does not include a database name, also set `MONGO_DB_NAME`.
- `MONGO_DB_NAME` – *(optional)* name of the MongoDB database when it is not part of `MONGO_URI`.
- `LOG_CHANNEL_ID` – Telegram channel ID where the bot sends log messages.

These variables can be placed in a `.env` file in the project root. They will be
loaded automatically by `python-dotenv` when the bot starts.

```
BOT_TOKEN=your_bot_token
MONGO_URI=mongodb://user:pass@host:27017/guard
# if your URI does not include the database name, set it separately
MONGO_DB_NAME=guard
LOG_CHANNEL_ID=-1001234567890
```

## Installation

Install dependencies using `pip`:

```bash
pip install -r requirements.txt
```

## Running

After setting the environment variables, start the bot with:

```bash
python main.py
```


If you encounter a `ConfigurationError` complaining about the default database,
make sure the MongoDB URI contains a database name or set `MONGO_DB_NAME`
explicitly.
