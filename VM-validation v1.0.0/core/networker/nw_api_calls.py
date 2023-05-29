""""
This file is used to work with NetWorker using the RESTful APIs

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


def get_api_call(server: str, user: str, password: str, uri: str) -> str:
    """
    Making an API call to the NetWorker server
    """

    # Logging the API call being made
    msg = f'Marking API call: {uri}'
    logger.info(msg)

    # A timeout value of 30 seconds has been applied and if reached, allows the application to continue
    try:
        r = requests.get(uri, auth=(user, password), verify=False, timeout=glb.api_call_timeout)
        msg = f'Making Get API call to {uri}'
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


def post_api_call(server: str, user: str, password: str, uri: str, data: str) -> str:
    """
    Making an POST API call to the NetWorker server
    """

    # Logging the API call being made
    msg = f'Marking POST API call: {uri}'
    logger.info(msg)

    # A timeout value of 30 seconds has been applied and if reached, allows the application to continue
    try:
        r = requests.post(uri, auth=(user, password), json=data, verify=False, timeout=glb.api_call_timeout)
        msg = f'Making POST API call to {uri}'
        logger.info(msg)

        if r.status_code == 201:
            # networker.api_call_success = True
            msg = f'Successful response received for API call to {server}'
            logger.info(msg)
            # Return the JSON output for processing
            data = r.headers
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


def post_api_cancel_job(server: str, user: str, password: str, uri: str, data) -> bool:
    """
    Making an POST API call to the NetWorker server to cancel a job
    """

    # Logging the API call being made
    msg = f'Marking POST API call: {uri}'
    logger.info(msg)

    # A timeout value of 30 seconds has been applied and if reached, allows the application to continue
    try:
        r = requests.post(uri, auth=(user, password), json=data, verify=False, timeout=30)
        msg = f'Making POST API call to {uri}'
        logger.info(msg)

        if r.status_code == 202:
            # networker.api_call_success = True
            msg = f'Successful response received for API call to {server} for cancelling job'
            logger.info(msg)
            return True

        else:
            msg = f'API call failed to {server}'
            logger.error(msg)
            msg = f'Response code: {str(r.status_code)}'
            logger.debug(msg)
            return False

    except Exception as e:
        msg = f'API call timed out trying to reach - {uri}'
        logger.error(msg)
        logger.debug(str(e))


def get_alerts(server: str, user: str, password: str) -> str:
    """
    Get API call to the NetWorker server for list of current alerts and a good way to test the credentials
    """
    # Build the URL for the API call
    uri = 'https://' + server + ':9090/nwrestapi/v3/global/alerts'

    # Making the API call and get the json response if the call is successful
    alerts_json = get_api_call(server, user, password, uri)
    if alerts_json != 'API call unsuccessful':
        return alerts_json
    else:
        return 'API call unsuccessful'


def get_protected_vms(server: str, user: str, password: str, vcenter) -> str:
    """
    Get API call to the NetWorker server for list of protected VMs
    """
    # Build the URL for the API call
    uri = 'https://' + server + ':9090/nwrestapi/v3/global/vmware/vcenters/' \
          + vcenter.fqdn + '/protectedvms'

    # Making the API call and get the json response if the call is successful
    protected_vms_json = get_api_call(server, user, password, uri)
    if protected_vms_json != 'Failed':
        return protected_vms_json
    else:
        return 'API call unsuccessful'


def get_protected_vm_lastest_backup(server: str, user: str, password: str, protected_vm: str, protected_vm_href: str):
    """
    Get API call to the NetWorker server to get the latest recovery API URL for a protected VM backup
    """
    # Build the URL for the API call
    uri = protected_vm_href + '/backups'

    # Making the API call and get the json response if the call is successful
    protected_vm_latest_backups_json = get_api_call(server, user, password, uri)
    if protected_vm_latest_backups_json != 'Failed':
        return protected_vm_latest_backups_json
    else:
        return 'API call unsuccessful'
