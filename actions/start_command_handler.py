"""
- This module is responsible for handling the start command
"""
from pyrogram.types import Message

from database import DbManager


async def handle_start_command(update: Message) -> None:
    """
    Handles the start command
    :param update:
    :return:
    """
    text = None
    tg_chat = update.chat
    admin_chat_id = DbManager.get_admin_id()
    if admin_chat_id is not None:
        if tg_chat.id == admin_chat_id:
            targets = DbManager.get_target_chats()
            msgs = DbManager.get_scheduled_messages()
            text = (f"Total targets connected: {len(targets)}\n"
                    f"Total scheduled messages: {len(msgs)}\n\n"
                    f"# Commands:\n"
                    f"/target or /t -> to view, add, remove targets\n"
                    f"/schedule or /s -> to view, add, remove schedule messages\n"
                    f"/id -> to view id of a chat.")

    if text:
        await update.reply_text(
            text=text,
        )
