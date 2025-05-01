"""
- This module is responsible for providing some utility
"""


class Utility:
    """
    Provides utility methods
    """
    _add_bulk = False

    @classmethod
    def start_bulk_addition(cls) -> None:
        """
        Starts adding bulk messages
        :return:
        """
        cls._add_bulk = True

    @classmethod
    def stop_bulk_addition(cls) -> None:
        """
        Stops adding bulk messages
        :return:
        """
        cls._add_bulk = False

    @classmethod
    def need_to_add_bulk(cls) -> bool:
        """
        Whether we need to add bulk schedule messages
        :return:
        """
        return cls._add_bulk
