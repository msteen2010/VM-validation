""""
This file is used create a NetWorker object

Written by Mike van der Steen
Version 1.00

last updated: 29 December 2022
"""

from utils import log


logger = log.custom_logger()


# Defining the class for NetWorker
class Networker(object):
    def __init__(self):
        self.fqdn = ''
        self.api_user = ''
        self.api_password = ''
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
