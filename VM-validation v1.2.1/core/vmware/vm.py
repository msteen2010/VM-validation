""""
This file is used to work with VMs

Written by Mike van der Steen
Version 1.00

last updated: 9 July 2023
"""

from utils import log

logger = log.custom_logger()


# Defining the class for VM
class VM(object):
    def __init__(self):
        self.name = ''
        self.id = ''
        self.ia_name = ''
        self.vm_ref = ''
        self.powered_on = False
        self.registered = False
        self.vmtools_running = False
        self.validated = False
        self.continue_validation = False
        # The following values are not to be reset in the below method
        self.total_vms_to_process = 0
        self.vm_successfully_processed = 0
        self.validation_summary = []

    def reset_values(self):
        self.name = ''
        self.id = ''
        self.ia_name = ''
        self.vm_ref = ''
        self.powered_on = False
        self.registered = False
        self.vmtools_running = False
        self.validated = False
        self.continue_validation = False