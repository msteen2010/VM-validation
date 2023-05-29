""""
This file is used create a PowerProtect Data Manager object

Written by Mike van der Steen
Version 1.00

last updated: 29 December 2022
"""

from utils import log


logger = log.custom_logger()


# Defining the class for PowerProtect Data Manager
class PowerProtectDataManager(object):
    def __init__(self):
        self.fqdn = ''
        self.api_user = ''
        self.api_password = ''
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


