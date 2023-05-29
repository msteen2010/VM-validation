"""
listed some global variables that will be referenced by multiple modules
These will be defined as objects once initiated by each relevant module
"""

import os

from core.networker import nw
from core.ppdm import ppdm
from core.vmware import vcenter
from gui import gui
from utils.file import read_config_file_int


# Create a single NetWorker server object that can be referenced by multiple modules
nw_server = nw.Networker()

# Create a single PowerProtect Data Manager server object that can be referenced by multiple modules
ppdm_server = ppdm.PowerProtectDataManager()

# Create a single vCenter server object that can be referenced by multiple modules
vcenter_server = vcenter.VCenter()

# Create the main UI object
main_ui = gui.MainWindow()

# Timeout values for VMware related activities
directory = os.getcwd()
fullpath = os.path.join(directory, 'config.ini')
registered_vm_delay = read_config_file_int(fullpath, 'timeout', 'registered_vm_delay')
vm_registration_timeout = read_config_file_int(fullpath, 'timeout', 'vm_registration_timeout')
vm_powerup_timeout = read_config_file_int(fullpath, 'timeout', 'vm_powerup_timeout')
vmtools_startup_timeout = read_config_file_int(fullpath, 'timeout', 'vmtools_startup_timeout')
api_call_timeout = read_config_file_int(fullpath, 'api', 'api_call_timeout')
page_size = read_config_file_int(fullpath, 'api', 'page_size')


# Other global variables that will have their values assigned when the utility is running
output_file = None


