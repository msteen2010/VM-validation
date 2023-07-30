"""
This file is used to set the logging parameters

author: Mike van der Steen
last updated: 31 July 2023
"""


import logging
from pathlib import Path


def custom_logger():
    """
    Define the format of the output when logging
    """

    # Check to see if the logs directory exists, if not create it
    if not Path('logs').exists():
        path = Path.cwd() / 'logs'
        path.mkdir()

    logger = logging.getLogger(__name__)
    if not len(logger.handlers):
        # Set the parameters for logging
        formatter = logging.Formatter(fmt='%(asctime)s : %(levelname)s : %(module)s : %(lineno)d : %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('logs/debug.log', mode='w', delay=False)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger
