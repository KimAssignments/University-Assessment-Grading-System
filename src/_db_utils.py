"""Pandas database utilities.
"""
from pathlib import Path
from typing import Literal, Union
import numpy as np
import os
import pandas as pd
import platform

from ._constants import *
from ._utils import app_path, make_dir, touch_file

PATH = os.path.join(app_path(), 'data')
make_dir(PATH)

def pull_data(
    section: Literal['courses_list', 'students_info', 'results'],
    dtype: Union[np.dtype, str, complex, bool, object]=str,
) -> pd.DataFrame:
    """Pulls data from the database.

    Args:
        section (courses_list', 'students_info'): The section of the database to pull from.
        dtype (numpy.dtype, str, complex, bool, object), optional: The data type of the data. Defaults to str.

    Returns:
        pandas.DataFrame: The data.
    """
    FILENAME = section + '.csv'
    touch_file(FILENAME, PATH)
    if os.path.getsize(os.path.join(PATH, FILENAME)) == 0:
        return pd.DataFrame()

    return pd.read_csv(os.path.join(PATH, FILENAME), index_col=0, dtype=dtype, encoding='utf-8')

def push_data(
    data: pd.DataFrame,
    section: Literal['courses_list', 'students_info'],
) -> None:
    """Pushes data to the database.

    Args:
        data (pandas.DataFrame): The data to push.
        section ('courses_list', 'students_info'): The section of the database to push to.

    Returns:
        None
    """
    FILENAME = section + '.csv'
    touch_file(FILENAME, PATH)

    return data.to_csv(os.path.join(PATH, FILENAME), encoding='utf-8')

def drop_duplicates(
    section: Literal['courses_list', 'students_info'],
    code: str=MISSING,
    keep: Literal['first', 'last', False]='first',
) -> None:
    """Drops duplicates from the database.
    """
    df = pull_data(section)
    if code is MISSING:
        df.drop_duplicates(subset=['code'], keep=keep, inplace=True)

    else:
        df['code' == code].drop_duplicates(subset=['code'], keep=keep, inplace=True)

    return push_data(df, section)

