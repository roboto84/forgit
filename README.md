<h1 align="center">forgit</h1>

<div align="center">
	<img src="assets/forgit.png" width="250" title="forgit logo">
</div>

## About
`forgit` is a tool that automatically git commits to a repo at a given
time interval (*24hrs by default*) if tracked files have changed.

## Requirements
- [pipx](https://github.com/pypa/pipx "pipx") or [poetry](https://github.com/python-poetry/poetry "poetry")
- Python 3.10^

## Install
- With pipx:
    ```
    pipx install git+https://github.com/roboto84/forgit.git
    ```

or

- Local build with poetry:
    ```
    git clone https://github.com/roboto84/forgit.git
    ```
    ```
    cd forgit
    ```
    ```
    poetry install
    ```

## Usage
- With pipx
    ```
    forgit
    ```

- With poetry
    ```
    poetry run forgit
    ```

## Options
| Flag | Title | Description | Use
|------|-------|-------------|-----
| `-h` | help | Show help menu. | `forgit -h`
| `-v` | version | Show `forgit` version. | `forgit -v`
| `-p` | persist | By default Forgit clears the terminal on each status refresh. Set `-p` to disable this feature. | `forgit -p`
| `-d path` | directory path | Git directory to manage. <br/>Default: `./` | `forgit -d /home/projectA`
| `-i time` | interval time | Interval to check the given git repository for a possible auto-commit. <br/>Default: `24h` | `forgit -i 10h`
| `-m message` | commit message | Git commit message. <br/>Default: `auto-commit` | `forgit -m "My commit message."`

## Commit Conventions
Git commits follow [Conventional Commits](https://www.conventionalcommits.org) message style as explained in detail on their website.

<br/>
<sup>
    <a href="https://www.flaticon.com/free-icons/automatic" title="automatic icons">
        forgit icon created by Parzival’ 1997  - Flaticon
    </a>
</sup>
