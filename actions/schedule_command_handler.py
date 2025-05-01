"""
- This module is responsible for scheduling messages
"""
from datetime import datetime, timedelta

from pyrogram.types import Message

from database import DbManager
from job_manager import JobManager
from .utils import Utility


def find_closest_next(numbers, target):
    """
    Find the closest next number from a list of numbers.

    Parameters:
    numbers (list): A list of numbers.
    target (int): The target number.

    Returns:
    int: The closest next number from the list.
    """
    closest_next = None
    min_difference = float('inf')

    for num in numbers:
        if num > target:
            difference = num - target
            if difference < min_difference:
                min_difference = difference
                closest_next = num

    return closest_next


async def handle_schedule_command(update: Message) -> None:
    """
    Handles the schedule command
    :param update:
    :return:
    """
    text = None
    command_guide = ("# Schedule Command Guide:\n"
                     "/schedule -> to view all the scheduled messages\n"
                     "/schedule add -> Reply this to the message that you want to schedule.\n"
                     "/schedule bulk_add start -> To start adding bulk messages\n"
                     "/schedule bulk_add stop -> To stop adding bulk messages.\n"
                     "/schedule `schedule_id` -> to view the original message related to the `schedule_id`.\n"
                     "/schedule remove `schedule_id` -> To remove the schedule with id `schedule_id`. You can get the "
                     "id of the schedule, by sending /schedule.")
    tg_chat = update.chat
    admin_chat_id = DbManager.get_admin_id()
    if admin_chat_id is not None:
        if tg_chat.id == admin_chat_id:
            targets = DbManager.get_target_chats()
            # if there are no target chats
            if not targets:
                text = "No target channels added. Please add some target channel before scheduling a message."

            # if there are target chats
            else:
                command = update.command
                command_length = len(command)
                if command_length == 1:
                    msgs = DbManager.get_scheduled_messages()
                    if not msgs:
                        text = f"No messages has been scheduled.\n\n{command_guide}"

                    else:
                        text = f"Total scheduled messages: {len(msgs)}\n"
                        current_time = datetime.now(tz=JobManager.timezone)
                        next_hour = find_closest_next(
                            numbers=JobManager.selected_times,
                            target=current_time.hour,
                        )
                        next_datetime = current_time.replace(hour=next_hour, minute=0, second=0)
                        if current_time > next_datetime:
                            next_datetime += timedelta(days=1)

                        time_string = "%I : %M %p %d-%m-%Y Cairo"
                        for i, _ in enumerate(msgs, start=1):
                            text += f"{i}. MSG [{next_datetime.strftime(time_string)}]\n"
                            next_datetime += timedelta(hours=2)

                            if len(text) >= 3000:
                                await update.reply_text(
                                    text=text,
                                )
                                text = ""

                        if text:
                            await update.reply_text(
                                text=text,
                            )

                        text = command_guide

                elif command_length == 2:
                    param = command[1].lower()
                    # if the user wants to schedule a message
                    if param == "add":
                        replied_message = update.reply_to_message
                        if replied_message is None:
                            text = ("To schedule a message, send this command in reply to the message that you want to "
                                    "schedule.")

                        else:
                            if replied_message.text or replied_message.media:
                                added = DbManager.add_scheduled_message(
                                    msg_id=replied_message.id,
                                    media_group_id=replied_message.media_group_id,
                                    forced=True,
                                )
                                update = replied_message
                                if added:
                                    text = "Okay, this message has been added to the schedule list."

                                else:
                                    text = "This message is already scheduled."

                            else:
                                text = ("Service messages can not be sent. Please send this command in reply to a "
                                        "normal message.")

                    # trying to show the original message that has been scheduled.
                    else:
                        try:
                            schedule_index = int(param)

                        except (ValueError, TypeError):
                            text = ("Invalid schedule id provided with the command. Please provide a valid schedule id "
                                    "to check the original message that has been scheduled.")

                        else:
                            msgs = DbManager.get_scheduled_messages()
                            try:
                                msg = msgs[schedule_index-1]

                            except IndexError:
                                text = ("Oops! Could not find any message with this id. Please get the schedule id by "
                                        "sending /schedule.")

                            else:
                                text = f"This is the original message with schedule id: `{schedule_index}`"
                                # todo: check what happens if the source message is deleted
                                await update.reply_text(
                                    text=text,
                                    reply_to_message_id=msg.id,
                                )
                                text = None

                elif command_length == 3:
                    param = command[1].lower()
                    # if the user wants to manage bulk addition
                    if param == "bulk_add":
                        sub_param = command[-1].lower()
                        if sub_param == "start":
                            text = ("Okay, bulk message scheduling on. It will auto schedule all the message sent here."
                                    "\nTo stop bulk message scheduling, send /schedule bulk_add stop")
                            Utility.start_bulk_addition()

                        elif sub_param == "stop":
                            text = ("Okay, bulk message scheduling is off. "
                                    "\nTo start bulk message scheduling, send /schedule bulk_add start")
                            Utility.stop_bulk_addition()

                        else:
                            text = command_guide

                    # if the user wants to remove a message from schedule list
                    elif param == "remove":
                        try:
                            schedule_index = int(command[-1])

                        except (ValueError, TypeError):
                            text = ("Invalid schedule id provided with the command. Please send a valid schedule id to "
                                    "remove it from the schedule list.")

                        else:
                            removed_msg = DbManager.remove_scheduled_message(schedule_index)
                            if removed_msg is None:
                                text = f"Oops! Could not find any message with the schedule id: {schedule_index}"

                            else:
                                text = "Okay, this message has been removed from the schedule list."
                                # todo: check what happens if the original message is deleted.
                                await update.reply_text(
                                    text=text,
                                    reply_to_message_id=removed_msg.id,
                                )
                                text = None

                    else:
                        text = f"Invalid command.\n\n{command_guide}"

                else:
                    text = command_guide

    if text:
        await update.reply_text(
            text=text,
        )
