"""
listed some global variables that will be referenced by multiple modules
These will be defined as objects once initiated by each relevant module

author: Mike van der Steen
last updated: 31 July 2023
"""

import os

from utils import log
from utils.file import read_config_file_int

logger = log.custom_logger()

# Get the current working directory and location of config.ini file
directory = os.getcwd()
fullpath = os.path.join(directory, 'config.ini')

"""
Timeout values related to VMware activities
"""

# The registered_vm_delay is the wait time for vCenter to fully register a VM - suggested value is 10 seconds
response = read_config_file_int(fullpath, 'timeout', 'registered_vm_delay')
if response != -99999:
    registered_vm_delay = response
else:
    registered_vm_delay = 10
    msg = f'Failed to read registration of VM value, setting the value of {registered_vm_delay}'
    logger.info(msg)

# The vm_registration_timeout is the wait time for a VM to be registered with vCenter - suggested value is 60 seconds
response = read_config_file_int(fullpath, 'timeout', 'vm_registration_timeout')
if response != -99999:
    vm_registration_timeout = response
else:
    vm_registration_timeout = 60
    msg = f'Failed to read timeout value for registration of VM value, setting the value to {vm_registration_timeout}'
    logger.info(msg)

# The vm_powerup_timeout is the wait time for a VM to power up - recommended value is 60 seconds
response = read_config_file_int(fullpath, 'timeout', 'vm_powerup_timeout')
if response != -99999:
    vm_powerup_timeout = response
else:
    vm_powerup_timeout = 60
    msg = f'Failed to read the timeout value for VM powering up, setting the value to {vm_powerup_timeout}'
    logger.info(msg)

# The vmtools_startup_timeout is the wait time for a VMtools to start in the VM - suggested value is 600 seconds
response = read_config_file_int(fullpath, 'timeout', 'vmtools_startup_timeout')
if response != -99999:
    vmtools_startup_timeout = response
else:
    vmtools_startup_timeout = 600
    msg = f'Failed to read the timeout value for VM tools starting, setting the value to {vmtools_startup_timeout}'
    logger.info(msg)

"""
Timeout values related to API processing
"""

# The api_call_timeout is the wait time for an API call - suggested value is 30 lines
response = read_config_file_int(fullpath, 'api', 'api_call_timeout')
if response != -99999:
    api_call_timeout = response
else:
    api_call_timeout = 30
    msg = f'Failed to read the timeout value for an API call, setting the value to {api_call_timeout}'
    logger.info(msg)

"""
Values used by the GUI
"""

# The number of lines to be shown in the GUI textbox section - suggested value is 25
response = read_config_file_int(fullpath, 'gui', 'number_of_lines')
if response != -99999:
    number_of_lines = response
    msg = f'The number of lines to be shown in the GUI textbox section from the config.ini file is {response}'
    logger.info(msg)
else:
    number_of_lines = 25
    msg = f'Failed to read the number of lines for the GUI textbox section, setting the value to {number_of_lines}'
    logger.info(msg)

"""
# Other global variables that will have their values assigned when the utility is running
"""

backup_server_fqdn = ''
backup_server_type = ''
output_file = ''
