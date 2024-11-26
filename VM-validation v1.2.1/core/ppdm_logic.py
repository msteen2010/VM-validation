#!/usr/bin/env python3
"""
This module provides the core logic for PowerProtect Data Manager instant recovery of VM

author: Mike van der Steen
last updated: 31 July 2023
"""

from utils import log, task, file
from core import core_logic, vm_logic
from core.ppdm import ppdm_process_json
from utils import global_objects as glb_o
from utils import global_variables as glb_v

logger = log.custom_logger()


def extract_vm_backup_information() -> None:
    """
    PowerProtect Data Manager protected VMs that the user wishes to validate will be run in this function
    """

    # Refresh the access token
    ppdm_response = glb_o.ppdm_server.refresh_token_api_call()
    
    glb_o.ppdm_server.token = ppdm_response['access_token']

    # If the protected list of VMs has not been run, get the JSON data from PPDM before continuing
    if glb_o.ppdm_server.protected_vms_json == '':
        core_logic.get_list_protected_vms()

    # Clear the output screen
    glb_o.main_ui.clear_output()

    msg = f'Output of VM validation is provided in {glb_v.output_file}'
    logger.info(msg)
    file.append_datetime_prefix(glb_v.output_file, msg)
    glb_o.main_ui.append_to_output(msg, True)
    glb_o.main_ui.update()
    msg = f'PowerProtect Data Manager server is {glb_o.vcenter_server.fqdn}'
    logger.info(msg)
    file.append_datetime_prefix(glb_v.output_file, msg)
    glb_o.main_ui.append_to_output(msg, True)
    glb_o.main_ui.update()
    msg = f'vCenter server is {glb_o.vcenter_server.fqdn}'
    logger.info(msg)
    file.append_datetime_prefix(glb_v.output_file, msg)
    glb_o.main_ui.append_to_output(msg, True)
    glb_o.main_ui.update()

    # Get the list of user defined VMs from the text file as specified in the UI
    glb_o.ppdm_server.user_vm_names = file.create_list(glb_o.main_ui.directories_vm_path.get())

    # Filter the list of VMs and the href references based on the user VM list
    glb_o.ppdm_server.user_vm_names_id = \
        task.compare_dict_with_list_inclusion(glb_o.ppdm_server.protected_vms_names_id,
                                              glb_o.ppdm_server.user_vm_names)
    glb_o.vm.total_vms_to_process = len(glb_o.ppdm_server.user_vm_names_id)
    glb_o.main_ui.progress_total_vms_amount.configure(text=glb_o.vm.total_vms_to_process)
    msg = f'The total number of VMs to validate is: {glb_o.vm.total_vms_to_process}'
    logger.info(msg)
    file.append_datetime_prefix(glb_v.output_file, msg)
    glb_o.main_ui.append_to_output(msg, True)
    glb_o.main_ui.update()

    # Get the list of VMs in user defined list that are not protected by NetWorker
    uncommon_vms = task.compare_list_with_dict_exclusion(glb_o.ppdm_server.user_vm_names,
                                                         glb_o.ppdm_server.protected_vms_names_id)
    for item in uncommon_vms:
        msg = f'VM {item} in User Defined VM List was not found in the backup server protected VM list ' \
              f'and skipping VM validation.'
        glb_o.main_ui.append_to_output(msg, True)


def process_each_vm_via_instant_access() -> None:
    """
    Process each VM by performing an instant access recovery and see if VM tools starts
    """

    # Reset these values before the VM validation proceeds
    glb_o.vm.vm_successfully_processed = 0
    glb_o.vm.validation_summary = []

    # Process each user listed VM for backup validation where the glb_o.vm.name is a reference to the VM
    for vm_name, vm_ref in glb_o.ppdm_server.user_vm_names_id.items():
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

            # Refresh the access token for PPDM
            ppdm_response = glb_o.ppdm_server.refresh_token_api_call()
            glb_o.ppdm_server.token = ppdm_response['access_token']

            # Refresh the access token for vCenter
            glb_o.vcenter_server.authenticate_api_call()

            msg = f'{glb_o.vm.name} - Processing VM for validation'
            logger.info(msg)
            msg = f'The VM asset ID is {glb_o.vm.vm_ref}'
            logger.info(msg)

            # Get the latest backups for each user listed VM as JSON response
            glb_o.ppdm_server.temp_vm_latest_backup_json = glb_o.ppdm_server.get_asset_backups(glb_o.vm.vm_ref)

            if glb_o.ppdm_server.temp_vm_latest_backup_json != 'API call failed':
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

        # Proceed with instant access if the required JSON response was received from PPDM
        if glb_o.vm.continue_validation:

            # Obtain the latest backup ID for the VM image backup
            glb_o.ppdm_server.temp_backup_id = \
                ppdm_process_json.get_latest_backup_id(glb_o.ppdm_server.temp_vm_latest_backup_json)

            # Obtain the vCenter information needed to build the payload for the instant access recovery request
            glb_o.ppdm_server.temp_asset_info_json = glb_o.ppdm_server.get_asset_info(glb_o.vm.vm_ref)

            # Create the payload information needed to make the instant access recovery of the VM
            glb_o.ppdm_server.temp_payload = \
                ppdm_process_json.get_instant_access_payload_data(glb_o.ppdm_server.temp_asset_info_json,
                                                                  glb_o.ppdm_server.temp_backup_id)
            msg = 'Payload information for the PPDM instant access recovery request'
            logger.info(msg)
            logger.info(glb_o.ppdm_server.temp_payload)

            # Performing the instant access recovery of the VM with PowerProtect Data Manager
            response = glb_o.ppdm_server.instant_access_recovery(glb_o.ppdm_server.temp_payload)

            if response != 'API call failed':
                msg = f'{glb_o.vm.name} - Instant Access recovery request is being processed'
                logger.info(msg)
                file.append_datetime_prefix(glb_v.output_file, msg)
                glb_o.main_ui.append_to_output(msg, True)
                glb_o.ppdm_server.temp_activity_id = response['id']
                msg = f'{glb_o.vm.name} - The activity ID for the instant access recovery is ' \
                      f'{glb_o.ppdm_server.temp_activity_id}'
                logger.info(msg)
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
            msg = f'{glb_o.vm.name} - Attempting to stop the instant access recovery session'
            logger.info(msg)
            file.append_datetime_prefix(glb_v.output_file, msg)
            glb_o.main_ui.append_to_output(msg, True)
            glb_o.main_ui.update()
            response = glb_o.ppdm_server.cancel_instant_access_recovery(glb_o.ppdm_server.temp_activity_id)
            if response == 'API call successful':
                msg = f'{glb_o.vm.name} - Stopped the instant access recovery session. It may take up to 1 minute ' \
                      f'for the VM to be removed from vCenter'
                logger.info(msg)
                file.append_datetime_prefix(glb_v.output_file, msg)
                glb_o.main_ui.append_to_output(msg, True)
                glb_o.main_ui.update()

            else:
                msg = f'{glb_o.vm.name} - API call to cancel the instant access recovery for {glb_o.vm.ia_name} ' \
                      f'failed. You may need to remove the VM {glb_o.vm.ia_name} manually from vCenter and/or ' \
                      f'PowerProtect Data Manager server {glb_o.ppdm_server.fqdn}.'
                logger.info(msg)
                glb_o.main_ui.append_to_output(msg, True)

        if not glb_o.vm.continue_validation:
            msg = f'{glb_o.vm.name} - Skipping validation of this VM and moving onto the next VM. ' \
                  f'See logs for more detail as to why VM validation was skipped.'
            logger.info(msg)
            file.append_datetime_prefix(glb_v.output_file, msg)
            glb_o.main_ui.append_to_output(msg, True)
            glb_o.main_ui.update()
