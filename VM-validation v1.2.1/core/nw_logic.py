#!/usr/bin/env python3
"""
This module provides the core logic of NetWorker in performing VM instant access recovery operation

author: Mike van der Steen
last updated: 31 July 2023
"""

from utils import log, task, file
from core import core_logic, vm_logic
from core.networker import nw_process_json
from utils import global_objects as glb_o
from utils import global_variables as glb_v

logger = log.custom_logger()


def extract_vm_backup_information() -> None:
    """
    NetWorker protected VMs that the user wishes to validate will be run in this function
    """

    # Create the output file that will contain an audit of the VM validation
    glb_v.output_file = file.create_datetime_file(glb_o.main_ui.directories_output_path.get(), 
                                                  '-VM validation output.txt')

    # If the protected list of VMs has not been run, get the JSON data from NetWorker before continuing
    if glb_o.nw_server.protected_vms_json == '':
        core_logic.get_list_protected_vms()
        
    # Get the latest protected list of VMs from NetWorker before continuing
    core_logic.get_list_protected_vms()

    # Clear the output screen
    glb_o.main_ui.clear_output()

    msg = f'Output of VM validation is provided in {glb_v.output_file}'
    logger.info(msg)
    file.append_datetime_prefix(glb_v.output_file, msg)
    glb_o.main_ui.append_to_output(msg, True)
    glb_o.main_ui.update()
    msg = f'NetWorker server is {glb_o.nw_server.fqdn}'
    logger.info(msg)
    file.append_datetime_prefix(glb_v.output_file, msg)
    glb_o.main_ui.append_to_output(msg, True)
    glb_o.main_ui.update()
    msg = f'vCenter server is {glb_o.vcenter_server.fqdn}'
    logger.info(msg)
    file.append_datetime_prefix(glb_v.output_file, msg)
    glb_o.main_ui.append_to_output(msg, True)
    glb_o.main_ui.update()

    # Extract the protected VMs and the href reference from NetWorker and store it in a dictionary
    glb_o.nw_server.protected_vms_names_href = \
        nw_process_json.get_protected_vms_href(glb_o.nw_server.protected_vms_json)

    # Get the list of user defined VMs from the text file as specified in the UI
    glb_o.nw_server.user_vm_names = file.create_list(glb_o.main_ui.directories_vm_path.get())

    # Filter the list of VMs and the href references based on the user VM list
    glb_o.nw_server.user_vm_names_href = task.compare_dict_with_list_inclusion(glb_o.nw_server.protected_vms_names_href,
                                                                               glb_o.nw_server.user_vm_names)
    glb_o.vm.total_vms_to_process = len(glb_o.nw_server.user_vm_names_href)
    glb_o.main_ui.progress_total_vms_amount.configure(text=glb_o.vm.total_vms_to_process)
    msg = f'The total number of VMs to validate is: {glb_o.vm.total_vms_to_process}'
    logger.info(msg)
    file.append_datetime_prefix(glb_v.output_file, msg)
    glb_o.main_ui.append_to_output(msg, True)
    glb_o.main_ui.update()

    # Get the list of VMs in user defined list that are not protected by NetWorker
    uncommon_vms = task.compare_list_with_dict_exclusion(glb_o.nw_server.user_vm_names,
                                                         glb_o.nw_server.protected_vms_names_href)
    for vm_ref in uncommon_vms:
        msg = f'VM {vm_ref} in User Defined VM List was not found in the backup server protected VM list ' \
              f'and skipping VM validation.'
        glb_o.main_ui.append_to_output(msg, True)


def process_each_vm_via_instant_access() -> None:
    """
    Process each VM by performing an instant access recovery and see if VM tools starts
    """

    # Reset these values before the VM validation proceeds
    glb_o.vm.vm_successfully_processed = 0
    glb_o.vm.validation_summary = []

    # Process each user listed VM for backup validation where the vm_name is a reference to the VM
    for vm_name, vm_ref in glb_o.nw_server.user_vm_names_href.items():
        # Resetting the VM instance variables before proceeding with the VM validation
        glb_o.vm.reset_values()
        glb_o.vm.name = vm_name
        glb_o.vm.vm_ref = vm_ref
        glb_o.vm.ia_name = f'{glb_o.vm.name}_ia'

        # Connect to vCenter to see a VM with the same name as the Instant Access VM exists already
        msg = f'{glb_o.vm.name} - Checking if VM {glb_o.vm.ia_name} already exists in vCenter'
        logger.info(msg)
        file.append_datetime_prefix(glb_v.output_file, msg)
        file.append_datetime_prefix(glb_v.output_file, msg)
        glb_o.main_ui.append_to_output(msg, True)
        glb_o.main_ui.update()
        response = vm_logic.does_vm_exist(glb_o.vm.ia_name)
        if response:
            msg = f'{glb_o.vm.name} - VM with the name of {glb_o.vm.ia_name} already exists in vCenter and the ' \
                  f'validation of this VM cannot continue'
            logger.info(msg)
            file.append_datetime_prefix(glb_v.output_file, msg)
            glb_o.main_ui.append_to_output(msg, True)
            glb_o.main_ui.update()
            glb_o.vm.continue_validation = False
        else:
            msg = f'{glb_o.vm.name} - VM with the name {glb_o.vm.ia_name} does not exist in vCenter and ' \
                  f'continuing with the VM validation process'
            logger.info(msg)
            file.append_datetime_prefix(glb_v.output_file, msg)
            glb_o.main_ui.append_to_output(msg, True)
            glb_o.main_ui.update()
            glb_o.vm.continue_validation = True

        # If a VM with the instant access name does not exist, proceed with Instant Recovery VM validation
        if glb_o.vm.continue_validation:

            # Get the latest backups for each user listed VM as JSON response
            glb_o.nw_server.temp_vm_latest_backup_json = \
                glb_o.nw_server.get_protected_vm_lastest_backup(glb_o.vm.vm_ref)
            
            # Refresh the access token for vCenter
            glb_o.vcenter_server.authenticate_api_call()

            msg = f'{glb_o.vm.name} - Processing VM for validation'
            logger.info(msg)
            msg = f'The VM asset ID is {glb_o.vm.vm_ref}'
            logger.info(msg)

            # Process the JSON data for the latest backup and extract the recovery URL
            glb_o.nw_server.temp_vm_latest_recovery_href = \
                nw_process_json.get_protected_vms_latest_backup_href(glb_o.nw_server.temp_vm_latest_backup_json)

            # Get the available recovery details for the latest backup href in the form of a JSON response
            glb_o.nw_server.temp_vm_latest_recovery_json = \
                glb_o.nw_server.get_api_call(glb_o.nw_server.temp_vm_latest_recovery_href)

            if glb_o.nw_server.temp_vm_latest_recovery_json != 'API call failed':
                msg = f'{glb_o.vm.name} - Obtained the latest VM backup JSON response from the API call'
                logger.info(msg)
                glb_o.vm.continue_validation = True
            else:
                msg = f'{glb_o.vm.name} - Failed to get the latest VM backup JSON response from the API call, ' \
                      f'unable to proceed further and skipping the VM validation'
                logger.info(msg)
                file.append_datetime_prefix(glb_v.output_file, msg)
                glb_o.main_ui.append_to_output(msg, True)
                glb_o.main_ui.update()
                glb_o.vm.continue_validation = False

        # Proceed with instant access if the required JSON response was received from NetWorker
        if glb_o.vm.continue_validation:

            # Process the latest VM recovery href response to extract the URL and data required for instant access
            vm_restore_link, json_data = \
                nw_process_json.get_instant_access_restore_link(glb_o.nw_server.temp_vm_latest_recovery_json)

            if glb_o.nw_server.temp_vm_latest_recovery_json != 'API call failed':
                glb_o.vm.ia_name = json_data['vmName']
                msg = f'{glb_o.vm.name} - Recovery URL endpoint is {vm_restore_link}'
                logger.info(msg)
                file.append_datetime_prefix(glb_v.output_file, msg)
                msg = f'{glb_o.vm.name} - JSON data package is {json_data}'
                logger.info(msg)
                file.append_datetime_prefix(glb_v.output_file, msg)
                msg = f'{glb_o.vm.name} - Performing Instant Access Recovery of VM with the name of {glb_o.vm.ia_name}'
                logger.info(msg)
                file.append_datetime_prefix(glb_v.output_file, msg)
                glb_o.main_ui.append_to_output(msg, True)
                glb_o.main_ui.update()
                glb_o.vm.continue_validation = True
            else:
                msg = f'{glb_o.vm.name} - Failed to get the VM instant access restore link from the API call, ' \
                      f'unable to proceed further and skipping the VM validation'
                logger.info(msg)
                file.append_datetime_prefix(glb_v.output_file, msg)
                glb_o.main_ui.append_to_output(msg, True)
                glb_o.main_ui.update()
                glb_o.vm.continue_validation = False

            # Start the Instant Access recovery using the vm_restore_link and json_data information
            response = glb_o.nw_server.post_api_call(vm_restore_link, json_data)

            if response != 'API call failed':
                msg = f'{glb_o.vm.name} - Instant Access recovery request is being processed'
                logger.info(msg)
                file.append_datetime_prefix(glb_v.output_file, msg)
                glb_o.main_ui.append_to_output(msg, True)
                glb_o.main_ui.update()
                glb_o.nw_server.recovery_job = response['Location']
                msg = f'{glb_o.vm.name} - NetWorker job reference: {glb_o.nw_server.recovery_job}'
                logger.info(msg)
                file.append_datetime_prefix(glb_v.output_file, msg)
                glb_o.main_ui.append_to_output(msg, True)
                glb_o.main_ui.update()
                glb_o.vm.continue_validation = True
            else:
                msg = f'{glb_o.vm.name} - Failed to process the Instant Access recovery request, ' \
                      f'unable to proceed further and skipping the VM validation'
                logger.info(msg)
                file.append_datetime_prefix(glb_v.output_file, msg)
                glb_o.main_ui.append_to_output(msg, True)
                glb_o.main_ui.update()
                glb_o.vm.continue_validation = False
        # Check the registration, power and vmtools status of the Instant Access VM
        if glb_o.vm.continue_validation:
            glb_o.vm.vmtools_running = vm_logic.vm_state_checks(glb_o.vm.name, glb_o.vm.ia_name)

        # Cancel the Instant Access recovery job in PowerProtect Data Manager
        if glb_o.vm.continue_validation:
            # Cancel the Instant Access recovery job in NetWorker
            cancel_recovery_url = f'{glb_o.nw_server.recovery_job}/op/cancel'
            data = {}
            job_status = glb_o.nw_server.post_api_cancel_job(cancel_recovery_url, data)

            glb_o.main_ui.after(3000)
            if response != 'API call failed':
                if job_status:
                    msg = f'{glb_o.vm.name} - Stopping the instant access recovery session'
                    logger.info(msg)
                    file.append_datetime_prefix(glb_v.output_file, msg)
                    glb_o.main_ui.append_to_output(msg, True)
                    glb_o.main_ui.update()
                else:
                    msg = f'{glb_o.vm.name} - An error occurred trying to stop the instant access recovery. ' \
                          f'You may need to remove the VM {glb_o.vm.ia_name} manually from vCenter ' \
                          f'{glb_o.vcenter_server.fqdn}'
                    logger.info(msg)
                    file.append_datetime_prefix(glb_v.output_file, msg)
                    glb_o.main_ui.append_to_output(msg, True)
                    glb_o.main_ui.update()
            else:
                msg = f'{glb_o.vm.name} - Post API call to cancel the instant access recovery for ' \
                      f'{glb_o.vm.ia_name} failed. Review the debug log file that is located in the log directory ' \
                      f'where this utility is run from.'
                logger.info(msg)
                glb_o.main_ui.append_to_output(msg, True)

        if not glb_o.vm.continue_validation:
            msg = f'{glb_o.vm.name} - Skipping validation of this VM and moving onto the next VM. ' \
                  f'See logs for more detail as to why VM validation was skipped.'
            logger.info(msg)
            file.append_datetime_prefix(glb_v.output_file, msg)
            glb_o.main_ui.append_to_output(msg, True)
            glb_o.main_ui.update()
