"""
- This module is responsible for handling the database related tasks
"""
import json
import logging
from functools import wraps
from typing import Union, List

from pydantic import BaseModel, Field

from core import Constant


log = logging.getLogger(__name__)


def initialize_db(func):
    """
    Checks whether the db is initialized or not and initializes
    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(cls: "DbManager", *args, **kwargs):
        if not cls._initialized:
            cls.initialize()

        return func(cls, *args, **kwargs)

    return wrapper


class Target(BaseModel):
    """
    Models the target chats
    """
    id: int
    title: str


class Msg(BaseModel):
    """
    Represents the scheduled message
    """
    id: int
    media_group_id: Union[int, None] = Field(default=None)


class DBModel(BaseModel):
    """
    Models the database
    """
    # stores the id of the admin chat
    admin_id: Union[int, None] = Field(default=None)
    # stores the details of the target chats
    targets: List[Target] = Field(default_factory=list)
    # stores the details of the scheduled messages
    msgs: List[Msg] = Field(default_factory=list)


class DbManager:
    """
    Provides the methods to work with database
    """
    _data: DBModel = DBModel()
    _initialized = False

    @classmethod
    def initialize(cls) -> None:
        """
        Initializes the database
        :return:
        """
        log.info("initializing database")
        json_data = dict()
        if Constant.db_path.exists() and Constant.db_path.is_file():
            log.debug("database file path exists")
            with open(Constant.db_path, "r", encoding="utf-8") as f:
                try:
                    json_data = json.load(f)

                except json.JSONDecodeError:
                    log.debug("JSONDecodeError occurred while reading the data from the database file")

        cls._data = DBModel.model_validate(obj=json_data)
        cls._initialized = True
        log.info(f"store the database's data to: {json_data!r}")

    @classmethod
    def _write_data(cls) -> None:
        """
        Writes the data in the database file
        :return:
        """
        log.info("writing data in the database file")
        with open(Constant.db_path, "w", encoding="utf-8") as f:
            json.dump(cls._data.dict(), f)

    @classmethod
    @initialize_db
    def get_admin_id(cls) -> Union[int, None]:
        """
        Returns the admin id from the database
        :return:
        """
        log.info("getting admin id")
        return cls._data.admin_id

    @classmethod
    @initialize_db
    def get_target_chats(cls) -> List[Target]:
        """
        Returns the list of the target chats
        :return:
        """
        log.info("getting target chats")
        return cls._data.targets

    @classmethod
    @initialize_db
    def get_scheduled_messages(cls) -> List[Msg]:
        """
        Returns the list of messages which are scheduled
        :return:
        """
        log.info("getting scheduled messages")
        return cls._data.msgs

    @classmethod
    @initialize_db
    def update_admin_id(cls, admin_id: int) -> None:
        """
        Updates the admin id
        :param admin_id:
        :return:
        """
        log.info("changing the admin id from: %s to: %s", cls._data.admin_id, admin_id)
        cls._data.admin_id = admin_id
        cls._write_data()

    @classmethod
    @initialize_db
    def add_target(cls, chat_id: int, title: str) -> None:
        """
        Adds target to the database, raises ValueError if the target already exists
        :param chat_id:
        :param title:
        :return:
        """
        log.info("adding target, id: %s, title: %s", chat_id, title)
        new_target = Target(id=chat_id, title=title)
        for target in cls._data.targets:
            if target.id == new_target.id:
                log.debug("target already exists")
                raise ValueError("Target already exists")

        cls._data.targets.append(new_target)
        cls._write_data()

    @classmethod
    @initialize_db
    def remove_target(cls, chat_id: int) -> Union[Target, None]:
        """
        Removes the target from the database
        :param chat_id:
        :return:
        """
        log.info("removing target, id: %s", chat_id)
        removed: Union[Target, None] = None
        for i, target in enumerate(cls._data.targets):
            if target.id == chat_id:
                removed = cls._data.targets.pop(i)
                break

        if removed is not None:
            cls._write_data()

        return removed

    @classmethod
    @initialize_db
    def add_scheduled_message(cls, msg_id: int, media_group_id: Union[int, None] = None, forced: bool = False) -> bool:
        """
        Adds new message to the list of scheduled messages
        :param msg_id:
        :param media_group_id:
        :param forced: -> Whether the user is forcing to add
        :return: bool -> whether the message has been added or not
        """
        log.info("adding scheduled message, id: %s", msg_id)
        msg = Msg(
            id=msg_id,
            media_group_id=media_group_id,
        )
        add = True
        # ignoring the updates with same media group to be entered twice
        if not forced:
            if media_group_id is not None:
                scheduled_msgs = cls._data.msgs
                for scheduled_msg in scheduled_msgs:
                    if scheduled_msg.media_group_id is not None:
                        if scheduled_msg.media_group_id == media_group_id:
                            add = False
                            break

        if add:
            cls._data.msgs.append(msg)
            cls._write_data()

        return add

    @classmethod
    @initialize_db
    def remove_scheduled_message(cls, index: int) -> Union[Msg, None]:
        """
        Removes the scheduled message, and returns its id
        :param index:
        :return:
        """
        removed_msg = None
        log.info("removing scheduled message with index: %s", index)
        try:
            removed_msg = cls._data.msgs.pop(index-1)

        except IndexError:
            pass

        cls._write_data()
        return removed_msg
