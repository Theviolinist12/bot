"""
- This module is responsible for handling all the messages
"""
from pyrogram.types import Message

from database import DbManager
from .utils import Utility


async def handle_all_messages(update: Message) -> None:
    """
    Handles all the messages
    :param update:
    :return:
    """
    text = None
    tg_chat = update.chat
    admin_chat_id = DbManager.get_admin_id()
    if admin_chat_id is not None:
        if tg_chat.id == admin_chat_id:
            if Utility.need_to_add_bulk():
                if update.text or update.media:
                    added = DbManager.add_scheduled_message(msg_id=update.id, media_group_id=update.media_group_id)
                    if added:
                        text = ("Bulk addition on. This message has been scheduled. \n"
                                "To turn off bulk addition, send /schedule bulk_add stop")

    if text:
        await update.reply_text(
            text=text,
        )
