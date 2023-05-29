""""
This file is used to process JSON responses from PowerProtect Data Manager

Written by Mike van der Steen
Version 1.00

last updated: 30 December 2022
"""
import pathlib
import os
import json

from utils import log, file
from utils import globals as glb
from core.vmware import vcenter_api_calls

logger = log.custom_logger()


def get_protected_vms_names_by_vcenter(data: str, vcenter: str) -> dict:
    """
    Extract information from the PowerProtect Data Manager and Get Protected VMs names only form the JSON response
    filtering on the vcenter server provided
    """
    # List of protected VMs to be written to text files
    protected_vms = {}
    vm_count = 0

    # Getting the number of VMs
    try:
        vm_count = data['page']['totalElements']
        msg = f'Number of current reported protected VMs by PowerProtect Data Manager: {vm_count}'
        logger.info(msg)

    except Exception as e:
        msg = 'Unable to obtain the number of current protected VMs by PowerProtect Data Manager from JSON response'
        logger.error(msg)
        logger.debug(str(e))

    # If there is one or more protected VMs, extract the VM name and the associated href for each VM
    if vm_count >= 1:
        try:
            vms = data['content']
            for item in vms:
                if item:       # checking to see if an entry is empty, if so, skip to the next entry
                    try:
                        if item['details']['vm']['vcenterName'] == vcenter:
                            vm_name = item['name']
                            vm_id = item['id']
                            protected_vms[vm_name] = vm_id
                    except Exception as e:
                        logger.error(f'Unable to retrieve Key Value Pair for {item}')
                        logger.debug(str(e))
            msg = 'Finished processing protected VM names'
            logger.info(msg)
            return protected_vms

        except Exception as e:
            msg = 'Unable to extract protected VMs from PowerProtected Data Manager from JSON response'
            logger.error(msg)
            logger.debug(str(e))


def get_latest_backup_id(data: str) -> str:
    """
    Extract information from the PowerProtect Data Manager and get the latest backup copy ID
    """

    try:
        latest_backup = data['content'][0]['id']
        msg = 'Finished processing protected VM names'
        logger.info(msg)
        return latest_backup

    except Exception as e:
        logger.error(f'Unable to retrieve latest backup copy id')
        logger.debug(str(e))


def get_instant_access_payload_data(data: dict, backup_id: str) -> str:
    """
    Extract the required information to build the JSON data for an instant access recovery
    """

    try:
        # Get the dataCenterMoref and clusterMoref from vCenter API calls as this information is not included in
        # the asset ID json output unfortunately
        datacenter_name = data['details']['vm']['datacenter']
        datacenter = ''
        cluster_name = data['details']['vm']['clusterName']
        cluster = ''

        # Obtain the vCenter authentication value
        authentication_value = vcenter_api_calls.authenticate_api_call(glb.vcenter_server.fqdn,
                                                                       glb.vcenter_server.user,
                                                                       glb.vcenter_server.password)

        # Get the datacenter json response and process it to find the datacentreMoref value
        # **** May need to modify this section of code to be able to process the json response if
        # there are multiple datacenters ****
        datacenter_response = vcenter_api_calls.get_datacenter_json(glb.vcenter_server.fqdn,
                                                                    authentication_value)
        if datacenter_response['value'][0]['name'] == datacenter_name:
            datacenter = datacenter_response['value'][0]['datacenter']
        else:
            msg = f'Unable to obtain the datacenterMoref value for datacenter {datacenter_name}'
            logger.error(msg)

        # Get the cluster json response and process it to find the clusterMoref value and
        # skip API call if cluster value is null
        # **** May need to modify this section of code to be able to process the json response if
        # there are multiple clusters ****
        if cluster_name == 'null':
            cluster = ''
        else:
            cluster_response = vcenter_api_calls.get_clusters_json(glb.vcenter_server.fqdn,
                                                                   authentication_value)
            if cluster_response['value'][0]['name'] == cluster_name:
                datacenter = cluster_response['value'][0]['cluster']
            else:
                msg = f'Unable to find the clusterMoref value for cluster name {cluster_name}'
                logger.error(msg)

        # data_center = "datacenter-10035"
        # cluster = ""

        vm = data['name']
        vm_ia = f'{vm}_ia'
        desc = f'Instant Access recovery of VM {vm} being attempted with target name of {vm_ia}'
        vc_id = data['details']['vm']['inventorySourceId']
        esx_host_data = str(data['details']['vm']['hostMoref'])
        esx_host = esx_host_data.split(':', 1)[1]
        data_store_data = data['details']['vm']['datastore'][0]['datastoreMoref']
        data_store = data_store_data.split(':', 1)[1]

        payload = json.dumps({"description": desc,
                   "copyId": backup_id,
                   "restoreType": "INSTANT_ACCESS",
                   "restoredCopiesDetails": {
                       "targetVmInfo": {
                           "inventorySourceId": vc_id,
                           "vmName": vm_ia,
                           "dataCenterMoref": datacenter,
                           "clusterMoref": cluster,
                           "hostMoref": esx_host,
                           "dataStoreMoref": data_store,
                           "vmPowerOn": 'true',
                           "vmReconnectNic": 'false'}}})
        return payload

    except Exception as e:
        msg = f'Unable to extract information for instant access recovery of vm {vm}'
        logger.error(msg)
        logger.debug(str(e))
