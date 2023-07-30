"""
This file is used to process JSON responses from NetWorker

author: Mike van der Steen
last updated: 31 July 2023
"""

import os

from utils import log, file
from utils import global_objects as glb_o

logger = log.custom_logger()


def get_alerts(data: str) -> list:
    """
    Extract information from the NetWorker Get Alerts JSON response
    """
    # List of alert messages to be written to text files
    alert_messages = []
    alert_count = 0

    # Getting the number of alerts
    try:
        alert_count = data['count']
        msg = f'Number of current reported alerts for NetWorker: {alert_count}'
        logger.info(msg)

    except Exception as e:
        msg = 'Unable to obtain the number of current alerts for NetWorker from JSON response'
        logger.error(msg)
        logger.debug(str(e))

    # If there is one or more alerts present, extract the messages from the JSON response
    if alert_count >= 1:
        msg = f'Found {alert_count} alerts for NetWorker'
        logger.info(msg)
        try:
            alerts = data['alerts']
            for item in alerts:
                if not item:       # checking to see if an entry is empty, if so, skip to the next entry
                    pass
                else:
                    try:
                        text = item['message']
                        msg = 'Alert: ' + text.strip()
                        logger.info('Alert: ' + msg)
                        alert_messages.append(msg)
                    except Exception as e:
                        logger.error(f'Unable to retrieve Key Value Pair for {item}')
                        logger.debug(str(e))

            # Output the data to a text file
            complete_path = os.path.join(glb_o.main_ui.directories_output_path.get(),
                                         'NetWorker_alerts.txt')
            file.write_list(complete_path, alert_messages)
            return alert_messages

        except Exception as e:
            msg = 'Unable to extract messages from alerts for NetWorker from JSON response'
            logger.error(msg)
            logger.debug(str(e))


def get_protected_vms_names(data: str) -> list:
    """
    Extract information from the NetWorker Get Protected VMs names only form the JSON response
    """
    # List of protected VMs to be written to text files
    protected_vms = []
    vm_count = 0

    # Getting the number of VMs
    try:
        vm_count = data['count']
        msg = f'Number of current reported protected VMs by NetWorker: {vm_count}'
        logger.info(msg)

    except Exception as e:
        msg = 'Unable to obtain the number of current protected VMs by NetWorker from JSON response'
        logger.error(msg)
        logger.debug(str(e))

    # If there is one or more protected VMs, extract the VM name and the associated href for each VM
    if vm_count >= 1:
        try:
            vms = data['vms']
            for item in vms:
                if item:       # checking to see if an entry is empty, if so, skip to the next entry
                    try:
                        vm_name = item['name']
                        protected_vms.append(vm_name)
                    except Exception as e:
                        logger.error(f'Unable to retrieve Key Value Pair for {item}')
                        logger.debug(str(e))
            msg = 'Finished processing protected VM names'
            logger.info(msg)
            return protected_vms

        except Exception as e:
            msg = 'Unable to extract protected VMs from NetWorker from JSON response'
            logger.error(msg)
            logger.debug(str(e))


def get_protected_vms_href(data: str) -> dict:
    """
    Extract information from the NetWorker Get Protected VMs and associated href information from JSON response
    """
    # List of protected VMs to be written to text files
    protected_vms = {}
    vm_count = 0

    # Getting the number of VMs
    try:
        vm_count = data['count']
        msg = f'Number of current reported protected VMs for NetWorker: {vm_count}'
        logger.info(msg)

    except Exception as e:
        msg = 'Unable to obtain the number of current protected VMs for NetWorker from JSON response'
        logger.error(msg)
        logger.debug(str(e))

    # If there is one or more protected VMs, extract the VM name and the associated href for each VM
    if vm_count >= 1:
        try:
            vms = data['vms']
            for item in vms:
                if item:       # checking to see if an entry is empty, if so, skip to the next entry
                    try:
                        vm_name = item['name']
                        logger.info(vm_name)
                        vm_href = item['links'][0]['href']
                        logger.info(vm_href)
                        protected_vms[vm_name] = vm_href
                    except Exception as e:
                        logger.error(f'Unable to retrieve Key Value Pair for {item}')
                        logger.debug(str(e))
            return protected_vms

        except Exception as e:
            msg = 'Unable to extract protected VMs and associated href from NetWorker from JSON response'
            logger.error(msg)
            logger.debug(str(e))


def get_protected_vms_latest_backup_href(data: str) -> str:
    """
    Extract information from the NetWorker Get Protected VMs JSON response
    """
    # Set linkCount to 0 so that the while loop only reads the first restore link returned
    link_count = 0

    # If there is one or more protected VMs, extract the VM name and the associated href for each VM
    try:
        backups = data['backups']
        for item in backups:
            if item:        # Checking to see if an entry is empty, if so, skip to the next entry
                while link_count == 0:
                    try:
                        backup_href = item['links'][0]['href']
                        logger.info(backup_href)
                        link_count = 1
                        return backup_href
                    except Exception as e:
                        logger.error(f'Unable to retrieve Key Value Pair for {item}')
                        logger.debug(str(e))

    except Exception as e:
        msg = 'Unable to extract the latest backup href for the VM from JSON response'
        logger.error(msg)
        logger.debug(str(e))


def get_instant_access_restore_link(data: str) -> str:
    """
    Extract the restore link and build the JSON data for an instant access recovery to be requested
    The restore link that is needed is the Mount as this provides instant access recovery
    """

    # Loop through the restore links from the JSON data of the latest backup
    try:
        backup_json = data
        restore_links = data['links']
        for link in restore_links:
            if link['title'] == 'Recover':
                try:
                    vm_restore_link = link['href']
                    logger.info(vm_restore_link)
                    msg = f'The NetWorker restore link for the VM is: {vm_restore_link}'
                    logger.info(msg)
                    host = backup_json['vmInformation']['hostMoref']
                    dc = backup_json['vmInformation']['morefPath'].split('/')[1]
                    vm_name = backup_json['vmInformation']['vmName']
                    vcenter = backup_json['vmInformation']['vCenterHostname']
                    data = {"recoverMode": "Instant",
                            "datacenterMoref": dc,
                            "powerOn": "true",
                            "vmName": vm_name + "_ia",
                            "vCenterHostname": vcenter,
                            "hostMoref": host,
                            "reconnectNic": "false",
                            "clusterComputeResourceMoref": ""}
                    return vm_restore_link, data
                except Exception as e:
                    logger.error(f'Unable to retrieve recovery link for {link}')
                    logger.debug(str(e))

    except Exception as e:
        msg = 'Unable to extract the recovery href for the VM from JSON response'
        logger.error(msg)
        logger.debug(str(e))
