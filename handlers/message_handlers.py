"""
- This module is responsible for handling the messages received by the bot
"""
from pyrogram import Client, filters
from pyrogram.types import Message

from actions import (
    handle_admin_command,
    handle_all_messages,
    handle_id_command,
    handle_manual_command,
    handle_schedule_command,
    handle_start_command,
    handle_target_command,
)


@Client.on_message(filters.command("admin"))
async def admin_command_handler(_: Client, update: Message) -> None:
    """
    Responsible for handling the /admin command
    """
    await handle_admin_command(update=update)


@Client.on_message(filters.command(["schedule", "s"]))
async def schedule_command_handler(_: Client, update: Message) -> None:
    """
    Responsible for handling the /schedule command
    """
    await handle_schedule_command(update=update)


@Client.on_message(filters.command("start"))
async def start_command_handler(_: Client, update: Message) -> None:
    """
    Responsible for handling the /start command
    """
    await handle_start_command(update=update)


@Client.on_message(filters.command("id"))
async def id_command_handler(_: Client, update: Message) -> None:
    """
    Responsible for handling the /id command
    """
    await handle_id_command(update=update)


@Client.on_message(filters.command(["target", "t"]))
async def target_command_handler(_: Client, update: Message) -> None:
    """
    Responsible for handling the /target command
    """
    await handle_target_command(update=update)


@Client.on_message(filters.command("manual"))
async def manual_command_handler(_: Client, update: Message) -> None:
    """
    Responsible for handling the /manual command
    """
    await handle_manual_command(update=update)


@Client.on_message()
async def all_message_handler(_: Client, update: Message) -> None:
    """
    Responsible for handling all the messages received by the bot
    """
    await handle_all_messages(update=update)
