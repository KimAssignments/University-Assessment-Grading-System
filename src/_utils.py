
from pathlib import Path
from textwrap import dedent
import os
import platform

from ._constants import *

def cls() -> None:
    """Clears the screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print(dedent(f'''

    ░█████╗░███╗░░██╗  ░█████╗░░██████╗░██████╗██╗░██████╗░███╗░░██╗███╗░░░███╗███████╗███╗░░██╗████████╗
    ██╔══██╗████╗░██║  ██╔══██╗██╔════╝██╔════╝██║██╔════╝░████╗░██║████╗░████║██╔════╝████╗░██║╚══██╔══╝
    ███████║██╔██╗██║  ███████║╚█████╗░╚█████╗░██║██║░░██╗░██╔██╗██║██╔████╔██║█████╗░░██╔██╗██║░░░██║░░░
    ██╔══██║██║╚████║  ██╔══██║░╚═══██╗░╚═══██╗██║██║░░╚██╗██║╚████║██║╚██╔╝██║██╔══╝░░██║╚████║░░░██║░░░
    ██║░░██║██║░╚███║  ██║░░██║██████╔╝██████╔╝██║╚██████╔╝██║░╚███║██║░╚═╝░██║███████╗██║░╚███║░░░██║░░░
    ╚═╝░░╚═╝╚═╝░░╚══╝  ╚═╝░░╚═╝╚═════╝░╚═════╝░╚═╝░╚═════╝░╚═╝░░╚══╝╚═╝░░░░░╚═╝╚══════╝╚═╝░░╚══╝░░░╚═╝░░░

    '''))

def app_path() -> str:
    """Returns the path to the application data directory.
    """
    uname = platform.system()
    if uname == 'Windows':
        return os.path.join(os.environ['APPDATA'], 'Kim', 'UTAR')
    elif uname == 'Linux':
        return os.path.join(os.environ['HOME'], '.kim', 'utar')
    elif uname == 'Darwin':
        return os.path.join(os.environ['HOME'], 'Library', 'Application Support', 'Kim', 'UTAR')
    else:
        return os.path.join(os.getcwd(), '.kim', 'utar')

def make_dir(path: str=MISSING) -> None:
    """Generates a directory if it does not exist.
    If path is not specified, the directory will be generated in the application data directory.
    """
    path = app_path() if path is MISSING else path
    if os.path.exists(path):
        return

    return os.makedirs(path)

def touch_file(filename: str, path: str=MISSING, exist_ok: bool=True) -> None:
    """Generates a file if it does not exist.

        path (str, optional): If not specified, the file will be generated in the application data directory.
        exist_ok (bool, optional): If True, do nothing if the file already exists. Defaults to True.
    """
    path = os.path.join(
        app_path() if path is MISSING else path,
        filename
    )

    return Path(path).touch(exist_ok=exist_ok)

def generate_backup(filename: str, path: str=MISSING) -> None:
    """TODO: Generate a backup of the database.
    """
    pass
