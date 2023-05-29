""""
This file is used to work with PowerProtect Data Manager using the RESTful APIs

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
    Making an API authentication call to the PowerProtect Data Manager server
    """

    uri = f'https://{server}:8443/api/v2/login'
    headers = {'Content-Type': 'application/json'}
    payload = '{"username":"%s", "password":"%s"}' % (user, password)

    # Logging the API call being made
    msg = f'Marking API call: {uri}'
    logger.info(msg)

    # Try to make an authentication API call to PowerProtect Data Manager
    try:
        r = requests.post(uri, data=payload, headers=headers, verify=False, timeout=glb.api_call_timeout)
        r.raise_for_status()
        msg = f'Making login authentication API call to {uri}'
        logger.info(msg)

        if r.status_code == 200:
            msg = f'Successful response received for API call to {server}'
            logger.info(msg)
            # Return the JSON output for processing
            data = r.json()
            return data
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


def refresh_token_api_call(server: str, token: str, refresh_token: str) -> str:
    """
    Making an API authentication call to the PowerProtect Data Manager server
    """

    uri = f'https://{server}:8443/api/v2/token'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(token)}
    payload = '{"refresh_token": "%s","grant_type": "refresh_token","scope": "aaa"}' % refresh_token

    # Logging the API call being made
    msg = f'Marking API call: {uri}'
    logger.info(msg)

    # Try to make refresh token API call to PowerProtect Data Manager
    try:
        r = requests.post(uri, data=payload, headers=headers, verify=False, timeout=glb.api_call_timeout)
        r.raise_for_status()
        msg = f'Making refresh token API call to {uri}'
        logger.info(msg)

        if r.status_code == 200:
            msg = f'Successful response received for API call to {server}'
            logger.info(msg)
            # Return the JSON output for processing
            data = r.json()
            return data
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


def get_api_call(uri: str, headers: dict, params: dict) -> str:
    """
    Making an GET API call to the PowerProtect Data Manager server
    """

    # Logging the API call being made
    msg = f'Marking GET API call: {uri}'
    logger.info(msg)

    # Try to make an authentication API call to PowerProtect Data Manager
    try:
        if params == '':
            r = requests.get(uri, headers=headers, verify=False, timeout=glb.api_call_timeout)
            r.raise_for_status()
        else:
            r = requests.get(uri, headers=headers, params=params, verify=False, timeout=glb.api_call_timeout)
            r.raise_for_status()
        msg = f'Making login authentication API call to {uri}'
        logger.info(msg)

        if r.status_code == 200:
            msg = f'Successful response received for API call'
            logger.info(msg)
            # Return the JSON output for processing
            data = r.json()
            return data
        else:
            msg = f'API call failed'
            logger.error(msg)
            msg = f'Response code: {str(r.status_code)}'
            logger.debug(msg)
            return 'API call unsuccessful'

    except Exception as e:
        msg = f'API call timed out trying to reach - {uri}'
        logger.error(msg)
        logger.debug(str(e))
        return 'API call unsuccessful'


def post_api_call(uri: str, headers: dict, payload: dict) -> str:
    """
    Making a POST API call to the PowerProtect Data Manager server
    """

    # Logging the API call being made
    msg = f'Marking POST API call: {uri}'
    logger.info(msg)

    # Try to make an authentication API call to PowerProtect Data Manager
    try:
        r = requests.post(uri, data=payload, headers=headers, verify=False, timeout=glb.api_call_timeout)
        r.raise_for_status()
        msg = f'Making login authentication API call to {uri}'
        logger.info(msg)

        if r.status_code == 201:
            msg = f'Successful response received for API call'
            logger.info(msg)
            # Return the JSON output for processing
            data = r.json()
            return data
        else:
            msg = f'API call failed'
            logger.error(msg)
            msg = f'Response code: {str(r.status_code)}'
            logger.debug(msg)
            return 'API call unsuccessful'

    except Exception as e:
        msg = f'API call timed out trying to reach - {uri}'
        logger.error(msg)
        logger.debug(str(e))
        return 'API call unsuccessful'


def get_protected_vms(server: str, token: str) -> str:
    """
    Get API call to PowerProtect Data Manager to get a list of protected VMs
    """
    # Build the URL for the API call
    uri = f'https://{server}:8443/api/v2/assets'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(token)}
    filters = 'protectionStatus eq "PROTECTED" and type eq "VMWARE_VIRTUAL_MACHINE"'
    params = {'filter': filters}

    # Making the API call and get the json response if the call is successful
    protected_vms = get_api_call(uri, headers, params)
    if protected_vms != 'API call unsuccessful':
        return protected_vms
    else:
        return 'API call unsuccessful'


def get_asset_backups(server: str, token: str, asset_id: str) -> str:
    """
    Get API call to PowerProtect Data Manager to get the latest backup of a VM by asset ID
    """
    # Build the URL for the API call
    uri = f'https://{server}:8443/api/v2/assets/{asset_id}/copies'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(token)}
    params = {}

    # Making the API call and get the json response if the call is successful
    backups = get_api_call(uri, headers, params)
    if backups != 'API call unsuccessful':
        return backups
    else:
        return 'API call unsuccessful'


def get_asset_info(server: str, token: str, asset_id: str) -> str:
    """
    Get API call to PowerProtect Data Manager to get information about the asset
    """
    # Build the URL for the API call
    uri = f'https://{server}:8443/api/v2/assets/{asset_id}'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(token)}
    params = {}

    # Making the API call and get the json response if the call is successful
    asset_info = get_api_call(uri, headers, params)
    if asset_info != 'API call unsuccessful':
        return asset_info
    else:
        return 'API call unsuccessful'


def instant_access_recovery(server: str, token: str, payload: dict) -> str:
    """
    Post API call to PowerProtect Data Manager to start instant access recovery of VM
    """
    # Build the URL for the API call
    uri = f'https://{server}:8443/api/v2/restored-copies'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(token)}

    # Making the API call and get the json response if the call is successful
    recovery = post_api_call(uri, headers, payload)
    if recovery != 'API call unsuccessful':
        return recovery
    else:
        return 'API call unsuccessful'


def cancel_instant_access_recovery(server: str, token: str, activity_id: str) -> str:
    """
    Post API call to PowerProtect Data Manager to cancel instant access recovery of VM
    """
    # Build the URL for the API call
    uri = f'https://{server}:8443/api/v2/restored-copies/{activity_id}/remove'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(token)}

    # Logging the API call being made
    msg = f'Marking POST API call: {uri}'
    logger.info(msg)

    # Try to make an authentication API call to PowerProtect Data Manager
    try:
        r = requests.post(uri, headers=headers, verify=False, timeout=glb.api_call_timeout)
        r.raise_for_status()
        msg = f'Making login authentication API call to {uri}'
        logger.info(msg)

        if r.status_code == 202:
            msg = f'Successful response received for API call'
            logger.info(msg)
            # Return the JSON output for processing
            data = r.json()
            return 'API call successful'
        else:
            msg = f'API call failed'
            logger.error(msg)
            msg = f'Response code: {str(r.status_code)}'
            logger.debug(msg)
            return 'API call unsuccessful'

    except Exception as e:
        msg = f'API call timed out trying to reach - {uri}'
        logger.error(msg)
        logger.debug(str(e))
        return 'API call unsuccessful'
