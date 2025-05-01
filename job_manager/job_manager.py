"""
- This module is responsible for handling the task of uploading channel data to google sheet
"""
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pyrogram.errors import ChannelPrivate, PeerIdInvalid

from bot import BotManager
from database import DbManager


class JobManager:
    """
    Responsible for managing the jobs
    """
    _initialized = False
    _scheduler = AsyncIOScheduler()
    selected_times = [
        1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23,
    ]
    timezone = pytz.timezone("Africa/Cairo")

    @classmethod
    async def the_job(cls) -> None:
        """
        The job of sending the scheduled messages
        :return:
        """
        client = BotManager.get_bot()
        msgs = DbManager.get_scheduled_messages()
        if msgs:
            msg = DbManager.remove_scheduled_message(1)
            admin_id = DbManager.get_admin_id()
            targets = DbManager.get_target_chats()
            status_text = ""
            for target in targets:
                m = await client.get_messages(
                    chat_id=admin_id,
                    message_ids=msg.id,
                )
                if m.empty:
                    text = (f"Could not send the scheduled message. With id: `{msg.id}`\n"
                            f"Sending the next message.")
                    await client.send_message(
                        chat_id=admin_id,
                        text=text,
                    )
                    return await cls.the_job()

                else:
                    try:
                        if m.media_group_id:
                            await client.copy_media_group(
                                chat_id=target.id,
                                from_chat_id=admin_id,
                                message_id=m.id,
                            )

                        else:
                            await client.copy_message(
                                chat_id=target.id,
                                from_chat_id=admin_id,
                                message_id=m.id,
                            )

                    except (ChannelPrivate, PeerIdInvalid):
                        status_text += (f"Could not send to: {target.title} [{target.id}]. Check if the bot is an "
                                        f"admin of the chat.\n")

                    else:
                        status_text += f"Sent to: {target.title} [{target.id}]\n"

            if status_text:
                await client.send_message(
                    chat_id=admin_id,
                    text=status_text,
                    reply_to_message_id=msg.id,
                )

    @classmethod
    def start_job(cls) -> None:
        """
        Starts the job
        :return:
        """
        if not cls._initialized:
            # print(cls.timezone)
            for selected_time in cls.selected_times:
                trigger = CronTrigger(
                    hour=selected_time,
                    timezone=cls.timezone,
                )
                cls._scheduler.add_job(
                    func=cls.the_job,
                    trigger=trigger,
                )

            cls._scheduler.start()
            cls._initialized = True
