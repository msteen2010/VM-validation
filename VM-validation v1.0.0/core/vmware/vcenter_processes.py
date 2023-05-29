""""
This file is used to process information from vCenter

Written by Mike van der Steen
Version 1.00

last updated: 29 December 2022
"""

from pyVim.connect import SmartConnect

from utils import log
from utils import globals as glb


logger = log.custom_logger()


def validation_credentials(vcenter: object) -> bool:
    """
    Using the provided credentials, verify if a connection can be established
    """

    try:
        # Try to make a connection to vCenter
        vcenter.smartconnect_connection = SmartConnect(host=vcenter.fqdn, user=vcenter.user, pwd=vcenter.password)
        msg = 'Connection to vCenter is successful'
        logger.info(msg)
        return True

    except Exception as e:
        msg = 'The vCenter server credentials and/or FQDN provided are not correct.\n' \
              'Please check that the correct information has been provided for vCenter.'
        logger.error(msg)
        glb.main_ui.append_to_output(msg, True)
        logger.error(str(e))
        glb.main_ui.append_to_output(msg, True)
        return False


def find_vm(vcenter: object, vm_name: str) -> bool:
    """
    Find a VM within a specific vCenter
    """

    datacenter = vcenter.smartconnect_connection.content.rootFolder.childEntity[0]
    vms = datacenter.vmFolder.childEntity

    for vm in vms:
        if vm.name == vm_name:
            msg = f'Located VM {vm.name}'
            logger.info(msg)
            return True


def is_vm_powered_on(vcenter: object, vm_name: str) -> bool:
    """
    Find a VM within a specific vCenter
    """

    datacenter = vcenter.smartconnect_connection.content.rootFolder.childEntity[0]
    vms = datacenter.vmFolder.childEntity

    for vm in vms:
        if vm.name == vm_name and vm.runtime.powerState == 'poweredOn':
            msg = f'VM {vm.name} is powered on VM'
            logger.info(msg)
            return True
        elif vm.name == vm_name and vm.runtime.powerState == 'poweredOff':
            msg = f'VM is powered off'
            logger.info(msg)
            return False


def power_on_vm(vcenter: object, vm_name: str) -> bool:
    """
    Find a VM within a specific vCenter
    """

    datacenter = vcenter.smartconnect_connection.content.rootFolder.childEntity[0]
    vms = datacenter.vmFolder.childEntity

    for vm in vms:
        if vm.name == vm_name and vm.runtime.powerState == 'poweredOn':
            msg = f'VM {vm.name} is powered on VM'
            logger.info(msg)
            return True
        elif vm.name == vm_name and vm.runtime.powerState == 'poweredOff':
            msg = f'VM is being powered on'
            logger.info(msg)
            vm.PowerOn()
            return False


def vm_tools_status(vcenter: object, vm_name: str) -> bool:
    """
    Check the status of VMtools for a particular VM
    """

    datacenter = vcenter.smartconnect_connection.content.rootFolder.childEntity[0]
    vms = datacenter.vmFolder.childEntity

    for vm in vms:
        if vm.name == vm_name:
            return vm.summary.guest.toolsStatus

