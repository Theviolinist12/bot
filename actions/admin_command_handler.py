"""
- This module is responsible for handling the /admin command
"""
from pyrogram.types import Message

from database import DbManager


async def handle_admin_command(update: Message) -> None:
    """
    Handles the admin command
    :param update:
    :return:
    """
    text = None
    tg_chat = update.chat
    admin_chat_id = DbManager.get_admin_id()
    if admin_chat_id is None:
        DbManager.update_admin_id(admin_id=tg_chat.id)
        text = "Okay, this chat has been marked as the admin chat."

    else:
        if tg_chat.id == admin_chat_id:
            text = "Don't worry, this chat is already marked as the admin chat."

    if text:
        await update.reply_text(
            text=text,
        )
