"""Loguru logger setup.
"""
from loguru import logger
import os
import sys

from ._constants import *
from ._utils import app_path, make_dir, touch_file


DIR_PATH = os.path.join(app_path(), 'logs')
FILE_NAME = 'app.log'
FULL_PATH = os.path.join(DIR_PATH, FILE_NAME)

make_dir(DIR_PATH)
touch_file(FILE_NAME, DIR_PATH)

# Remove all default handlers.
logger.remove()

# Add a file handler.
logger.add(
    FULL_PATH,
    level='DEBUG',
    rotation='12:00',
    retention='10 days',
    filter=lambda record: not 'excluded' in record['extra'] # By specified `logger.bind(excluded=True).info(...)` in the code can filter out the log.
)

# Add a stdout handler.
logger.add(
    sys.stderr,
    format='<level>{message}</level>',
    level='INFO'
)
