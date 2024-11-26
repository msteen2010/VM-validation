"""
This file is used create a NetWorker object

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


# Defining the class for NetWorker
class Networker(object):
    def __init__(self):
        self.fqdn = ''
        self.user = ''
        self.password = ''
        self.api_call_success = False
        self.alerts = []
        self.alerts_json = ''
        self.protected_vms_names = []
        self.protected_vms_names_href = {}
        self.protected_vms_json = ''
        self.user_vm_names = []
        self.user_vm_names_href = {}
        self.protected_vm_backups_json = ''
        self.temp_vm_latest_backup_json = ''
        self.temp_vm_latest_recovery_href = ''
        self.temp_vm_latest_recovery_json = ''
        self.recovery_job = ''
        self.proceed_with_instant_access = False

    def get_api_call(self, uri: str) -> str:
        """
        Making an API call to the NetWorker server
        """
    
        # Logging the API call being made
        msg = f'Marking API call: {uri}'
        logger.info(msg)
    
        # A timeout value of 30 seconds has been applied and if reached, allows the application to continue
        try:
            r = requests.get(uri, auth=(self.user, self.password), verify=False, timeout=glb_v.api_call_timeout)

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
    
    def post_api_call(self, uri: str, data: str) -> str:
        """
        Making an POST API call to the NetWorker server
        """
    
        # Logging the API call being made
        msg = f'Marking POST API call: {uri}'
        logger.info(msg)
    
        # A timeout value of 30 seconds has been applied and if reached, allows the application to continue
        try:
            r = requests.post(uri, auth=(self.user, self.password), json=data, verify=False,
                              timeout=glb_v.api_call_timeout)
            msg = f'Making POST API call to {uri}'
            logger.info(msg)
    
            if r.status_code == 201:
                # networker.api_call_success = True
                msg = f'Successful response received for API call to {self.fqdn}'
                logger.info(msg)
                # Return the JSON output for processing
                data = r.headers
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
    
    def post_api_cancel_job(self, uri: str, data) -> bool:
        """
        Making an POST API call to the NetWorker server to cancel a job
        """
    
        # Logging the API call being made
        msg = f'Marking POST API call: {uri}'
        logger.info(msg)
    
        # A timeout value of 30 seconds has been applied and if reached, allows the application to continue
        try:
            r = requests.post(uri, auth=(self.user, self.password), json=data, verify=False,
                              timeout=glb_v.api_call_timeout)
            msg = f'Making POST API call to {uri}'
            logger.info(msg)
    
            if r.status_code == 202:
                # networker.api_call_success = True
                msg = f'Successful response received for API call to {self.fqdn} for cancelling job'
                logger.info(msg)
                return True
    
            else:
                msg = f'API call failed to {self.fqdn}'
                logger.error(msg)
                msg = f'Response code: {str(r.status_code)}'
                logger.debug(msg)
                return False
    
        except Exception as e:
            msg = f'API call timed out trying to reach - {uri}'
            logger.error(msg)
            logger.debug(str(e))
    
    def get_alerts(self) -> str:
        """
        Get API call to the NetWorker server for list of current alerts and a good way to test the credentials
        """
        # Build the URL for the API call
        uri = 'https://' + self.fqdn + ':9090/nwrestapi/v3/global/alerts'
    
        # Making the API call and get the json response if the call is successful
        alerts_json = self.get_api_call(uri)
        if alerts_json != 'API call failed':
            return alerts_json
        else:
            return 'API call failed'
    
    def get_protected_vms(self, vcenter) -> str:
        """
        Get API call to the NetWorker server for list of protected VMs
        """
        # Build the URL for the API call
        uri = 'https://' + self.fqdn + ':9090/nwrestapi/v3/global/vmware/vcenters/' \
              + vcenter + '/protectedvms'
    
        # Making the API call and get the json response if the call is successful
        protected_vms_json = self.get_api_call(uri)
        if protected_vms_json != 'Failed':
            return protected_vms_json
        else:
            return 'API call failed'
    
    def get_protected_vm_lastest_backup(self, protected_vm_href: str):
        """
        Get API call to the NetWorker server to get the latest recovery API URL for a protected VM backup
        """
        # Build the URL for the API call
        uri = protected_vm_href + '/backups'
    
        # Making the API call and get the json response if the call is successful
        protected_vm_latest_backups_json = self.get_api_call(uri)
        if protected_vm_latest_backups_json != 'Failed':
            return protected_vm_latest_backups_json
        else:
            return 'API call failed'
