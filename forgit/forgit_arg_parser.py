import argparse
from importlib.metadata import version
from .types import MenuArgs, Interval
from .utils import to_color


def forgit_argument_parser(directory: str, check_git_interval: Interval, commit_message: str) -> MenuArgs:
    forgit_version: str = version('forgit')
    default_commit_message = commit_message
    default_directory: str = directory
    default_check_commit_interval: str = f'{check_git_interval["quantity"]}{check_git_interval["unit"].value}'
    quantity_str: str = to_color('quantity', 'green')
    unit_str: str = to_color('unit', 'magenta')

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog='forgit',
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=50)
    )

    parser.add_argument('-v', '--version', action='version', version=f'Forgit version {forgit_version}')
    parser.add_argument('-p', '--persist',
                        help='By default Forgit clears the terminal on each status refresh.\n'
                             'Set -p to disable this feature.\n ',
                        action='store_true')

    parser.add_argument('-d', '--directory',
                        help='Git directory to manage.\n'
                             f'Default: {to_color(default_directory)}\n ',
                        default=default_directory,
                        metavar='path')

    parser.add_argument('-i', '--interval',
                        help='Interval to check the given git repository for a possible auto-commit.\n'
                             f'Format: [{quantity_str}: integer]'
                             f'[{unit_str}: m(minutes), h(hours)]\n'
                             'Interval must be >= 5 minutes.\n'
                             'Example: 3h - check git repository for changes and auto-commit every 3 hours\n'
                             f'Default reconnect interval: {to_color(default_check_commit_interval)}\n ',
                        default=default_check_commit_interval,
                        metavar='time')

    parser.add_argument('-m', '--message',
                        help='Git commit message.\n'
                             f'Default: {to_color(default_commit_message)}\n ',
                        default=default_commit_message,
                        metavar='message')

    args: argparse.Namespace = parser.parse_args()

    return {
        'persist': args.persist,
        'directory': args.directory,
        'interval': args.interval,
        'message': args.message,
        'help': parser.print_help
    }
