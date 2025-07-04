from pyrogram import Client

from . import start, help, admin


def init_all(app: Client) -> None:
    start.init_start(app)
    help.init_help(app)
    admin.init_admin(app)
