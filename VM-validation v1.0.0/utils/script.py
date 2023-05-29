""""
This file is used for introduction and ending of script

Written by Mike van der Steen
Version 1.00

last updated: 31 December 2022
"""


from utils import log
from utils import globals as glb

logger = log.custom_logger()


# Welcome to the script
def welcome():
    msg = 'Welcome to the VM validation script for NetWorker (NW) and PowerProtect Data Manager (PPDM).\n' \
          '\n' \
          'This script takes the provided credentials for either a NW or PPDM backup server, performs\n' \
          'VM Instant Access recovery based on a list of VMs provided in a text file and then powers on\n' \
          'the VM from vCenter and monitors the status of VMtools until it is running.\n' \
          '\n' \
          'This script requires the following information:\n' \
          '1. Credentials for the backup server, be it NW or PPDM\n' \
          '2. Credentials for the VMware vCenter server\n' \
          '3. A text file with a list of VMs to be validated\n' \
          '\n' \
          'Please note that VMtools must be installed on the VM for the validation to be completed.\n'
    glb.main_ui.write_to_output(msg)
