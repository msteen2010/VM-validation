"""
This file is used to perform various function on file related tasks

author: Mike van der Steen
last updated: 31 July 2023
"""

from pathlib import Path
from datetime import datetime
from configparser import SafeConfigParser
import json
import os

from utils import log

logger = log.custom_logger()


def read_config_file_int(filepath: str, heading: str, key: str) -> int:
    """
    Read the contents of the config.ini file and assign return the associate value
    """

    # Attempt to read the config.ini file
    parser = SafeConfigParser()
    try:
        parser.read(filepath)
        msg = f'Successfully accessed the config.ini file at location {filepath}'
        logger.info(msg)
    except FileNotFoundError:
        msg = f'Config.ini file could not be found in the location {filepath}'
        logger.error(msg)

    # Attempt to extract the desired value from the key
    try:
        parser.read(filepath)
        value = int(parser.get(heading, key))
        msg = f'Successfully read the value for key {key} from heading {heading}'
        logger.info(msg)
        if isinstance(value, int):
            return value
        else:
            return -99999
    except Exception as e:
        msg = f'Failed to read the value for key {key} from heading {heading}'
        logger.error(msg)
        logger.error(str(e))
        return -99999


def read_config_file_str(filepath: str, heading: str, key: str) -> str:
    """
    Read the contents of the config.ini file and assign return the associate value
    """

    # Read the config.ini file and extract the desired value from the key
    parser = SafeConfigParser()
    parser.read(filepath)
    value = parser.get(heading, key)
    return value


def create_directory(directory: str):
    """
    Create an output directory if it does not exist
    """

    # Check to see if the directory exists and if not, create it
    if Path(directory).exists():
        logger.info(f'The output directory already exists for {directory}')
    else:
        path = Path.cwd() / directory
        path.mkdir()
        logger.info(f'Created the output directory of {directory}')


def write_list(filepath: str, input_list: list):
    """
    Write data from a list to a text file
    """
    try:
        with open(filepath, 'w') as filehandle:
            for items in input_list:
                filehandle.write(f'{items}\n')
            msg = f'Output has been written to {filepath}'
            logger.info(msg)

    except FileNotFoundError:
        msg = f'File could not be created and written to for {filepath}'
        logger.error(msg)


def write_dict_key(filepath: str, input_dict: dict):
    """
    Write data from a list to a text file
    """
    try:
        with open(filepath, 'w') as filehandle:
            for key in input_dict:
                filehandle.write(f'{key}\n')
            msg = f'Output has been written to {filepath}'
            logger.info(msg)

    except FileNotFoundError:
        msg = f'File could not be created and written to for {filepath}'
        logger.error(msg)


def append_list(filepath: str, filelist: list):
    """
    Write data from a list to a text file
    """
    try:
        with open(filepath, 'a') as filehandle:
            for items in filelist:
                filehandle.write(f'{items}\n')
            msg = f'Output has been written to {filepath}'
            logger.info(msg)

    except FileNotFoundError:
        msg = f'File could not be created and written to for {filepath}'
        logger.error(msg)


def write_text(filepath: str, text: str):
    """
    Write data to a text file
    """
    try:
        with open(filepath, 'w') as filehandle:
            filehandle.write(f'{text}')
            msg = f'Output has been written to {filepath}'
            logger.info(msg)

    except FileNotFoundError:
        msg = f'File could not be created and written to for {filepath}'
        logger.error(msg)


def create_datetime_file(directory: str, filename: str) -> str:
    """
    Create a file with the datetime set as a prefix with a directory as the input
    """

    # Check to see if the directory exists, if not create it
    create_directory(directory)

    # Obtain the current datetime to prefix the output filename
    now = datetime.now()
    dt_string = now.strftime('%Y%m%d %H.%M')
    complete_filename = str(dt_string) + filename

    # Create full path to file with date prefix
    filepath = os.path.join(directory, complete_filename)

    return filepath


def append_datetime_prefix(filepath: str, text: str) -> None:
    """
    Append information to a file with a datetime prefix to the information
    """
    try:
        with open(filepath, 'a') as filehandle:

            # Obtain the current datetime to prefix the output filename
            now = datetime.now()
            dt_string = now.strftime('%Y%m%d %H:%M:%S')
            data = str(dt_string) + ' ' + text + '\n'

            filehandle.write(data)

    except FileNotFoundError:
        msg = f'Text could not be written to {filepath}'
        logger.error(msg)


def write_json(filepath: str, data: str, description: str):
    """
    Write JSON data to a text file with indentation to make it easier to read
    """
    try:
        with open(filepath, 'w') as filehandle:
            # output = json.load(data)
            pretty_json = json.dumps(data, indent=4)
            filehandle.write(f'{pretty_json}')
            msg = f'Output of {description} has been written to {filepath}'
            logger.info(msg)

    except FileNotFoundError:
        msg = f'File could not be created and written to for {description}'
        logger.error(msg)


def create_list(filepath: str) -> list:
    """
    Read from a file the contents and append this to a list
    """
    msg = f'Path of the file containing the list of VMs to validate is: {filepath}'
    logger.info(msg)

    # Read the contents of the text file containing the list of VMs

    if Path(filepath).exists():
        # Read the contents of the file
        data = open(filepath).readlines()
        vm_list = [s.rstrip() for s in data]
        number_vms = len(vm_list)
        msg = f'The number of VMs listed in the {filepath} is: {number_vms}'
        logger.info(msg)
        return vm_list
    else:
        msg = 'Unable to locate the text file, please check that it exists or the name of it, including the suffix'
        logger.error(msg)
