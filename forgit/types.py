from enum import Enum
from typing import TypedDict, Callable


class Unit(Enum):
    SECOND = 's'
    MINUTE = 'm'
    HOUR = 'h'


class MenuArgs(TypedDict):
    persist: bool
    directory: str
    interval: str
    message: str
    help: Callable


class Interval(TypedDict):
    quantity: int
    unit: Unit


class BaseValues(TypedDict):
    directory: str
    check_git_interval: Interval
    commit_message: str


class GitManagerStatus(TypedDict):
    success: bool
    status: str
    debug: list[str]
