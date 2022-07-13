from termcolor import cprint
from .forgit import Forgit
from .logging import configure_logging
from .forgit_arg_parser import forgit_argument_parser
from .types import MenuArgs, BaseValues, Unit


def run_forgit():
    configure_logging()
    defaults: BaseValues = {
        'directory': './',
        'check_git_interval': {'quantity': 1, 'unit': Unit.HOUR},
        'commit_message': 'auto-commit'
    }

    menu_args: MenuArgs = forgit_argument_parser(
        defaults['directory'],
        defaults['check_git_interval'],
        defaults['commit_message']
    )

    try:
        forgit = Forgit(
            menu_args['directory'],
            menu_args['interval'],
            menu_args['message'],
            menu_args['persist']
        )
        forgit.run()
    except Exception as e:
        cprint(f'{e}', 'red', attrs=['bold'])
        menu_args['help']()
