"""
This file is used for introduction and ending of script

author: Mike van der Steen
last updated: 31 July 2023
"""


from utils import log
from utils import global_objects as glb

logger = log.custom_logger()


# Welcome to the script
def welcome():
    msg = 'Welcome to the VM image backup validation utility.\n' \
          '\n'\
          'This utility currently supports NetWorker (NW) and PowerProtect Data Manager (PPDM) backup applications. ' \
          'Credentials for both the backup server and vCenter are required to validate VM backups and is performed ' \
          'through VM Instant Access recovery of the latest VM backup for VMs provided in a list. The VM is then ' \
          'powered on through vCenter or by the backup recovery process and the utility will monitor the status of ' \
          'VMtools until it is running.\n' \
          '\n' \
          'This utility will determine if a backup of a VM in valid if the VMtools is running during the instant ' \
          'access recovery.\n' \
          '\n' \
          'This utility requires the following information:\n' \
          '1. Credentials for the backup server with an account that has recovery permission.\n' \
          '2. Credentials for the VMware vCenter server with an account that has read only role, plus power on VM.\n' \
          '3. A text file with a list of VMs to be validated.\n' \
          '\n' \
          'Please note that VMtools must be installed on the VM for the validation to be completed.\n'
    glb.main_ui.write_to_output(msg)
