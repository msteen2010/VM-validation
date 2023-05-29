""""
This file is used to work with vCenter

Written by Mike van der Steen
Version 1.00

last updated: 29 December 2022
"""

from utils import log


logger = log.custom_logger()


# Defining the class for VCenter
class VCenter(object):
    def __init__(self):
        self.fqdn = ''
        self.user = ''
        self.password = ''
        self.connection_success = False
        self.vms = []
        self.smartconnect_connection = None




