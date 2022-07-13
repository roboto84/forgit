import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from typing import Any

from halo import Halo
from termcolor import colored

from forgit.types import GitManagerStatus
from forgit.utils import to_color, is_directory, color_print


class GitManager:
    def __init__(self, git_directory: str, commit_message: str):
        self._git_directory = git_directory
        self._commit_message = commit_message

    @staticmethod
    def _is_git_project(path: str):
        for file in os.listdir(path):
            if os.path.isdir(os.path.join(path, file)) and file == '.git':
                return True
        return False

    @staticmethod
    def raw_change_type(raw_change_type: str):
        git_change_types: dict = {
            'M': 'modified',
            'A': 'new file',
            'D': 'deleted',
            'R': 'renamed',
            'C': 'copied',
            'U': 'unmerged'
        }
        return git_change_types.get(raw_change_type)

    @staticmethod
    def get_full_git_repo_path(path: str):
        if is_directory(path):
            if GitManager._is_git_project(path):
                return os.path.abspath(path)
            else:
                print(f'\n  {to_color("Error", "red")}: {to_color(f"""{path}""", "yellow")} '
                      f'is not a valid git repository\n')
                sys.exit(1)
        else:
            print(f'\n  {to_color("Error", "red")}: {to_color(f"""{path}""", "yellow")} is not a valid directory\n')
            sys.exit(1)

    def check_and_commit(self) -> GitManagerStatus:
        debug: list[str] = []
        status: str = 'Commit not needed, Repo left alone.'
        spinner = Halo(text='Tracking')

        try:
            spinner.start()
            spinner.text = 'Checking for file changes'
            git_status: dict = GitManager.get_git_status(self._git_directory, 'changed')
            if len(git_status['modified_files']) > 0 or len(git_status['untracked_files']) > 0:
                spinner.text = f'Committing changes with commit message: "{self._commit_message}"'
                results: tuple[str, str] = GitManager.git_auto_commit(self._git_directory, self._commit_message)
                status = 'Commit attempted'
                debug.append(results[0])
                debug.append(results[1])
            else:
                debug.append(f'Checked Git Repo {self._git_directory} state: {status}')
            spinner.stop()

        except KeyboardInterrupt:
            spinner.stop()
            raise
        except Exception as e:
            color_print(f'\ncheck_and_commit: {e}', 'red')

        return {
            'success': True,
            'status': status,
            'debug': debug
        }

    @staticmethod
    def git_auto_commit(project_path: str, commit_message: str) -> tuple[str, str]:
        git_push_output_text: str = 'unsuccessful'
        git_commit = subprocess.Popen([
            'git',
            'commit',
            '-am',
            f'{commit_message}'
        ], cwd=project_path, stdout=subprocess.PIPE)
        raw_commit_output: str = git_commit.communicate()[0].decode()
        git_commit_output_text: str = ' '.join(raw_commit_output.split('\n'))
        if('file changed' in git_commit_output_text or
                'insertion' in git_commit_output_text or
                'deletion' in git_commit_output_text):
            git_push = subprocess.run([
                'git',
                'push',
            ], cwd=project_path, capture_output=True)
            git_push_output_text: str = ' '.join(git_push.stderr.decode().split('\n'))
        return git_commit_output_text, git_push_output_text

    @staticmethod
    def get_git_status(project_path: str, projects_collect_strategy: str) -> dict:
        # Using https://github.com/git/git/blob/master/wt-status.c#L287 and
        # https://git-scm.com/docs/git-status/2.6.7#_options
        git_change_types: list[str] = ['M', 'D', 'A', 'R', 'C', 'U']
        modified_files: list[dict] = []
        untracked_files: list[dict] = []

        git_status = subprocess.Popen(['git', 'status'], cwd=project_path, stdout=subprocess.PIPE)
        raw_status_output: str = git_status.communicate()[0].decode()
        git_status_output_text: list[str] = raw_status_output.split('\n')
        project_branch: str = ''
        project_branch_status: str = ''
        has_branch_changed_from_origin: bool = False

        if 'branch' in git_status_output_text[0]:
            project_branch: str = git_status_output_text[0].split(' ')[2]
        if 'branch' in git_status_output_text[1]:
            project_branch_status: str = git_status_output_text[1]
            has_branch_changed_from_origin: bool = 'Your branch is up to date' not in project_branch_status

        has_project_got_changes: bool = 'nothing to commit' not in raw_status_output or has_branch_changed_from_origin

        git_status_porcelain = subprocess.Popen(
            ['git', 'status', '--porcelain'],
            cwd=project_path,
            stdout=subprocess.PIPE
        )
        git_status_porcelain_output_text: list[str] = git_status_porcelain.communicate()[0].decode().split('\n')
        git_status_porcelain_output_text = list(filter(None, git_status_porcelain_output_text))

        if projects_collect_strategy != 'latest':
            for output_text in git_status_porcelain_output_text:
                output_text_split = output_text.split(' ')
                output_text_split = list(filter(None, output_text_split))
                output_first_letter: str = output_text_split[0][:1]
                if output_first_letter in git_change_types:
                    modified_files.append({
                        'short_type': output_text_split[0],
                        'long_type': GitManager.raw_change_type(output_first_letter),
                        'file_name': output_text_split[1]
                    })
                elif output_first_letter == '?':
                    untracked_files.append({
                        'type': output_text_split[0],
                        'file_name': output_text_split[1]
                    })

        return {
            'project_branch': project_branch,
            'project_branch_status': project_branch_status,
            'has_branch_changed': has_branch_changed_from_origin,
            'has_project_got_changes': has_project_got_changes,
            'modified_files': modified_files,
            'untracked_files': untracked_files
        }

    @staticmethod
    def get_latest_git_commit_summary(project_path: str) -> dict:
        try:
            temp = subprocess.Popen(['git', 'log'], cwd=project_path, stdout=subprocess.PIPE)
            subprocess_output: tuple[bytes, Any] = temp.communicate()
            raw_log_output: str = subprocess_output[0].decode()
            output_text_list: list[str] = raw_log_output.split('\n')
            current_date: datetime = datetime.now(timezone.utc)
            commit_tracking_index: int = -1
            commit_hash: str = ''
            commit_author: str = ''
            commit_date: str = ''
            commit_message: str = ''

            if raw_log_output != '':
                for index, log_element in enumerate(output_text_list):
                    element_split = log_element.split()
                    if len(element_split):
                        if 'commit' in element_split[0]:
                            if index != 0:
                                break
                            commit_hash = log_element.split()[1][0:7]
                        elif 'Author:' in element_split:
                            commit_author = ''.join(
                                f'{author_part} ' for author_part in log_element.split()[1:-1]).rstrip()
                        elif 'Date:' in element_split:
                            commit_tracking_index = index
                            commit_date = log_element.split(':', 1)[1].strip()
                        elif commit_tracking_index != -1:
                            commit_message = log_element.strip()
                            break

                commit_datetime: datetime = datetime.strptime(commit_date, '%a %b %d %H:%M:%S %Y %z')
                time_since_commit: timedelta = current_date - commit_datetime

                return {
                    'commit_message': commit_message,
                    'commit_date': commit_datetime,
                    'time_since_commit': time_since_commit,
                    'commit_author': commit_author,
                    'commit_hash': commit_hash
                }
            else:
                return {}
        except Exception as error:
            print(f'Received exception: {project_path}: {error}')

    @staticmethod
    def latest_git_commit_to_str(latest_commit: dict) -> str:
        if latest_commit:
            latest_commit_time_delta: tuple = GitManager.time_delta_to_str(latest_commit["time_since_commit"])
            colored_time_delta: str = colored(
                f'{latest_commit_time_delta[0]} {latest_commit_time_delta[1]} ago',
                attrs=['bold']
            )
            colored_author: str = colored(latest_commit["commit_author"], attrs=["bold"])
            return f'Latest {colored_time_delta} by {colored_author} ' \
                   f'({latest_commit["commit_date"].strftime("%m/%d/%Y %H:%M")}) ' \
                   f'{colored(latest_commit["commit_hash"], "magenta")}: ' \
                   f'{latest_commit["commit_message"]}'
        else:
            return 'Current branch does not have any commits yet'

    @staticmethod
    def time_delta_to_str(time_delta: timedelta) -> tuple[int, str]:
        week_divisor: int = 7
        month_divisor: int = 4
        year_divisor: int = 12
        time_delta_hours_estimate: int = int(time_delta.total_seconds() / (60 * 60 * 24))
        time_word: str = 'days' if time_delta_hours_estimate > 1 else 'day'

        if time_delta_hours_estimate > week_divisor:
            time_delta_hours_estimate = int(time_delta_hours_estimate / week_divisor)
            time_word = 'weeks' if time_delta_hours_estimate > 1 else 'week'
        if time_delta_hours_estimate > month_divisor:
            time_delta_hours_estimate = int(time_delta_hours_estimate / month_divisor)
            time_word = 'months' if time_delta_hours_estimate > 1 else 'month'
        if time_delta_hours_estimate > year_divisor:
            time_delta_hours_estimate = int(time_delta_hours_estimate / year_divisor)
            time_word = 'years' if time_delta_hours_estimate > 1 else 'year'
        return time_delta_hours_estimate, time_word
