"""
This file is the vCenter class and used to make APIs to vCenter

author: Mike van der Steen
last updated: 31 July 2023
"""

import requests
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

from utils import log
from utils import global_variables as glb_v

disable_warnings(InsecureRequestWarning)
logger = log.custom_logger()


# Defining the class for VCenter
class VCenter(object):
    def __init__(self):
        self.fqdn = ''
        self.user = ''
        self.password = ''
        self.token = ''
        self.connection_success = False

    def authenticate_api_call(self) -> str:
        """
        Make an API authentication call to vCenter
        """

        uri = f'https://{self.fqdn}/rest/com/vmware/cis/session'

        # Logging the API call being made
        msg = f'Marking API call: {uri}'
        logger.info(msg)

        # Try to make an authentication API call to PowerProtect Data Manager
        try:
            r = requests.post(uri, auth=(self.user, self.password), verify=False, timeout=glb_v.api_call_timeout)
            r.raise_for_status()
            msg = f'Making login authentication API call to {uri}'
            logger.info(msg)

            if r.status_code == 200:
                msg = f'Successful response received for API call to {self.fqdn}'
                logger.info(msg)
                # Return the JSON output for processing
                data = r.json()
                # Grabbing the authentication value (vmware-api-session-id) from the response
                self.token = data['value']

                return 'API call successful'
            else:
                msg = f'Response code: {str(r.status_code)}'
                logger.debug(msg)
                return 'API call failed'

        except Exception as e:
            msg = f'API call timed out trying to reach - {uri}'
            logger.error(msg)
            logger.debug(str(e))
            return 'API call failed'

    def get_api_call(self, uri: str) -> str:
        """
        Make a GET API call to vCenter
        """

        headers = {'vmware-api-session-id': '{}'.format(self.token)}

        # Try to make the API call to vCenter
        try:
            r = requests.get(uri, headers=headers, verify=False, timeout=glb_v.api_call_timeout)
            r.raise_for_status()

            if r.status_code == 200:
                # Return the JSON output for processing
                data = r.json()
                return data
            else:
                msg = f'API call failed to {uri}'
                logger.error(msg)
                msg = f'Response code: {str(r.status_code)}'
                logger.debug(msg)
                return 'API call failed'

        except Exception as e:
            msg = f'API call timed out trying to reach - {uri}'
            logger.error(msg)
            logger.debug(str(e))
            return 'API call failed'

    def post_api_call(self, uri: str) -> str:
        """
        Make a POST API call to vCenter
        """

        headers = {'vmware-api-session-id': '{}'.format(self.token)}

        # Try to make the API call to vCenter
        try:
            r = requests.post(uri, headers=headers, verify=False, timeout=glb_v.api_call_timeout)
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
                return 'API call failed'

        except Exception as e:
            msg = f'API call timed out trying to reach - {uri}'
            logger.error(msg)
            logger.debug(str(e))
            return 'API call failed'

    def get_datacenter_json(self) -> str:
        """
        GET API call to get the datacenterMoref value
        """

        uri = f'https://{self.fqdn}/rest/vcenter/datacenter'

        response = self.get_api_call(uri)
        return response

    def get_clusters_json(self) -> str:
        """
        GET API call to get the datacenterMoref value
        """

        uri = f'https://{self.fqdn}/rest/vcenter/cluster'

        response = self.get_api_call(uri)
        return response

    def get_vms(self) -> str:
        """
        GET API call to get the list of all VMs
        """

        uri = f'https://{self.fqdn}/rest/vcenter/vm'

        response = self.get_api_call(uri)
        return response

    def get_vm_power_status(self, vm_id: str) -> str:
        """
        GET API call to get the power status of a particular VM
        """

        uri = f'https://{self.fqdn}/rest/vcenter/vm/{vm_id}/power'

        response = self.get_api_call(uri)
        return response

    def get_vm_vmtools_status(self, vm_id: str) -> str:
        """
        GET API call to get the VM tools status of a particular VM
        """

        uri = f'https://{self.fqdn}/rest/vcenter/vm/{vm_id}/tools'

        response = self.get_api_call(uri)
        return response

    def power_on_vm(self, vm_id: str) -> str:
        """
        POST API call to power on a particular VM
        """

        uri = f'https://{self.fqdn}/rest/vcenter/vm/{vm_id}/power/start'

        response = self.post_api_call(uri)
        return response
