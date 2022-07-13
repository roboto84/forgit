import os
import time
import schedule
from typing import Callable
from datetime import datetime
from .git_manager import GitManager
from .logging import logger
from .types import Unit, Interval, GitManagerStatus
from .utils import color_print, to_color


class Forgit:
    def __init__(self, git_directory: str, git_check_time_interval: str, commit_message: str, persist: bool):
        self._tested_git_version: str = '2.35.1'
        self._persist: bool = persist
        self._git_directory: str = GitManager.get_full_git_repo_path(git_directory)
        self._commit_message: str = commit_message
        self._git_commit_check_interval: Interval = self._set_git_commit_check_interval(git_check_time_interval)
        self._git_manager: GitManager = GitManager(self._git_directory, commit_message)
        self._schedule: schedule = schedule

    @staticmethod
    def _set_git_commit_check_interval(time_interval: str) -> Interval:
        try:
            quantity: int = int(time_interval[:-1])
            unit: Unit = Unit(time_interval[-1])
        except ValueError:
            raise Exception('Time interval is invalid. Check out -h for help.')
        else:
            if unit is Unit.SECOND or unit is Unit.MINUTE and quantity < 5:
                raise Exception('Time interval is too low. Check out -h for help.')
            return {'quantity': quantity, 'unit': unit}

    def _setup_schedule(self, interval: Interval, git_job: Callable) -> None:
        match interval['unit']:
            case Unit.SECOND:
                self._schedule.every(interval['quantity']).seconds.do(git_job)
            case Unit.MINUTE:
                self._schedule.every(interval['quantity']).minutes.do(git_job)
            case Unit.HOUR:
                self._schedule.every(interval['quantity']).hours.do(git_job)

    def _print_header(self) -> None:
        status_color: str = 'green'
        color_print(f'NOTE:\tForgit was tested with Git Version: {self._tested_git_version}\n', status_color)
        color_print('Forgit - Automatic GIT Commit '.ljust(60, '_'))

    def _print_details(self) -> None:
        if not self._persist:
            os.system('cls' if os.name == 'nt' else 'clear')
            self._print_header()

        detail_list: list[tuple[str, str]] = [
            ('Git Directory: ', to_color(self._git_directory, 'green')),
            ('Repo Check Interval: ', to_color(
                f'{self._git_commit_check_interval["quantity"]}{self._git_commit_check_interval["unit"].value}')),
            ('Last Repo Check: ', datetime.now().strftime("%m/%d/%Y %H:%M:%S")),
            ('Configured Commit Message: ', f'"{self._commit_message}"')
        ]

        for item in detail_list:
            print(f'{item[0].ljust(40, "-")} {item[1]}')
        print()

    def _git_check_commit(self):
        self._print_details()
        git_commit_status: GitManagerStatus = self._git_manager.check_and_commit()
        for line in git_commit_status['debug']:
            logger.info(line)
        git_latest_commit: dict = GitManager.get_latest_git_commit_summary(self._git_directory)
        print(f'  {git_commit_status["debug"][0] if len(git_commit_status["debug"]) > 0 else ""}')

        if len(git_commit_status["debug"]) > 1:
            print(f'  {git_commit_status["debug"][1]}')
        print(f'  {GitManager.latest_git_commit_to_str(git_latest_commit)}\n')

    def run(self):
        try:
            self._setup_schedule(self._git_commit_check_interval, self._git_check_commit)
            logger.info(f'Forgit running on {self._git_directory}')
            self._print_header()
            self._git_check_commit()

            while True:
                self._schedule.run_pending()
                time.sleep(1)

        except KeyboardInterrupt:
            color_print('Forgit stopped.', 'yellow')
        except Exception as e:
            color_print(f'{e}', 'red')
