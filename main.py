"""
- Main entry point of the program
"""
import asyncio
import logging
from typing import List

from dotenv import load_dotenv

from bot import BotManager
from config import ConfigRepo
from core import Constant
from job_manager import JobManager


def _setup_logging(
    modules: List[str],
    log_handler: logging.Handler,
    log_level=logging.INFO
) -> None:
    """
    Sets up the logger for the modules
    :param modules:
    :param log_handler:
    :param log_level:
    :return:
    """
    log_handler.setLevel(log_level)
    for module in modules:
        logger = logging.getLogger(module)
        logger.setLevel(log_level)
        logger.addHandler(log_handler)


async def main():
    """
    Main function
    :return:
    """
    load_dotenv()
    # setting up the logging
    module_names = [
        "actions",
        "bot",
        "config",
        "database",
        "handlers",
    ]
    # log_handler = logging.StreamHandler()
    log_handler = logging.FileHandler(f"{Constant.data_dir}/bot-logs.log")
    formatter = logging.Formatter(fmt="[%(levelname) 7s/%(asctime)s] %(name)s: %(message)s",
                                  datefmt='%m/%d/%Y %I:%M:%S %p')
    log_handler.setFormatter(formatter)
    _setup_logging(modules=module_names, log_handler=log_handler, log_level=logging.INFO)

    # get the configurations
    config = ConfigRepo.get_config()
    session_name = "main-bot"
    await BotManager.start_bot(
        api_id=config.api_id,
        api_hash=config.api_hash,
        bot_token=config.bot_token,
        session_name=session_name,
        work_dir=Constant.data_dir,
    )
    JobManager.start_job()
    await BotManager.keep_running()
    await BotManager.stop_bot()


if __name__ == "__main__":
    asyncio.run(main())
