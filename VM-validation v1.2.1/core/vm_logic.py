#!/usr/bin/env python3
"""
This module provides the core logic for VM related checks

author: Mike van der Steen
last updated: 31 July 2023
"""

from utils import log, file
from core.vmware import vcenter_processes
from utils import global_objects as glb_o
from utils import global_variables as glb_v

logger = log.custom_logger()


def verify_vm_registration(vm, ia_vm: str) -> bool:
    """
    Communicate with vCenter to check the stat of the Instant Access VM
    """

    # Run through a number of iterations based on the value of the timeout
    for number in range(0, glb_v.vm_registration_timeout):
        # Get the JSON response from vCenter to find registered VM
        response = glb_o.vcenter_server.get_vms()
        vm_present = vcenter_processes.find_vm(response, ia_vm)

        if vm_present:
            glb_o.main_ui.append_to_output('\n', False)
            glb_o.main_ui.update()
            msg = f'{vm} - {ia_vm} is registered with vCenter'
            logger.info(msg)
            file.append_datetime_prefix(glb_v.output_file, msg)
            glb_o.main_ui.append_to_output(msg, True)
            glb_o.main_ui.update()
            return True

        else:
            msg = '*'
            # Increment the attempts and wait for up to 1 second before continuing
            glb_o.main_ui.after(1000, glb_o.main_ui.append_to_output(msg, False))
            glb_o.main_ui.update()

    # The timeout value has been reached
    glb_o.main_ui.append_to_output('\n', False)
    glb_o.main_ui.update()
    msg = f'{vm} - Waiting for VM {ia_vm} to be registered with vCenter, but ' \
          f'timed out after {glb_v.vm_registration_timeout} seconds'
    logger.info(msg)
    file.append_datetime_prefix(glb_v.output_file, msg)
    glb_o.main_ui.append_to_output(msg, True)
    glb_o.main_ui.update()
    return False


def does_vm_exist(vm: str) -> bool:
    """
    Communicate with vCenter to check for the existence of a VM
    """

    # Get the JSON response from vCenter to find registered VM
    response = glb_o.vcenter_server.get_vms()
    vm_present = vcenter_processes.find_vm(response, vm)

    if vm_present:
        msg = f'VM with the name of {vm} exists in with vCenter'
        logger.info(msg)
        return True

    if not vm_present:
        msg = f'VM with the name of {vm} does not exist in with vCenter'
        logger.info(msg)
        return False


def is_vm_powered_on(vm, ia_vm: str, vm_id: str) -> bool:
    """
    Communicate with vCenter to check the power state of the Instant Access VM
    """

    # Get the JSON response from vCenter to find the power state of a VM
    response = glb_o.vcenter_server.get_vm_power_status(vm_id)
    power_state = vcenter_processes.is_vm_powered_on(response, ia_vm)

    if not power_state:
        msg = f'{vm} - VM {ia_vm} is currently powered off'
        logger.info(msg)
        file.append_datetime_prefix(glb_v.output_file, msg)
        glb_o.main_ui.append_to_output(msg, True)
        glb_o.main_ui.update()
        # powering on the VM
        glb_o.vcenter_server.power_on_vm(vm_id)
        msg = f'{vm} - Attempting to power on {ia_vm} '
        logger.info(msg)
        file.append_datetime_prefix(glb_v.output_file, msg)
        glb_o.main_ui.append_to_output(msg, False)
        glb_o.main_ui.update()

    # Run through a number of iterations based on the value of the timeout
    for number in range(0, glb_v.vm_powerup_timeout):
        # Increment the attempts and wait for up to 1 second before continuing
        msg = '*'
        glb_o.main_ui.after(1000, glb_o.main_ui.append_to_output(msg, False))
        glb_o.main_ui.update()
        glb_o.vcenter_server.power_on_vm(vm_id)
        response = glb_o.vcenter_server.get_vm_power_status(vm_id)
        power_state = vcenter_processes.is_vm_powered_on(response, ia_vm)

        # checking if the VM is now powered on
        if power_state:
            glb_o.main_ui.append_to_output('\n', False)
            glb_o.main_ui.update()
            msg = f'{vm} - {ia_vm} is powered on'
            logger.info(msg)
            file.append_datetime_prefix(glb_v.output_file, msg)
            glb_o.main_ui.append_to_output(msg, True)
            glb_o.main_ui.update()
            return True

    # The timeout value has been reached
    glb_o.main_ui.append_to_output('\n', False)
    glb_o.main_ui.update()
    msg = f'{vm} - Waiting for {ia_vm} to power on, but timed out after {glb_v.vm_powerup_timeout} seconds'
    logger.info(msg)
    file.append_datetime_prefix(glb_v.output_file, msg)
    glb_o.main_ui.append_to_output(msg, True)
    glb_o.main_ui.update()
    return False


def is_vmtools_running(vm: str, ia_vm: str, vm_id: str) -> bool:
    """
    Communicate with vCenter to check the stat of the Instant Access VM
    """

    # Run through a number of iterations based on the value of the timeout
    for number in range(1, glb_v.vmtools_startup_timeout):
        # Get the JSON response from vCenter to find the status of VMware Tools of a VM
        response = glb_o.vcenter_server.get_vm_vmtools_status(vm_id)
        vm_tools_running = vcenter_processes.is_vmtools_running(response, ia_vm)

        if not vm_tools_running:
            msg = '*'
            # Increment the attempts and wait for up to 1 second before continuing
            glb_o.main_ui.after(1000, glb_o.main_ui.append_to_output(msg, False))
            glb_o.main_ui.update()

        if vm_tools_running:
            glb_o.main_ui.append_to_output('\n', False)
            glb_o.main_ui.update()
            msg = f'{vm} - VMware Tools is running on {ia_vm}'
            logger.info(msg)
            file.append_datetime_prefix(glb_v.output_file, msg)
            glb_o.main_ui.append_to_output(msg, True)
            glb_o.main_ui.update()
            return True

    # The timeout value has been reached
    glb_o.main_ui.append_to_output('\n', False)
    glb_o.main_ui.update()
    msg = f'{vm} - Waiting for VMware Tools to start on {ia_vm}, but timed out after ' \
          f'{glb_v.vmtools_startup_timeout} seconds'
    logger.info(msg)
    file.append_datetime_prefix(glb_v.output_file, msg)
    glb_o.main_ui.append_to_output(msg, True)
    glb_o.main_ui.update()
    return False


def vm_state_checks(vm: str, ia_vm: str) -> bool:
    """
    Communicate with vCenter to check the state of the Instant Access VM
    """

    # Connect to vCenter to see if the Instant Access VM has been configured within vCenter
    if glb_o.vm.continue_validation:
        msg = f'{vm} - Checking if VM {ia_vm} registered with the vCenter '
        logger.info(msg)
        file.append_datetime_prefix(glb_v.output_file, msg)
        glb_o.main_ui.append_to_output(msg, False)
        glb_o.main_ui.update()
        response = verify_vm_registration(vm, ia_vm)
        if response:
            msg = f'{vm} - {ia_vm} registered with vCenter'
            logger.info(msg)
            glb_o.vm.continue_validation = True

            # Going to allow vCenter some additional time to finalize the configuration
            msg = f'{vm} - Allowing some additional time for vCenter to finalize configuration of {ia_vm} '
            logger.info(msg)
            file.append_datetime_prefix(glb_v.output_file, msg)
            glb_o.main_ui.append_to_output(msg, False)
            glb_o.main_ui.update()

            # Run through a number of iterations based on the value of the timeout
            for number in range(0, glb_v.registered_vm_delay):
                msg = '*'
                # Increment the attempts and wait for up to 1 second before continuing
                glb_o.main_ui.after(1000, glb_o.main_ui.append_to_output(msg, False))
                glb_o.main_ui.update()
            msg = ' '
            glb_o.main_ui.append_to_output(msg, True)
            glb_o.main_ui.update()
        else:
            msg = f'{vm} - VM {ia_vm} failed to be registered with vCenter'
            logger.info(msg)
            file.append_datetime_prefix(glb_v.output_file, msg)
            glb_o.main_ui.append_to_output(msg, True)
            glb_o.main_ui.update()
            glb_o.vm.continue_validation = False
            return False

    # Get the VM ID from vCenter for the instant access VM
    if glb_o.vm.continue_validation:
        msg = f'{vm} - Getting the VM ID for VM {ia_vm}'
        logger.info(msg)
        response = glb_o.vcenter_server.get_vms()
        if response != 'API call failed':
            msg = f'{vm} - Successfully obtained the VM ID for {ia_vm}'
            logger.info(msg)
            glb_o.vm.id = vcenter_processes.find_vm_id(response, ia_vm)
            glb_o.vm.continue_validation = True
        else:
            msg = f'{vm} - Failed to locate the VM ID from vCenter. ' \
                  f'The Instant Access VM will need to be powered on manually for the validation to continue.'
            logger.info(msg)
            glb_o.main_ui.update()
            return False

    # Connect to vCenter to see if the Instant Access VM has been powered on
    if glb_o.vm.continue_validation:
        msg = f'{vm} - Getting power state of VM {ia_vm}'
        logger.info(msg)
        file.append_datetime_prefix(glb_v.output_file, msg)
        glb_o.main_ui.append_to_output(msg, True)
        glb_o.main_ui.update()
        response = is_vm_powered_on(vm, ia_vm, glb_o.vm.id)
        if response:
            msg = f'{vm} - VM {ia_vm} is powered on'
            logger.info(msg)
            glb_o.vm.continue_validation = True
        else:
            msg = f'{vm} - Failed to power on VM {ia_vm}'
            logger.info(msg)
            file.append_datetime_prefix(glb_v.output_file, msg)
            glb_o.main_ui.append_to_output(msg, True)
            glb_o.main_ui.update()
            return False

    # Connect to vCenter to see if the VMware tools is running on the VM
    if glb_o.vm.continue_validation:
        msg = f'{vm} - Checking the status of VMware tools on VM {ia_vm} '
        logger.info(msg)
        file.append_datetime_prefix(glb_v.output_file, msg)
        glb_o.main_ui.append_to_output(msg, False)
        glb_o.main_ui.update()
        response = is_vmtools_running(vm, ia_vm, glb_o.vm.id)
        if response:
            file.append_datetime_prefix(glb_v.output_file, msg)
            glb_o.main_ui.append_to_output(msg, True)
            msg = f'{vm} - VM validation of the latest backup is deemed successful as VM Tools is running'
            logger.info(msg)
            file.append_datetime_prefix(glb_v.output_file, msg)
            glb_o.main_ui.append_to_output(msg, True)
            glb_o.main_ui.update()
            glb_o.vm.vm_successfully_processed += 1
            glb_o.main_ui.progressed_vms_amount.config(text=glb_o.vm.vm_successfully_processed)
            glb_o.vm.validation_summary.append(f'{vm} - Validation Successful')
            glb_o.vm.vmtools_running = True
            return True
        else:
            msg = f'{vm} - VM validation of {ia_vm} instant recovery failed as VMware Tools failed to start'
            logger.info(msg)
            file.append_datetime_prefix(glb_v.output_file, msg)
            glb_o.main_ui.append_to_output(msg, True)
            msg = f'{vm} - Check the status of VMtools on {vm} and install VMtools if ' \
                  f'possible, this will allow VM validation to be run in future tests. ' \
                  f'Alternatively, you may need to manually validate VM.'
            logger.info(msg)
            file.append_datetime_prefix(glb_v.output_file, msg)
            glb_o.main_ui.append_to_output(msg, True)
            glb_o.main_ui.update()
            glb_o.vm.validation_summary.append(f'{vm} - Validation Failed')
            glb_o.vm.continue_validation = False
            glb_o.vm.vmtools_running = False
            return False
