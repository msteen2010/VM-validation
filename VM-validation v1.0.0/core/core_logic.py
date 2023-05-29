#!/usr/bin/env python3
"""
This module provides the core logic of the application

Written by Mike van der Steen
Version 1.00

Last updated 27 December 2022
"""
import os
import time

from utils import log, task, file
from core.networker import nw_api_calls, nw_process_json
from core.ppdm  import ppdm_api_calls, ppdm_process_json
from core.vmware import vcenter_processes
from utils import globals as glb


logger = log.custom_logger()


def validation_of_credentials():
    """
    Getting the values entered by the user and verifying if the credentials are correct
    """

    # clear the output screen
    glb.main_ui.clear_output()
    # check that all input fields are populated with information
    check_for_empty_inputs()

    # Determine if NetWorker or PowerProtect Data Manager is selected
    if glb.main_ui.server_selected.get() == 'NetWorker' and glb.main_ui.all_inputs_provided:
        msg = 'NetWorker is the backup software and all inputs have been provided'
        logger.info(msg)
        # preform a validation check and get the resultant response
        nw_credentials_valid = validate_nw_credentials()
        vcenter_credentials_valid = validate_vcenter_credentials()

        # check to see if the validation check of the credentials for NW were successful
        if nw_credentials_valid:
            msg = 'NetWorker server credentials are valid'
            logger.info(msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.backup_verified_label.config(text=msg)
            glb.main_ui.update()

        # Check if the vCenter server credentials were valid
        if vcenter_credentials_valid:
            msg = 'vCenter server credentials are valid'
            logger.info(msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.vcenter_verified_label.config(text=msg)
            glb.main_ui.update()

        # Check if both backup and vCenter server credentials are valid, enable the buttons
        if nw_credentials_valid and vcenter_credentials_valid:
            msg = f'Both NetWorker server {glb.main_ui.backup_server_input.get()} ' \
                  f'and vCenter server {glb.main_ui.vcenter_server_input.get()} ' \
                  f'credentials are valid - enabling the buttons on the GUI'
            logger.info(msg)
            glb.main_ui.button_get_vms.configure(state='active')
            glb.main_ui.button_validate_vms.configure(state='active')
            glb.main_ui.update()

        else:
            msg = 'Please check that the server type, the associated FQDN, username and password are correct'
            logger.error(f'{msg} for server: {glb.main_ui.backup_server_input.get()}')
            glb.main_ui.button_get_vms.configure(state='disabled')
            glb.main_ui.button_validate_vms.configure(state='disabled')
            if not nw_credentials_valid:
                glb.main_ui.backup_verified_label.config(text='No')
            if not vcenter_credentials_valid:
                glb.main_ui.vcenter_verified_label.config(text='No')
            glb.main_ui.update()

    # Confirm that PowerProtect Data Manager has been selected
    elif glb.main_ui.server_selected.get() == 'PowerProtect Data Manager' and glb.main_ui.all_inputs_provided:
        msg = 'PowerProtect Data Manager is the backup software and all inputs have been provided'
        logger.info(msg)
        # Obtain the authentication token to preform a validation check and get the resultant token response
        ppdm_credentials_valid = validate_ppdm_credentials()
        vcenter_credentials_valid = validate_vcenter_credentials()

        # check to see if the validation check of the credentials for PPDM were successful
        if ppdm_credentials_valid:
            msg = 'PowerProtect Data Manager server credentials are valid'
            logger.info(msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.backup_verified_label.config(text=msg)
            glb.main_ui.update()

        # Check if the vCenter server credentials were valid
        if vcenter_credentials_valid:
            msg = 'vCenter server credentials are valid'
            logger.info(msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.vcenter_verified_label.config(text=msg)
            glb.main_ui.update()

        # Check if both backup and vCenter server credentials are valid, enable the buttons
        if ppdm_credentials_valid and vcenter_credentials_valid:
            msg = f'Both PowerProtect Data Manager server {glb.main_ui.backup_server_input.get()} ' \
                  f'and vCenter server {glb.main_ui.vcenter_server_input.get()} ' \
                  f'credentials are valid - enabling the buttons on the GUI'
            logger.info(msg)
            glb.main_ui.button_get_vms.configure(state='active')
            glb.main_ui.button_validate_vms.configure(state='active')
            glb.main_ui.update()

        else:
            msg = 'Please check that the server type, the associated FQDN, username and password are correct'
            logger.error(f'{msg} for server: {glb.main_ui.backup_server_input.get()}')
            glb.main_ui.button_get_vms.configure(state='disabled')
            glb.main_ui.button_validate_vms.configure(state='disabled')
            if not ppdm_credentials_valid:
                glb.main_ui.backup_verified_label.config(text='No')
            if not vcenter_credentials_valid:
                glb.main_ui.vcenter_verified_label.config(text='No')
            glb.main_ui.update()


def check_for_empty_inputs():
    """
    Check if the input fields contain information, before the credentials can be validated
    """
    msg = 'Checking for empty inputs, before credential validation can continue'
    logger.info(msg)

    # Iterate through the list of input values to determine if they are empty or not
    for item in glb.main_ui.input_list:
        value = item.get()
        if value == '':
            msg = f'No information was provided for - {item.winfo_name()}'
            logger.info(msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
            glb.main_ui.number_empty_fields += 1

    # Set the variable to True if there are no empty input fields
    if glb.main_ui.number_empty_fields == 0:
        glb.main_ui.all_inputs_provided = True
        msg = 'All inputs have been entered into the text fields'
        logger.info(msg)
    else:
        msg = '\nAs one of more inputs were left empty, validation cannot continue \n' \
              'Provide information to the above listed field/s'
        logger.error(msg)
        glb.main_ui.append_to_output(msg, True)
        glb.main_ui.update()
        # Reset the counter
        glb.main_ui.number_empty_fields = 0


def validate_nw_credentials() -> bool:
    """
    Validate the credentials of the backup server - NetWorker
    """

    # Extract the backup server information and credentials from the user input on the GUI
    glb.nw_server.fqdn = glb.main_ui.backup_server_input.get()
    glb.nw_server.api_user = glb.main_ui.backup_user_input.get()
    glb.nw_server.api_password = glb.main_ui.backup_pass_input.get()
    msg = 'Extracting the input data from the NetWorker backup server'
    logger.info(msg)

    # Make an API call to NetWorker to see fi the credentials are correct
    nw_response = nw_api_calls.get_alerts(glb.nw_server.fqdn, glb.nw_server.api_user, glb.nw_server.api_password)

    if nw_response != 'API call unsuccessful':
        msg = 'Rest API call to NetWorker successful'
        logger.info(msg)
        glb.main_ui.append_to_output(msg, True)
        glb.main_ui.update()
        glb.nw_server.api_call_success = True
        return True
    else:
        msg = 'The NetWorker server credentials and/or FQDN provided are not correct.\n' \
              'Please check that the correct information has been provided for NetWorker.\n' \
              'Review the debug log file that is located in the log directory where this utility is run from.'
        logger.info(msg)
        glb.main_ui.append_to_output(msg, True)
        glb.main_ui.update()
        glb.nw_server.api_call_success = False
        return False


def validate_ppdm_credentials() -> bool:
    """
    Validate the credentials of the backup server - PowerProtect Data Manager
    """

    # Extract the backup server information and credentials from the user input on the GUI
    glb.ppdm_server.fqdn = glb.main_ui.backup_server_input.get()
    glb.ppdm_server.api_user = glb.main_ui.backup_user_input.get()
    glb.ppdm_server.api_password = glb.main_ui.backup_pass_input.get()
    msg = 'Extracting the input data from the NetWorker backup server'
    logger.info(msg)

    # Make an API call to NetWorker to see fi the credentials are correct
    ppdm_response = ppdm_api_calls.authenticate_api_call(glb.ppdm_server.fqdn,
                                                         glb.ppdm_server.api_user,
                                                         glb.ppdm_server.api_password)

    if ppdm_response != 'API call unsuccessful':
        msg = 'Rest API call to PowerProtect Data Manager successful'
        logger.info(msg)
        glb.main_ui.append_to_output(msg, True)
        glb.main_ui.update()
        glb.ppdm_server.api_call_success = True
        glb.ppdm_server.token = ppdm_response['access_token']
        glb.ppdm_server.refresh_token = ppdm_response['refresh_token']
        return True
    else:
        msg = 'The PowerProtect Data Manager server credentials and/or FQDN provided are not correct.\n' \
              'Please check that the correct information has been provided for PowerProtect Data manager.\n' \
              'Review the debug log file that is located in the log directory where this utility is run from.'
        logger.info(msg)
        glb.main_ui.append_to_output(msg, True)
        glb.main_ui.update()
        glb.ppdm_server.api_call_success = False
        return False


def validate_vcenter_credentials() -> bool:
    """
    Validate the credentials of vCenter server
    """

    # Extract the vcenter server information and credentials from the user input on the GUI
    glb.vcenter_server.fqdn = glb.main_ui.vcenter_server_input.get()
    glb.vcenter_server.user = glb.main_ui.vcenter_user_input.get()
    glb.vcenter_server.password = glb.main_ui.vcenter_pass_input.get()
    msg = 'Extracting the input data from the vCenter server'
    logger.info(msg)

    glb.vcenter_server.connection_success = vcenter_processes.validation_credentials(glb.vcenter_server)

    # If the credentials call is successful, return True response
    if glb.vcenter_server.connection_success:
        msg = 'SmartConnect connection to vCenter successfully made'
        logger.info(msg)
        glb.main_ui.append_to_output(msg, True)
        glb.main_ui.update()
        return True


def get_list_protected_vms():
    """
    This function will extract the list of all protected VMs from the backup server and save it to a file.
    """

    if glb.main_ui.server_selected.get() == 'NetWorker':

        # Get the protected VMs JSON response from NetWorker server
        glb.nw_server.protected_vms_json = nw_api_calls.get_protected_vms(glb.nw_server.fqdn,
                                                                          glb.nw_server.api_user,
                                                                          glb.nw_server.api_password,
                                                                          glb.vcenter_server)
        # Store the protected VMs names to the NetWorker object
        if glb.nw_server.protected_vms_json != 'API call unsuccessful':
            glb.nw_server.protected_vms_names = \
                nw_process_json.get_protected_vms_names(glb.nw_server.protected_vms_json)

        # Output the data to a text file
        complete_path = os.path.join(glb.main_ui.directories_output_path.get(),
                                     f'Protected vms by {glb.nw_server.fqdn} for {glb.vcenter_server.fqdn}.txt')
        file.write_list(complete_path, glb.nw_server.protected_vms_names)
        msg = f'Protected VMs written to {complete_path}'
        logger.info(msg)
        glb.main_ui.write_to_output(msg)
        glb.main_ui.update()

    elif glb.main_ui.server_selected.get() == 'PowerProtect Data Manager':

        # Refresh the access token
        ppdm_response = ppdm_api_calls.refresh_token_api_call(glb.ppdm_server.fqdn,
                                                              glb.ppdm_server.token,
                                                              glb.ppdm_server.refresh_token)
        glb.ppdm_server.token = ppdm_response['access_token']

        # Get the protected VMs JSON response from PowerProtect Data Manager server
        glb.ppdm_server.protected_vms_json = ppdm_api_calls.get_protected_vms(glb.ppdm_server.fqdn,
                                                                              glb.ppdm_server.token)

        # Store the protected VMs names to the NetWorker object
        if glb.ppdm_server.protected_vms_json != 'API call unsuccessful':
            glb.ppdm_server.protected_vms_names_id = \
                ppdm_process_json.get_protected_vms_names_by_vcenter(glb.ppdm_server.protected_vms_json,
                                                                     glb.vcenter_server.fqdn)

        # Output the data to a text file
        complete_path = os.path.join(glb.main_ui.directories_output_path.get(),
                                     f'Protected vms by {glb.ppdm_server.fqdn} for {glb.vcenter_server.fqdn}.txt')
        file.write_dict_key(complete_path, glb.ppdm_server.protected_vms_names_id)
        msg = f'Protected VMs written to {complete_path}'
        logger.info(msg)
        glb.main_ui.write_to_output(msg)
        glb.main_ui.update()


def validate_vms():
    """
    This is the function that is run when the 'Validate VM' button is pressed on the UI
    """
    if glb.main_ui.server_selected.get() == 'NetWorker':
        validate_nw_vms()
        msg = 'Validating NetWorker VMs'
        logger.info(msg)
    elif glb.main_ui.server_selected.get() == 'PowerProtect Data Manager':
        validated_ppdm_vms()
        msg = 'Validating PowerProtect Data Manager VMs'
        logger.info(msg)


def validate_nw_vms():
    """
    NetWorker protected VMs that the user wishes to validate will be run in this function
    """

    vm_successfully_processed = 0
    validation_summary = []

    # Create the output file that will contain an audit of the VM validation
    glb.output_file = file.create_datetime_file(glb.main_ui.directories_output_path.get(),
                                                '-VM validation output.txt')

    # If the protected list of VMs has not been run, get the JSON data before continuing
    if glb.nw_server.protected_vms_json == '':
        get_list_protected_vms()

    # Clear the output screen
    glb.main_ui.clear_output()

    msg = f'Output of VM validation is provided in {glb.output_file}'
    logger.info(msg)
    file.append_datetime_prefix(glb.output_file, msg)
    glb.main_ui.append_to_output(msg, True)
    glb.main_ui.update()
    msg = f'NetWorker server is {glb.nw_server.fqdn}'
    logger.info(msg)
    file.append_datetime_prefix(glb.output_file, msg)
    glb.main_ui.append_to_output(msg, True)
    glb.main_ui.update()
    msg = f'vCenter server is {glb.vcenter_server.fqdn}'
    logger.info(msg)
    file.append_datetime_prefix(glb.output_file, msg)
    glb.main_ui.append_to_output(msg, True)
    glb.main_ui.update()

    # Extract the protected VMs and the href reference from NetWorker and store it in a dictionary
    glb.nw_server.protected_vms_names_href = nw_process_json.get_protected_vms_href(glb.nw_server.protected_vms_json)

    # Get the list of user defined VMs from the text file as specified in the UI
    glb.nw_server.user_vm_names = file.create_list(glb.main_ui.directories_vm_path.get())

    # Filter the list of VMs and the href references based on the user VM list
    glb.nw_server.user_vm_names_href = task.compare_dict_with_list_inclusion(glb.nw_server.protected_vms_names_href,
                                                                             glb.nw_server.user_vm_names)
    number_of_vms = len(glb.nw_server.user_vm_names_href)
    glb.main_ui.progress_total_vms_amount.configure(text=number_of_vms)
    msg = f'The total number of VMs to validate is: {number_of_vms}'
    logger.info(msg)
    file.append_datetime_prefix(glb.output_file, msg)
    glb.main_ui.append_to_output(msg, True)
    glb.main_ui.update()

    # Get the list of VMs in user defined list that are not protected by NetWorker
    uncommon_vms = task.compare_list_with_dict_exclusion(glb.nw_server.user_vm_names,
                                                         glb.nw_server.protected_vms_names_href)
    for value in uncommon_vms:
        msg = f'VM called {value} in User Defined List of VMs was not found in backup server protected VM list ' \
              f'and is being excluded from VM validation. VM name is case sensitive, please check spelling and case.'
        glb.main_ui.append_to_output(msg, True)

    # Process each user listed VM for backup validation where the key is a reference to the VM
    for key, value in glb.nw_server.user_vm_names_href.items():
        msg = f'{key} - Processing VM for validation'
        logger.info(msg)
        file.append_datetime_prefix(glb.output_file, msg)
        glb.main_ui.append_to_output(msg, True)
        glb.main_ui.update()
        msg = f'URL endpoint for the vm is {value}'
        logger.info(msg)

        # Get the latest backups for each user listed VM as JSON response
        glb.nw_server.temp_vm_latest_backup_json = \
            nw_api_calls.get_protected_vm_lastest_backup(glb.nw_server.fqdn,
                                                         glb.nw_server.api_user,
                                                         glb.nw_server.api_password,
                                                         key,
                                                         value)
        if glb.nw_server.temp_vm_latest_backup_json != 'API call unsuccessful':
            msg = f'{key} - Obtained the latest VM backup JSON response from the API call'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
        else:
            msg = f'{key} - Failed to get the latest VM backup JSON response from the API call, ' \
                  f'unable to proceed further and skipping the VM validation'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
            break

        # Process the JSON data for the latest backup and extract the recovery URL
        glb.nw_server.temp_vm_latest_recovery_href = \
            nw_process_json.get_protected_vms_latest_backup_href(glb.nw_server.temp_vm_latest_backup_json)

        # Get the available recovery details for the latest backup href in the form of a JSON response
        glb.nw_server.temp_vm_latest_recovery_json = \
            nw_api_calls.get_api_call(glb.nw_server.fqdn,
                                      glb.nw_server.api_user,
                                      glb.nw_server.api_password,
                                      glb.nw_server.temp_vm_latest_recovery_href)
        if glb.nw_server.temp_vm_latest_recovery_json != 'API call unsuccessful':
            msg = f'{key} - Obtained the VM recovery JSON response from the API call'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
        else:
            msg = f'{key} - Failed to get the VM recovery JSON response from the API call, ' \
                  f'unable to proceed further and skipping the VM validation'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
            break

        # Process the latest VM recovery href response to extract the URL and data required for instant access recovery
        vm_restore_link, json_data = \
            nw_process_json.get_instant_access_restore_link(glb.nw_server.temp_vm_latest_recovery_json)
        if glb.nw_server.temp_vm_latest_recovery_json != 'API call unsuccessful':
            instant_access_vm = json_data['vmName']
            msg = f'{key} - Recovery URL endpoint is {vm_restore_link}'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            msg = f'{key} - JSON data package is {json_data}'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            msg = f'{key} - Performing Instant Access Recovery of VM with the name of {instant_access_vm}'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
        else:
            msg = f'{key} - Failed to get the VM instant access restore link from the API call, ' \
                  f'unable to proceed further and skipping the VM validation'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
            break

        # Start the Instant Access recovery using the vm_restore_link and json_data information
        response = nw_api_calls.post_api_call(glb.nw_server.fqdn,
                                              glb.nw_server.api_user,
                                              glb.nw_server.api_password,
                                              vm_restore_link,
                                              json_data)
        if response != 'API call unsuccessful':
            glb.nw_server.recovery_job = response['Location']
            msg = f'{key} - NetWorker job reference: {glb.nw_server.recovery_job}'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
        else:
            msg = f'{key} - Post API call to start the instant access recovery failed, ' \
                  f'Review the debug log file that is located in the log directory where this utility is run from.'
            logger.info(msg)
            glb.main_ui.append_to_output(msg, True)

        # Connect to vCenter to see if the Instant Access VM has been configured within vCenter
        msg = f'{key} - Checking if registered with the vCenter'
        logger.info(msg)
        file.append_datetime_prefix(glb.output_file, msg)
        glb.main_ui.append_to_output(msg, True)
        glb.main_ui.update()

        # check with VMware on the state of the Instant Access VM recovery
        vm_validation = vmware_checks(key, instant_access_vm)

        if not vm_validation:
            msg = f'{key} - VM validation cannot proceed as VMware Tools is not installed or running. ' \
                  f'Skipping validation of this VM'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
            msg = f'Install VMtools on {key} to enable VM validation to be run in future tests'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
            validation_summary.append(f'{key} - Validation Failed')

        if vm_validation:
            msg = f'{key} - VM validation is successful as VMware Tools is running. ' \
                  f'VM validation of the latest backup for VM {key} is successful'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
            vm_successfully_processed += 1
            glb.main_ui.progressed_vms_amount.config(text=vm_successfully_processed)
            validation_summary.append(f'{key} - Validation Successful')

        # Cancel the Instant Access recovery job in NetWorker
        cancel_recovery_url = f'{glb.nw_server.recovery_job}/op/cancel'
        data = {}
        job_status = nw_api_calls.post_api_cancel_job(glb.nw_server.fqdn,
                                                      glb.nw_server.api_user,
                                                      glb.nw_server.api_password,
                                                      cancel_recovery_url,
                                                      data)
        time.sleep(3)
        if response != 'API call unsuccessful':
            if job_status:
                msg = f'{key} - Stopping the instant access recovery session'
                logger.info(msg)
                file.append_datetime_prefix(glb.output_file, msg)
                glb.main_ui.append_to_output(msg, True)
                glb.main_ui.update()
            else:
                msg = f'{key} - An error occurred trying to stop the instant access recovery. ' \
                      f'You may need to remove the VM {instant_access_vm} manually from vCenter ' \
                      f'{glb.vcenter_server.fqdn}'
                logger.info(msg)
                file.append_datetime_prefix(glb.output_file, msg)
                glb.main_ui.append_to_output(msg, True)
                glb.main_ui.update()
        else:
            msg = f'{key} - Post API call to cancel the instant access recovery for {instant_access_vm} failed, ' \
                  f'Review the debug log file that is located in the log directory where this utility is run from.'
            logger.info(msg)
            glb.main_ui.append_to_output(msg, True)

    # Summary of VM validation
    msg = f'Successfully validated {vm_successfully_processed} of {number_of_vms} VMs'
    logger.info(msg)
    file.append_datetime_prefix(glb.output_file, msg)
    glb.main_ui.append_to_output(msg, True)
    glb.main_ui.update()
    file.append_list(glb.output_file, validation_summary)


def validated_ppdm_vms():
    """
    PowerProtect Data Manager protected VMs that the user wishes to validate will be run in this function
    """

    vm_successfully_processed = 0
    validation_summary = []

    # Create the output file that will contain an audit of the VM validation
    glb.output_file = file.create_datetime_file(glb.main_ui.directories_output_path.get(),
                                                '-VM validation output.txt')

    # Refresh the access token
    ppdm_response = ppdm_api_calls.refresh_token_api_call(glb.ppdm_server.fqdn,
                                                          glb.ppdm_server.token,
                                                          glb.ppdm_server.refresh_token)
    glb.ppdm_server.token = ppdm_response['access_token']

    # If the protected list of VMs has not been run, get the JSON data from PPDM before continuing
    if glb.ppdm_server.protected_vms_json == '':
        get_list_protected_vms()

    # Clear the output screen
    glb.main_ui.clear_output()

    msg = f'Output of VM validation is provided in {glb.output_file}'
    logger.info(msg)
    file.append_datetime_prefix(glb.output_file, msg)
    glb.main_ui.append_to_output(msg, True)
    glb.main_ui.update()
    msg = f'PowerProtect Data Manager server is {glb.nw_server.fqdn}'
    logger.info(msg)
    file.append_datetime_prefix(glb.output_file, msg)
    glb.main_ui.append_to_output(msg, True)
    glb.main_ui.update()
    msg = f'vCenter server is {glb.vcenter_server.fqdn}'
    logger.info(msg)
    file.append_datetime_prefix(glb.output_file, msg)
    glb.main_ui.append_to_output(msg, True)
    glb.main_ui.update()

    # Get the list of user defined VMs from the text file as specified in the UI
    glb.ppdm_server.user_vm_names = file.create_list(glb.main_ui.directories_vm_path.get())

    # Filter the list of VMs and the href references based on the user VM list
    glb.ppdm_server.user_vm_names_id = \
        task.compare_dict_with_list_inclusion(glb.ppdm_server.protected_vms_names_id,
                                              glb.ppdm_server.user_vm_names)
    number_of_vms = len(glb.ppdm_server.user_vm_names_id)
    glb.main_ui.progress_total_vms_amount.configure(text=number_of_vms)
    msg = f'The total number of VMs to validate is: {number_of_vms}'
    logger.info(msg)
    file.append_datetime_prefix(glb.output_file, msg)
    glb.main_ui.append_to_output(msg, True)
    glb.main_ui.update()

    # Get the list of VMs in user defined list that are not protected by NetWorker
    uncommon_vms = task.compare_list_with_dict_exclusion(glb.ppdm_server.user_vm_names,
                                                         glb.ppdm_server.protected_vms_names_id)
    for value in uncommon_vms:
        msg = f'VM called {value} in User Defined List of VMs was not found in backup server protected VM list ' \
              f'and is being excluded from VM validation. VM name is case sensitive, please check spelling and case.'
        glb.main_ui.append_to_output(msg, True)

    # Process each user listed VM for backup validation where the key is a reference to the VM
    for key, value in glb.ppdm_server.user_vm_names_id.items():
        msg = f'{key} - Processing VM for validation'
        logger.info(msg)
        file.append_datetime_prefix(glb.output_file, msg)
        glb.main_ui.append_to_output(msg, True)
        glb.main_ui.update()
        msg = f'The VM asset ID is {value}'
        logger.info(msg)
        # Get the latest backups for each user listed VM as JSON response
        glb.ppdm_server.temp_vm_latest_backup_json = \
            ppdm_api_calls.get_asset_backups(glb.ppdm_server.fqdn, glb.ppdm_server.token, value)

        if glb.ppdm_server.temp_vm_latest_backup_json != 'API call unsuccessful':
            msg = f'{key} - Obtained the latest VM backup JSON response from the API call'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
            glb.ppdm_server.temp_backup_id = \
                ppdm_process_json.get_latest_backup_id(glb.ppdm_server.temp_vm_latest_backup_json)
        else:
            msg = f'{key} - Failed to get the latest VM backup JSON response from the API call, ' \
                  f'unable to proceed further and skipping the VM validation'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
            break

        # Obtain the vCenter information needed to build the payload for the instant access recovery request
        glb.ppdm_server.temp_asset_info_json = ppdm_api_calls.get_asset_info(glb.ppdm_server.fqdn,
                                                                             glb.ppdm_server.token,
                                                                             value)
        # Create the payload information needed to make the instant access recovery of the VM
        glb.ppdm_server.temp_payload = \
            ppdm_process_json.get_instant_access_payload_data(glb.ppdm_server.temp_asset_info_json,
                                                              glb.ppdm_server.temp_backup_id)
        msg = 'Payload information for the PPDM instant access recovery request'
        logger.info(msg)
        logger.info(glb.ppdm_server.temp_payload)

        # Performing the instant access recovery of the VM with PowerProtect Data Manager
        response = ppdm_api_calls.instant_access_recovery(glb.ppdm_server.fqdn,
                                                          glb.ppdm_server.token,
                                                          glb.ppdm_server.temp_payload)

        if response != 'API call unsuccessful':
            msg = f'{key} - Instant Access recovery request is being processed'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.ppdm_server.temp_activity_id = response['id']
            msg = f'{key} - The activity ID for the instant access recovery is {glb.ppdm_server.temp_activity_id}'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
        else:
            msg = f'{key} - Failed to process the Instant Access recovery request, ' \
                  f'unable to proceed further and skipping the VM validation'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
            break

        # Connect to vCenter to see if the Instant Access VM has been configured within vCenter
        msg = f'{key} - Checking if registered with the vCenter'
        logger.info(msg)
        file.append_datetime_prefix(glb.output_file, msg)
        glb.main_ui.append_to_output(msg, True)
        glb.main_ui.update()

        # Check with VMware on the state of the Instant Access VM recovery
        instant_access_vm = f'{key}_ia'
        vm_validation = vmware_checks(key, instant_access_vm)

        if not vm_validation:
            msg = f'{key} - VM validation cannot proceed as VMware Tools is not installed or running. ' \
                  f'Skipping validation of this VM'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
            msg = f'Install VMtools on {key} to enable VM validation to be run in future tests'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
            validation_summary.append(f'{key} - Validation Failed')

        if vm_validation:
            msg = f'{key} - VM validation is successful as VMware Tools is running. ' \
                  f'VM validation of the latest backup for VM {key} is successful'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
            vm_successfully_processed += 1
            glb.main_ui.progressed_vms_amount.config(text=vm_successfully_processed)
            validation_summary.append(f'{key} - Validation Successful')

        # Cancel the Instant Access recovery job in PowerProtect Data Manager
        response = ppdm_api_calls.cancel_instant_access_recovery(glb.ppdm_server.fqdn,
                                                                 glb.ppdm_server.token,
                                                                 glb.ppdm_server.temp_activity_id)
        time.sleep(3)
        if response == 'API call successful':
            msg = f'{key} - Stopping the instant access recovery session'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
        else:
            msg = f'{key} - Post API call to cancel the instant access recovery for {instant_access_vm} failed, ' \
                  f'You may need to remove the VM {instant_access_vm} manually from vCenter and/or ' \
                  f'PowerProtect Data Manager server {glb.ppdm_server.fqdn}.'
            logger.info(msg)
            glb.main_ui.append_to_output(msg, True)

    # Summary of VM validation
    msg = f'Successfully validated {vm_successfully_processed} of {number_of_vms} VMs'
    logger.info(msg)
    file.append_datetime_prefix(glb.output_file, msg)
    glb.main_ui.append_to_output(msg, True)
    glb.main_ui.update()
    file.append_list(glb.output_file, validation_summary)


def vmware_checks(key, ia_vm: str) -> bool:
    """
    Communicate with vCenter to check the stat of the Instant Access VM
    """

    # Communicate with vCenter to see if the instant access recovery VM has been registered with vCenter
    vm_present = False
    attempt = 0

    while not vm_present:
        vm_present = vcenter_processes.find_vm(glb.vcenter_server, ia_vm)
        attempt += 1
        seconds = attempt * 1
        time.sleep(1)

        if vm_present:
            msg = f'{key} - {ia_vm}has been registered with vCenter and took {seconds} seconds'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
            vm_present = True

        if not vm_present:
            if attempt == 1:
                msg = f'{key} - Checking registration of {ia_vm} with vCenter'
                glb.main_ui.append_to_output(msg, False)
                glb.main_ui.update()
            else:
                msg = '.'
                glb.main_ui.append_to_output(msg, False)
                glb.main_ui.update()

        if attempt == 60:
            msg = f'\n{key} - Waiting for VM {ia_vm} to be registered with vCenter, but ' \
                  f'timed out after {seconds} seconds'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
            break

    # Providing vCenter a few extra seconds to ensure that the VM is fully configured and registered - default 5 seconds
    time.sleep(glb.registered_vm_delay)
    # If the VM is present, check the power state and power it on if needed
    power_state = None
    attempt = 0

    if vm_present:
        msg = f'{key} - Checking the power status of {ia_vm}'
        logger.info(msg)
        file.append_datetime_prefix(glb.output_file, msg)
        glb.main_ui.append_to_output(msg, True)
        glb.main_ui.update()
        power_state = vcenter_processes.is_vm_powered_on(glb.vcenter_server, ia_vm)

        if not power_state:
            msg = f'{key} - {ia_vm} is currently powered off'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, True)
            glb.main_ui.update()
            # powering on the VM
            vcenter_processes.power_on_vm(glb.vcenter_server, ia_vm)
            msg = f'{key} - {ia_vm} is being powered on'
            logger.info(msg)
            file.append_datetime_prefix(glb.output_file, msg)
            glb.main_ui.append_to_output(msg, False)
            glb.main_ui.update()

        # The timeout value for the VM powering on is 60 seconds (1 second per attempt
        while not power_state:
            attempt += 1
            seconds = attempt * 1
            msg = '.'
            glb.main_ui.append_to_output(msg, False)
            glb.main_ui.update()
            time.sleep(1)
            vcenter_processes.power_on_vm(glb.vcenter_server, ia_vm)
            power_state = vcenter_processes.is_vm_powered_on(glb.vcenter_server, ia_vm)

            # checking if the VM is now powered on
            if power_state:
                msg = f'{key} - {ia_vm} is powered on and took {seconds} seconds'
                logger.info(msg)
                file.append_datetime_prefix(glb.output_file, msg)
                glb.main_ui.append_to_output(msg, True)
                glb.main_ui.update()
                power_state = True

            # The default value for the number of attempts is 60 as obtained from the glb.ini file
            if attempt == glb.vm_powerup_timeout:
                msg = f'{key} - Waiting for {ia_vm} to power on, but timed out after {seconds} seconds'
                logger.info(msg)
                file.append_datetime_prefix(glb.output_file, msg)
                glb.main_ui.append_to_output(msg, True)
                glb.main_ui.update()
                break

    # If the VM powered on, check the VMtools is running and a timeout is set to 600 seconds (1 second per attempt)
    vm_tools_running = False
    attempt = 0

    if power_state:
        msg = f'{key} - Checking the status of VMware tools on {ia_vm}'
        logger.info(msg)
        file.append_datetime_prefix(glb.output_file, msg)
        glb.main_ui.append_to_output(msg, True)
        glb.main_ui.update()

        while not vm_tools_running:
            vm_tools_status = vcenter_processes.vm_tools_status(glb.vcenter_server, ia_vm)
            attempt += 1
            seconds = attempt * 1

            if vm_tools_status == 'toolsNotInstalled' or vm_tools_status == 'toolsNotRunning':
                if attempt == 1:
                    msg = f'{key} - Waiting for VMtools to start on {ia_vm} '
                    glb.main_ui.append_to_output(msg, False)
                    glb.main_ui.update()
                else:
                    msg = '.'
                    glb.main_ui.append_to_output(msg, False)
                    glb.main_ui.update()
                time.sleep(1)

            if vm_tools_status == 'toolsOk':
                msg = f'{key} - VMware Tools is running on {ia_vm} and took {seconds} seconds to start'
                logger.info(msg)
                file.append_datetime_prefix(glb.output_file, msg)
                glb.main_ui.append_to_output(msg, True)
                glb.main_ui.update()
                logger.info(msg)
                return True

            # The default value for the number of attempts is 600 as obtained from the glb.ini file
            if attempt == glb.vmtools_startup_timeout:
                msg = f'{key} - Waiting for VMware Tools to start on {ia_vm} timed out after {seconds} seconds'
                logger.info(msg)
                file.append_datetime_prefix(glb.output_file, msg)
                glb.main_ui.append_to_output(msg, True)
                glb.main_ui.update()
                return False
