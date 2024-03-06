
from enum import Enum

from colors import Colors


class Error(Enum):
    """docstring for  Error"""

    OK = 0
    FAIL = 1
    ERROR = 2

    @staticmethod
    def add_message(st):
        pass
