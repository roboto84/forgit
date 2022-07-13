import os
from termcolor import colored, cprint


def to_color(string: str, color: str = 'cyan'):
    return colored(string, color, attrs=['bold'])


def color_print(string: str, color: str = 'cyan'):
    cprint(string, color, attrs=['bold'])


def is_directory(path: str):
    return os.path.isdir(path)
