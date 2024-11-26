"""
listed some global variables that will be referenced by multiple modules
These will be defined as objects once initiated by each relevant module

author: Mike van der Steen
last updated: 31 July 2023
"""

from core.networker import nw
from core.ppdm import ppdm
from core.vmware import vcenter, vm
from gui import gui


# Create an instance of the main UI object
main_ui = gui.MainWindow()
# Create an instance of the NetWorker server object that can be referenced by multiple modules
nw_server = nw.Networker()
# Create an instance of the PowerProtect Data Manager server object that can be referenced by multiple modules
ppdm_server = ppdm.PowerProtectDataManager()
# Create an instance of the vCenter server object that can be referenced by multiple modules
vcenter_server = vcenter.VCenter()
# Create an instance of a VM
vm = vm.VM()
