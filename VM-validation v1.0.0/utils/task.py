""""
This file is used to perform various functions

Written by Mike van der Steen
Version 1.00

last updated: 1 January 2023
"""

from utils import log

logger = log.custom_logger()


def compare_dict_with_list_inclusion(user_dictionary: dict, user_list: list) -> dict:
    """
    Compare a dictionary with a list and export a list that includes items common in both
    """
    # New dictionary containing only common items in dictionary and list
    common_items = {}

    # Compare the key of the dictionary to the items in the list
    for key, value in user_dictionary.items():
        if key in user_list:
            common_items[key] = value

    msg = f'Compared dictionary to list and resulted in {len(common_items)} common items'
    logger.info(msg)
    return common_items


def compare_list_with_dict_exclusion(user_list: list, user_dictionary: dict) -> list:
    """
    Compare a list with a dictionary and export a list of items not found in the dict
    """
    # New dictionary containing only common items in dictionary and list
    uncommon_items = []

    # Compare the list to the first key of the dictionary
    for value in user_list:
        if value not in user_dictionary:
            uncommon_items.append(value)
            msg = f'VM called {value} in User Defined List of VMs, was not found in backup server protected VM list ' \
                  f'and is being excluded from VM validation.'
            logger.info(msg)
    return uncommon_items
