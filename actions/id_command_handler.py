"""
- This module is responsible for handling the id command
"""
from pyrogram.types import Message


async def handle_id_command(update: Message) -> None:
    """
    Handles the id command
    :param update:
    :return:
    """
    text = f"Chat ID: {update.chat.id}"
    if text:
        await update.reply_text(
            text=text,
        )
