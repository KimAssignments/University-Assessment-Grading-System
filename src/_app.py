
from typing import Literal
import base64
import json
import os
import pandas as pd

from ._constants import *
from ._db_utils import pull_data, push_data
from ._log_utils import logger
from ._utils import app_path, make_dir, touch_file


class Application:
    """The main class for the application.
    """
    def __init__(self, section: Literal['courses_list', 'students_info', 'results']):
        """Initializes the class.
        The application will be initialized with a given section either 'courses_list', 'students_info', or 'results'.
        """
        self.section = section
        self.class_name = self.__class__.__name__

        self._view_children: list = []

        # Initialize the view children (column).
        self._init_view_children()

    def pull(self) -> pd.DataFrame:
        """Gets the data.
        """
        return pull_data(self.section)

    def push(self, data: pd.DataFrame) -> None:
        """Pushes data to the database.
        """
        return push_data(data, self.section)

    @property
    def children(self) -> list:
        """Gets the available whitelisted childrens (columns).
        """
        return self._view_children

    def _init_view_children(self) -> None:
        """Initializes the view children (column).
        Pulling the columns from the database.
        """
        df = self.pull()
        for col in df.columns:
            self._view_children.append(col)

    def add_item(self, item: str) -> None:
        """Manually adds an item to the view children (column).
        """
        if item in self.children:
            return

        self._view_children.append(item)

    def remove_item(self, item: str) -> None:
        """Manually removes an item from the view children (column).
        """
        if item not in self.children:
            return

        self._view_children.remove(item)

    def view(self, code: str) -> pd.DataFrame:
        """Views the data.
        """
        df = self.pull()
        if code not in df.index:
            return pd.DataFrame()

        return df.loc[pd.Index([code])]

    def append(self, code: str) -> None:
        """Appends a new entry to the database.
        """
        df = self.pull()

        # If the code already exists, return.
        if code in df.index:
            return logger.bind(excluded=True).warning(f'{self.class_name}: Code already exists: {code}')

        # Create a new entry by adding the children as keys and None as values.
        entry: dict = {k: [None] for k in self.children}

        # Concatenate the new entry to the database.
        final = pd.concat(
            [df, pd.DataFrame(entry, index=[code])],
            verify_integrity=True,
            sort=True
        )

        self.push(final)
        logger.info(f'{self.class_name}: {code} appended successfully.')

    def delete(self, code: str) -> None:
        """Deletes an entry from the database.
        """
        df = self.pull()

        # If the code does not exist, return.
        if code not in df.index:
            return logger.bind(excluded=True).warning(f'{self.class_name}: Code not exists: {code}')

        # Drop the entry from the database.
        df.drop(index=code, inplace=True)

        self.push(df)
        logger.warning(f'{self.class_name}: {code} deleted successfully.')

    def edit(self, code: str, **kwargs) -> None:
        """Edits an entry from the database.

        Usage:
            __class__.edit('code', key1=value1, key2=value2, ...)
            __class__.edit('code', **{'key1': value1, 'key2': value2, ...})
        """
        df = self.pull()

        # If the code does not exist, return.
        if code not in df.index:
            return logger.bind(excluded=True).warning(f'{self.class_name}: Code not exists: {code}')

        # Go through the given kwargs and edit the database.
        for k, v in kwargs.items():
            # If the key is not in the whitelist, skip.
            if k not in self.children:
                logger.bind(excluded=True).warning(f'{self.class_name}: Key not in whitelist: {k}')
                continue

            # Edit the database.
            df.loc[code, k] = v
            logger.info(f'{self.class_name}: {code} edited successfully. {k} = {v}')

        self.push(df)

    def search(self, keyword: str) -> pd.DataFrame:
        """Searches the database by keyword.
        """
        df = self.pull()

        # Return the dataframe with indexes that contain the keyword.
        return df[df.index.str.contains(keyword, case=False)]

class User:
    """The user class for the application.
    """
    def __init__(self):
        self.PATH = os.path.join(app_path(), 'data')
        self.FILENAME = 'user.json'
        self.FULL_PATH = os.path.join(self.PATH, self.FILENAME)
        self.class_name = self.__class__.__name__

        # Create the file if it does not exist.
        make_dir(self.PATH)
        touch_file(self.FILENAME, self.PATH)

        # If the file is empty, write an empty dictionary to prevent json.decoder.JSONDecodeError.
        if os.stat(self.FULL_PATH).st_size == 0:
            with open(self.FULL_PATH, 'w', encoding='utf-8') as f:
                f.write('{}')

    @staticmethod
    def encrypt_password(password: str) -> bytes:
        """Encrypts the password.
        """
        return base64.b64encode(password.encode('utf-8'))

    def check(self, username: str) -> bool:
        """Checks if the username exists.
        """
        with open(self.FULL_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return username in data.keys()

    def login(self, username: str, password: str, silent: bool=False) -> bool:
        """Logs in the user.
        """
        with open(self.FULL_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # If the username does not exist, return.
        if not self.check(username):
            logger.bind(excluded=True).warning(f'{self.class_name}: {username} does not exist')
            return False

        # Encrypt the given password and compare it with real encrypted password.
        result = data[username] == str(self.encrypt_password(password))

        if result and not silent:
            logger.info(f'{self.class_name}: {username} logged in')

        return result

    def register(self, username: str, password: str) -> bool:
        """Registers a new user.
        """
        with open(self.FULL_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # If the username already exists, return.
        if self.check(username):
            return False

        # Encrypt the password and add it to the dictionary.
        data[username] = str(self.encrypt_password(password))

        with open(self.FULL_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

        logger.info(f'{self.class_name}: {username} registered')
        return True

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Changes the password of the user.
        """
        with open(self.FULL_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # If the username does not exist, return.
        if not self.check(username):
            logger.bind(excluded=True).warning(f'{self.class_name}: Username not exists: {username}')
            return False

        # If the old password is incorrect, return.
        if not self.login(username, old_password, silent=True):
            logger.bind(excluded=True).warning(f'{self.class_name}: Incorrect password: {username}')
            return False

        # Encrypt the password and update the database.
        data[username] = str(self.encrypt_password(new_password))
        with open(self.FULL_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

        logger.info(f'{self.class_name}: {username} changed password successfully.')
        return True