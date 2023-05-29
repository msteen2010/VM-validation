""""
This file is used to work with vCenter using the RESTful APIs

Written by Mike van der Steen
Version 1.00

last updated: 29 December 2022
"""

import requests
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

from utils import log
from utils import globals as glb

disable_warnings(InsecureRequestWarning)
logger = log.custom_logger()


def authenticate_api_call(server: str, user: str, password: str) -> str:
    """
    Making an API authentication call to vCenter
    """

    uri = f'https://{server}/rest/com/vmware/cis/session'

    # Logging the API call being made
    msg = f'Marking API call: {uri}'
    logger.info(msg)

    # Try to make an authentication API call to PowerProtect Data Manager
    try:
        r = requests.post(uri, auth=(user, password), verify=False, timeout=glb.api_call_timeout)
        r.raise_for_status()
        msg = f'Making login authentication API call to {uri}'
        logger.info(msg)

        if r.status_code == 200:
            msg = f'Successful response received for API call to {server}'
            logger.info(msg)
            # Return the JSON output for processing
            data = r.json()
            # Grapping the authentication value (vmware-api-session-id) from the reponse
            return data['value']
        else:
            msg = f'API call failed to {server}'
            logger.error(msg)
            msg = f'Response code: {str(r.status_code)}'
            logger.debug(msg)
            return 'API call unsuccessful'

    except Exception as e:
        msg = f'API call timed out trying to reach - {uri}'
        logger.error(msg)
        logger.debug(str(e))
        return 'API call unsuccessful'


def get_api_call(uri: str, headers: dict) -> str:
    """
    Making a GET API call to get the datacenterMoref value
    """

    # Logging the API call being made
    msg = f'Marking API call: {uri}'
    logger.info(msg)

    # Try to make the API call to vCenter
    try:
        r = requests.get(uri, headers=headers, verify=False, timeout=glb.api_call_timeout)
        r.raise_for_status()

        if r.status_code == 200:
            msg = f'Successful response received for API call to {uri}'
            logger.info(msg)
            # Return the JSON output for processing
            data = r.json()
            return data
        else:
            msg = f'API call failed to {uri}'
            logger.error(msg)
            msg = f'Response code: {str(r.status_code)}'
            logger.debug(msg)
            return 'API call unsuccessful'

    except Exception as e:
        msg = f'API call timed out trying to reach - {uri}'
        logger.error(msg)
        logger.debug(str(e))
        return 'API call unsuccessful'


def get_datacenter_json(server: str, token: str) -> str:
    """
    Making a GET API call to get the datacenterMoref value
    """

    uri = f'https://{server}/rest/vcenter/datacenter'
    headers = {'vmware-api-session-id': '{}'.format(token)}

    response = get_api_call(uri, headers)
    return response


def get_clusters_json(server: str, token: str) -> str:
    """
    Making a GET API call to get the datacenterMoref value
    """

    uri = f'https://{server}/rest/vcenter/cluster'
    headers = {'vmware-api-session-id': '{}'.format(token)}

    response = get_api_call(uri, headers)
    return response



