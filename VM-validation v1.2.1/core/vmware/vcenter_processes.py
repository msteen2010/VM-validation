"""
This file is used to process information from vCenter

Written by Mike van der Steen
Version 1.00

last updated: 31 July 2022
"""


from utils import log

logger = log.custom_logger()


def find_vm(data: str, vm_name: str) -> bool:
    """
    Extract information from the vCenter VM JSON response and see if a VM has been registered
    """
    try:
        for vm in data['value']:
            if vm['name'] == vm_name:
                msg = f'Found VM {vm_name}'
                logger.info(msg)
                return True

    except Exception as e:
        logger.error(f'Unable to find VM name of {vm_name} from vCenter get VM JSON response')
        logger.debug(str(e))


def find_vm_id(data: str, vm_name: str) -> str:
    """
    Extract information from the vCenter VM JSON response to extract the VM ID
    """

    try:
        for vm in data['value']:
            if vm['name'] == vm_name:
                vm_id = vm['vm']
                msg = f'Located VM {vm_name} and the ID is {vm_id}'
                logger.info(msg)
                return vm_id

    except Exception as e:
        logger.error(f'Unable to retrieve VM id for {vm_name} from vCenter get VM JSON response')
        logger.debug(str(e))


def is_vm_powered_on(data: str, vm_name: str) -> bool:
    """
    Extract information from the vCenter VM JSON response to determine if a VM is powered on
    """

    try:
        power_state = data['value']['state']
        if power_state == 'POWERED_ON':
            msg = f'VM {vm_name} powered on'
            logger.info(msg)
            return True
        else:
            return False

    except Exception as e:
        logger.error(f'Unable to retrieve VM power status for VM {vm_name} from vCenter get VM JSON response')
        logger.debug(str(e))


def is_vmtools_running(data: str, vm_name: str) -> bool:
    """
    Extract information from the vCenter VM JSON response to determine if a VMware tools is running
    """

    try:
        tools_state = data['value']['run_state']
        if tools_state == 'RUNNING':
            msg = f'VMware Tools on {vm_name} is running'
            logger.info(msg)
            return True
        else:
            return False

    except Exception as e:
        logger.error(f'Unable to retrieve the VMware tools status of VM {vm_name} form vCenter get VM JSON response')
        logger.debug(str(e))
