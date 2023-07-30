#!/usr/bin/env python3
"""
This module provides the core logic of the application

author: Mike van der Steen
last updated: 31 July 2023
"""

import os

from utils import log, file, web
from core import ppdm_logic, nw_logic
from core.networker import nw_process_json
from core.ppdm import ppdm_process_json
from utils import global_objects as glb_o
from utils import global_variables as glb_v

logger = log.custom_logger()


def validation_of_credentials():
    """
    Getting the values entered by the user and verifying if the credentials are correct
    """

    # clear the output screen
    glb_o.main_ui.clear_output()
    # check that all input fields are populated with information
    check_for_empty_inputs()

    # Reset the VM count
    glb_o.main_ui.progress_total_vms_amount.configure(text='')
    glb_o.main_ui.progressed_vms_amount.configure(text='')

    # Determine if NetWorker or PowerProtect Data Manager is to be used for this validation
    if glb_o.main_ui.all_inputs_provided:
        msg = 'Determining the backup server type:'
        logger.info(msg)
        glb_o.main_ui.append_to_output(msg, True)
        glb_o.main_ui.update_idletasks()

        # Obtain the backup server FQDN from the input field
        glb_v.backup_server_fqdn = glb_o.main_ui.backup_server_input.get()

        # Defining the URLs for each backup server type and adding them to a list
        nw_uri = 'https://' + glb_v.backup_server_fqdn + ':9090/nwui'
        ppdm_uri = 'https://' + glb_v.backup_server_fqdn
        uri_list = [nw_uri, ppdm_uri]

        # Determine the backup server type
        for uri in uri_list:
            # Does the web page title state NetWorker?
            response = web.title_search(uri, 'NetWorker')
            if response:
                glb_v.backup_server_type = 'NetWorker'
                msg = f'The backup server {glb_v.backup_server_fqdn} was determined to be NetWorker'
                logger.info(msg)
                glb_o.main_ui.append_to_output(msg, True)
                glb_o.main_ui.update_idletasks()
            # Does teh web page title state PowerProtect Data manager?
            response = web.title_search(uri, 'PowerProtect Data Manager')
            if response:
                glb_v.backup_server_type = 'PowerProtect Data Manager'
                msg = f'The backup server {glb_v.backup_server_fqdn} was determined to be PowerProtect Data Manager'
                logger.info(msg)
                glb_o.main_ui.append_to_output(msg, True)
                glb_o.main_ui.update_idletasks()

    msg = f'Checking if the provided credentials are correct:'
    logger.info(msg)
    glb_o.main_ui.append_to_output(msg, True)
    glb_o.main_ui.update_idletasks()

    # Validating the credentials for the backup server and vCenter
    if glb_v.backup_server_type == 'NetWorker':
        msg = 'NetWorker is the backup software and all inputs have been provided'
        logger.info(msg)
        # preform a validation check and get the resultant response
        nw_credentials_valid = validate_nw_credentials()
        vcenter_credentials_valid = validate_vcenter_credentials()

        # check to see if the validation check of the credentials for NW were successful
        if nw_credentials_valid:
            msg = 'NetWorker server credentials valid'
            logger.info(msg)
            glb_o.main_ui.append_to_output(msg, True)
            glb_o.main_ui.backup_verified_label.config(text=msg)
            glb_o.main_ui.update_idletasks()

        # Check if the vCenter server credentials were valid
        if vcenter_credentials_valid:
            msg = 'vCenter server credentials are valid'
            logger.info(msg)
            glb_o.main_ui.append_to_output(msg, True)
            glb_o.main_ui.vcenter_verified_label.config(text=msg)
            glb_o.main_ui.update_idletasks()

        # Check if both backup and vCenter server credentials are valid, enable the buttons
        if nw_credentials_valid and vcenter_credentials_valid:
            msg = f'Both NetWorker server {glb_o.main_ui.backup_server_input.get()} ' \
                  f'and vCenter server {glb_o.main_ui.vcenter_server_input.get()} ' \
                  f'credentials are valid - enabling the buttons on the GUI'
            logger.info(msg)
            glb_o.main_ui.button_get_vms.configure(state='active')
            glb_o.main_ui.button_validate_vms.configure(state='active')
            glb_o.main_ui.update_idletasks()

        else:
            msg = 'Please check that the server type, the associated FQDN, username and password are correct'
            logger.error(f'{msg} for server: {glb_o.main_ui.backup_server_input.get()}')
            glb_o.main_ui.button_get_vms.configure(state='disabled')
            glb_o.main_ui.button_validate_vms.configure(state='disabled')
            if not nw_credentials_valid:
                glb_o.main_ui.backup_verified_label.config(text='No')
            if not vcenter_credentials_valid:
                glb_o.main_ui.vcenter_verified_label.config(text='No')
            glb_o.main_ui.update_idletasks()

    # Confirm that PowerProtect Data Manager has been selected
    elif glb_v.backup_server_type == 'PowerProtect Data Manager':
        msg = 'PowerProtect Data Manager is the backup software and all inputs have been provided'
        logger.info(msg)
        # Obtain the authentication token to preform a validation check and get the resultant token response
        ppdm_credentials_valid = validate_ppdm_credentials()
        vcenter_credentials_valid = validate_vcenter_credentials()

        # check to see if the validation check of the credentials for PPDM were successful
        if ppdm_credentials_valid:
            msg = 'PowerProtect Data Manager server credentials valid'
            logger.info(msg)
            glb_o.main_ui.append_to_output(msg, True)
            glb_o.main_ui.backup_verified_label.config(text=msg)
            glb_o.main_ui.update_idletasks()

        # Check if the vCenter server credentials were valid
        if vcenter_credentials_valid:
            msg = 'vCenter server credentials are valid'
            logger.info(msg)
            glb_o.main_ui.append_to_output(msg, True)
            glb_o.main_ui.vcenter_verified_label.config(text=msg)
            glb_o.main_ui.update_idletasks()

        # Check if both backup and vCenter server credentials are valid, enable the buttons
        if ppdm_credentials_valid and vcenter_credentials_valid:
            msg = f'Both PowerProtect Data Manager server {glb_o.main_ui.backup_server_input.get()} ' \
                  f'and vCenter server {glb_o.main_ui.vcenter_server_input.get()} ' \
                  f'credentials are valid - enabling the buttons on the GUI'
            logger.info(msg)
            glb_o.main_ui.button_get_vms.configure(state='active')
            glb_o.main_ui.button_validate_vms.configure(state='active')
            glb_o.main_ui.update_idletasks()

        else:
            msg = 'Please check that the server type, the associated FQDN, username and password are correct'
            logger.error(f'{msg} for server: {glb_o.main_ui.backup_server_input.get()}')
            glb_o.main_ui.button_get_vms.configure(state='disabled')
            glb_o.main_ui.button_validate_vms.configure(state='disabled')
            if not ppdm_credentials_valid:
                glb_o.main_ui.backup_verified_label.config(text='No')
            if not vcenter_credentials_valid:
                glb_o.main_ui.vcenter_verified_label.config(text='No')
            glb_o.main_ui.update_idletasks()

    else:
        msg = 'Unable to determine the backup server type, please check the backup server FQDN. ' \
              'Currently only NetWorker and PowerProtect Data Manager are supported with this utility.'
        logger.info(msg)
        glb_o.main_ui.append_to_output(msg, True)
        glb_o.main_ui.update_idletasks()


def check_for_empty_inputs():
    """
    Check if the input fields contain information, before the credentials can be validated
    """
    msg = 'Checking for empty inputs, before credential validation can continue'
    logger.info(msg)

    # Iterate through the list of input values to determine if they are empty or not
    for item in glb_o.main_ui.input_list:
        value = item.get()
        if value == '':
            msg = f'No information was provided for - {item.winfo_name()}'
            logger.info(msg)
            glb_o.main_ui.append_to_output(msg, True)
            glb_o.main_ui.update_idletasks()
            glb_o.main_ui.number_empty_fields += 1

    # Set the variable to True if there are no empty input fields
    if glb_o.main_ui.number_empty_fields == 0:
        glb_o.main_ui.all_inputs_provided = True
        msg = 'All inputs have been entered into the text fields'
        logger.info(msg)
    else:
        msg = '\nAs one of more inputs were left empty, validation cannot continue \n' \
              'Provide information to the above listed field/s'
        logger.error(msg)
        glb_o.main_ui.append_to_output(msg, True)
        glb_o.main_ui.update_idletasks()
        # Reset the counter
        glb_o.main_ui.number_empty_fields = 0


def validate_nw_credentials() -> bool:
    """
    Validate the credentials of the backup server - NetWorker
    """

    # Extract the backup server information and credentials from the user input on the GUI
    glb_o.nw_server.fqdn = glb_o.main_ui.backup_server_input.get()
    glb_o.nw_server.user = glb_o.main_ui.backup_user_input.get()
    glb_o.nw_server.password = glb_o.main_ui.backup_pass_input.get()
    msg = 'Extracting the input data from the NetWorker backup server'
    logger.info(msg)

    # Make an API call to NetWorker to see fi the credentials are correct
    nw_response = glb_o.nw_server.get_alerts()

    if nw_response != 'API call failed':
        msg = 'Rest API call to NetWorker successful'
        logger.info(msg)
        glb_o.main_ui.append_to_output(msg, True)
        glb_o.main_ui.update_idletasks()
        glb_o.nw_server.api_call_success = True
        return True
    else:
        msg = 'The NetWorker server credentials and/or FQDN provided are not correct.\n' \
              'Please check that the correct information has been provided for NetWorker.\n' \
              'Review the debug log file that is located in the log directory where this utility is run from.'
        logger.info(msg)
        glb_o.main_ui.append_to_output(msg, True)
        glb_o.main_ui.update_idletasks()
        glb_o.nw_server.api_call_success = False
        return False


def validate_ppdm_credentials() -> bool:
    """
    Validate the credentials of the backup server - PowerProtect Data Manager
    """

    # Extract the backup server information and credentials from the user input on the GUI
    glb_o.ppdm_server.fqdn = glb_o.main_ui.backup_server_input.get()
    glb_o.ppdm_server.user = glb_o.main_ui.backup_user_input.get()
    glb_o.ppdm_server.password = glb_o.main_ui.backup_pass_input.get()
    msg = 'Extracting the input data for the PowerProtect Data Manager backup server'
    logger.info(msg)

    # Make an API call to NetWorker to see fi the credentials are correct
    ppdm_response = glb_o.ppdm_server.authenticate_api_call()

    if ppdm_response != 'API call failed':
        msg = 'Rest API call to PowerProtect Data Manager successful'
        logger.info(msg)
        glb_o.main_ui.append_to_output(msg, True)
        glb_o.main_ui.update_idletasks()
        glb_o.ppdm_server.api_call_success = True
        glb_o.ppdm_server.token = ppdm_response['access_token']
        glb_o.ppdm_server.refresh_token = ppdm_response['refresh_token']
        return True
    else:
        msg = 'The PowerProtect Data Manager server credentials and/or FQDN provided are not correct.\n' \
              'Please check that the correct information has been provided for PowerProtect Data manager.\n' \
              'Review the debug log file that is located in the log directory where this utility is run from.'
        logger.info(msg)
        glb_o.main_ui.append_to_output(msg, True)
        glb_o.main_ui.update_idletasks()
        glb_o.ppdm_server.api_call_success = False
        return False


def validate_vcenter_credentials() -> bool:
    """
    Validate the credentials of vCenter server
    """

    # Extract the vcenter server information and credentials from the user input on the GUI
    glb_o.vcenter_server.fqdn = glb_o.main_ui.vcenter_server_input.get()
    glb_o.vcenter_server.user = glb_o.main_ui.vcenter_user_input.get()
    glb_o.vcenter_server.password = glb_o.main_ui.vcenter_pass_input.get()
    msg = 'Extracting the input data from the vCenter server'
    logger.info(msg)

    # Refresh the access token for vCenter
    vcenter_response = glb_o.vcenter_server.authenticate_api_call()

    if vcenter_response != 'API call failed':
        msg = 'API Call to vCenter successfully made'
        logger.info(msg)
        glb_o.main_ui.append_to_output(msg, True)
        glb_o.main_ui.update_idletasks()
        glb_o.vcenter_server.connection_success = True
        return True


def get_list_protected_vms():
    """
    This function will extract the list of all protected VMs from the backup server and save it to a file.
    """

    if glb_v.backup_server_type == 'NetWorker':

        # Get the protected VMs JSON response from NetWorker server
        glb_o.nw_server.protected_vms_json = glb_o.nw_server.get_protected_vms(glb_o.vcenter_server.fqdn)

        # Store the protected VMs names to the NetWorker object
        if glb_o.nw_server.protected_vms_json != 'API call failed':
            glb_o.nw_server.protected_vms_names = \
                nw_process_json.get_protected_vms_names(glb_o.nw_server.protected_vms_json)

        # Output the data to a text file
        complete_path = os.path.join(glb_o.main_ui.directories_output_path.get(),
                                     f'Protected vms by {glb_o.nw_server.fqdn} for {glb_o.vcenter_server.fqdn}.txt')
        file.write_list(complete_path, glb_o.nw_server.protected_vms_names)
        msg = f'Protected VMs written to {complete_path}'
        logger.info(msg)
        glb_o.main_ui.write_to_output(msg)
        glb_o.main_ui.update_idletasks()

    elif glb_v.backup_server_type == 'PowerProtect Data Manager':

        # Refresh the access token
        ppdm_response = glb_o.ppdm_server.refresh_token_api_call()

        glb_o.ppdm_server.token = ppdm_response['access_token']

        # Get the protected VMs JSON response from PowerProtect Data Manager server
        glb_o.ppdm_server.protected_vms_json = glb_o.ppdm_server.get_protected_vms()

        # Store the protected VMs names to the NetWorker object
        if glb_o.ppdm_server.protected_vms_json != 'API call failed':
            glb_o.ppdm_server.protected_vms_names_id = \
                ppdm_process_json.get_protected_vms_names_by_vcenter(glb_o.ppdm_server.protected_vms_json,
                                                                     glb_o.vcenter_server.fqdn)

        # Output the data to a text file
        complete_path = os.path.join(glb_o.main_ui.directories_output_path.get(),
                                     f'Protected vms by {glb_o.ppdm_server.fqdn} for {glb_o.vcenter_server.fqdn}.txt')
        file.write_dict_key(complete_path, glb_o.ppdm_server.protected_vms_names_id)
        msg = f'Protected VMs written to {complete_path}'
        logger.info(msg)
        glb_o.main_ui.write_to_output(msg)
        glb_o.main_ui.update_idletasks()


def validate_vms():
    """
    This is the function that is run when the 'Validate VM' button is pressed on the UI
    """

    if glb_v.backup_server_type == 'NetWorker':
        msg = 'Validating NetWorker VMs'
        logger.info(msg)
        # Commence processing the NetWorker VMs for validation by resetting some values first
        glb_o.nw_server.vm_successfully_processed = 0
        glb_o.nw_server.validation_summary = []

        # Create the output file that will contain an audit of the VM validation
        glb_v.output_file = file.create_datetime_file(glb_o.main_ui.directories_output_path.get(),
                                                      '-VM validation output.txt')

        # Extract the VM backup information via API calls to NetWorker and process the JSON responses accordingly
        nw_logic.extract_vm_backup_information()

        # For each detected VM, perform instant access to validate if VM tools will start
        nw_logic.process_each_vm_via_instant_access()

    elif glb_v.backup_server_type == 'PowerProtect Data Manager':
        msg = 'Validating PowerProtect Data Manager VMs'
        logger.info(msg)
        # Commence processing the PowerProtect Data Manager VMs for validation by resetting some values first
        glb_o.ppdm_server.vm_successfully_processed = 0
        glb_o.ppdm_server.validation_summary = []

        # Create the output file that will contain an audit of the VM validation
        glb_v.output_file = file.create_datetime_file(glb_o.main_ui.directories_output_path.get(),
                                                      '-VM validation output.txt')

        # Extract the VM backup information via API calls to PPDM and process the JSON responses accordingly
        ppdm_logic.extract_vm_backup_information()

        # For each detected VM, perform instant access to validate if VM tools will start
        ppdm_logic.process_each_vm_via_instant_access()

    # Summary of VM validation
    msg = f'Successfully validated {glb_o.vm.vm_successfully_processed} ' \
          f'of {glb_o.vm.total_vms_to_process} VMs'
    logger.info(msg)
    file.append_datetime_prefix(glb_v.output_file, msg)
    glb_o.main_ui.append_to_output(msg, True)
    glb_o.main_ui.update_idletasks()
    for item in glb_o.vm.validation_summary:
        glb_o.main_ui.append_to_output(str(item), True)
        glb_o.main_ui.update_idletasks()
    file.append_list(glb_v.output_file, glb_o.vm.validation_summary)
