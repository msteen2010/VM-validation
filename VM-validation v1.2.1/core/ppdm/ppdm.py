""""
This file is used create a PowerProtect Data Manager object

author: Mike van der Steen
last updated: 26 November 2024
"""

import requests
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

from utils import log
from utils import global_variables as glb_v

disable_warnings(InsecureRequestWarning)
logger = log.custom_logger()


# Defining the class for PowerProtect Data Manager
class PowerProtectDataManager(object):
    def __init__(self):
        self.fqdn = ''
        self.user = ''
        self.password = ''
        self.token_json = ''
        self.token = ''
        self.refresh_token = ''
        self.jti = ''
        self.api_call_success = False
        self.protected_vms_json = ''
        self.protected_vms_names_id = {}
        self.user_vm_names = []
        self.user_vm_names_id = {}
        self.temp_vm_latest_backup_json = ''
        self.temp_backup_id = ''
        self.temp_asset_info_json = ''
        self.temp_payload = {}
        self.temp_activity_id = ''
        self.proceed_with_instant_access = False
        self.number_of_vms = 0
        self.vm_successfully_processed = 0
        self.validation_summary = []

    def authenticate_api_call(self) -> str:
        """
        Making an API authentication call to the PowerProtect Data Manager server
        """

        uri = f'https://{self.fqdn}:8443/api/v2/login'
        headers = {'Content-Type': 'application/json'}
        payload = '{"username":"%s", "password":"%s"}' % (self.user, self.password)

        # Logging the API call being made
        msg = f'Marking API call: {uri}'
        logger.info(msg)

        # Try to make an authentication API call to PowerProtect Data Manager
        try:
            r = requests.post(uri, data=payload, headers=headers, verify=False, timeout=glb_v.api_call_timeout)
            r.raise_for_status()
            msg = f'Making login authentication API call to {uri}'
            logger.info(msg)

            if r.status_code == 200:
                msg = f'Successful response received for API call to {self.fqdn}'
                logger.info(msg)
                # Return the JSON output for processing
                data = r.json()
                return data
            else:
                msg = f'API call failed to {self.fqdn}'
                logger.error(msg)
                msg = f'Response code: {str(r.status_code)}'
                logger.debug(msg)
                return 'API call failed'

        except Exception as e:
            msg = f'API call timed out trying to reach - {uri}'
            logger.error(msg)
            logger.debug(str(e))
            return 'API call failed'

    def refresh_token_api_call(self) -> str:
        """
        Making an API authentication call to the PowerProtect Data Manager server
        """

        uri = f'https://{self.fqdn}:8443/api/v2/token'
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(self.token)}
        payload = '{"refresh_token": "%s","grant_type": "refresh_token","scope": "aaa"}' % self.refresh_token

        # Logging the API call being made
        msg = f'Marking API call: {uri}'
        logger.info(msg)

        # Try to make refresh token API call to PowerProtect Data Manager
        try:
            r = requests.post(uri, data=payload, headers=headers, verify=False, timeout=glb_v.api_call_timeout)
            r.raise_for_status()
            msg = f'Making refresh token API call to {uri}'
            logger.info(msg)

            if r.status_code == 200:
                msg = f'Successful response received for API call to {self.fqdn}'
                logger.info(msg)
                # Return the JSON output for processing
                data = r.json()
                return data
            else:
                msg = f'API call failed to {self.fqdn}'
                logger.error(msg)
                msg = f'Response code: {str(r.status_code)}'
                logger.debug(msg)
                return 'API call failed'

        except Exception as e:
            msg = f'API call timed out trying to reach - {uri}'
            logger.error(msg)
            logger.debug(str(e))
            return 'API call failed'

    def get_api_call(self, uri: str, params: dict) -> str:
        """
        Making an GET API call to the PowerProtect Data Manager server
        """

        # Logging the API call being made
        msg = f'Marking GET API call: {uri}'
        logger.info(msg)

        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(self.token)}

        # Try to make an authentication API call to PowerProtect Data Manager
        try:
            if params == '':
                r = requests.get(uri, headers=headers, verify=False, timeout=glb_v.api_call_timeout)
                r.raise_for_status()
            else:
                r = requests.get(uri, headers=headers, params=params, verify=False, timeout=glb_v.api_call_timeout)
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
                return 'API call failed'

        except Exception as e:
            msg = f'API call timed out trying to reach - {uri}'
            logger.error(msg)
            logger.debug(str(e))
            return 'API call failed'

    def post_api_call(self, uri: str, payload: dict) -> str:
        """
        Making a POST API call to the PowerProtect Data Manager server
        """

        # Logging the API call being made
        msg = f'Marking POST API call: {uri}'
        logger.info(msg)

        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(self.token)}

        # Try to make an authentication API call to PowerProtect Data Manager
        try:
            r = requests.post(uri, data=payload, headers=headers, verify=False, timeout=glb_v.api_call_timeout)
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
                return 'API call failed'

        except Exception as e:
            msg = f'API call timed out trying to reach - {uri}'
            logger.error(msg)
            logger.debug(str(e))
            return 'API call failed'

    def get_protected_vms(self) -> str:
        """
        Get API call to PowerProtect Data Manager to get a list of protected VMs
        """
        # Build the URL for the API call
        uri = f'https://{self.fqdn}:8443/api/v2/assets'
        filters = 'protectionStatus eq "PROTECTED" and type eq "VMWARE_VIRTUAL_MACHINE"'
        params = {'filter': filters}

        # Making the API call and get the json response if the call is successful
        protected_vms = self.get_api_call(uri, params)
        if protected_vms != 'API call failed':
            return protected_vms
        else:
            logger.error(protected_vms)
            return 'API call failed'

    def get_asset_backups(self, asset_id: str) -> str:
        """
        Get API call to PowerProtect Data Manager to get the latest backup of a VM by asset ID
        """
        # Build the URL for the API call
        uri = f'https://{self.fqdn}:8443/api/v2/assets/{asset_id}/copies'
        params = {}

        # Making the API call and get the json response if the call is successful
        backups = self.get_api_call(uri, params)
        if backups != 'API call failed':
            return backups
        else:
            logger.error(backups)
            return 'API call failed'

    def get_asset_info(self, asset_id: str) -> str:
        """
        Get API call to PowerProtect Data Manager to get information about the asset
        """
        # Build the URL for the API call
        uri = f'https://{self.fqdn}:8443/api/v2/assets/{asset_id}'
        params = {}

        # Making the API call and get the json response if the call is successful
        asset_info = self.get_api_call(uri, params)
        if asset_info != 'API call failed':
            return asset_info
        else:
            logger.error(asset_info)
            return 'API call failed'

    def instant_access_recovery(self, payload: dict) -> str:
        """
        Post API call to PowerProtect Data Manager to start instant access recovery of VM
        """
        # Build the URL for the API call
        uri = f'https://{self.fqdn}:8443/api/v2/restored-copies'

        # Making the API call and get the json response if the call is successful
        recovery = self.post_api_call(uri, payload)
        if recovery != 'API call failed':
            return recovery
        else:
            logger.error(recovery)
            return 'API call failed'

    def cancel_instant_access_recovery(self, activity_id: str) -> str:
        """
        Post API call to PowerProtect Data Manager to cancel instant access recovery of VM
        """
        # Build the URL for the API call
        uri = f'https://{self.fqdn}:8443/api/v2/restored-copies/{activity_id}/remove'
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(self.token)}

        # Logging the API call being made
        msg = f'Marking POST API call: {uri}'
        logger.info(msg)

        # Try to make an authentication API call to PowerProtect Data Manager
        try:
            r = requests.post(uri, headers=headers, verify=False, timeout=glb_v.api_call_timeout)
            r.raise_for_status()
            msg = f'Making login authentication API call to {uri}'
            logger.info(msg)

            if r.status_code == 202:
                msg = f'Successful response received for API call'
                logger.info(msg)
                # Return the JSON output for processing
                return 'API call successful'
            else:
                msg = f'API call failed'
                logger.error(msg)
                msg = f'Response code: {str(r.status_code)}'
                logger.debug(msg)
                return 'API call failed'

        except Exception as e:
            msg = f'API call timed out trying to reach - {uri}'
            logger.error(msg)
            logger.debug(str(e))
            return 'API call failed'
