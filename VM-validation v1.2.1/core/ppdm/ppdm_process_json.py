"""
This file is used to process JSON responses from PowerProtect Data Manager

author: Mike van der Steen
last updated: 31 July 2023
"""

import json

from utils import log
from utils import global_objects as glb_o

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

    vm = ''

    try:
        # Get the dataCenterMoref and clusterMoref from vCenter API calls as this information is not included in
        # the asset ID json output unfortunately
        datacenter_name = data['details']['vm']['datacenter']
        logger.info(f'The datacenter name that the VM is associated with is {datacenter_name}')
        datacenter_id = ''
        cluster_name = data['details']['vm']['clusterName']
        logger.info(f'The cluster name that the VM is associated with is {cluster_name}')
        cluster_id = ''

        # Get the datacenter json response and process it to find the datacentreMoref value
        datacenter_response = glb_o.vcenter_server.get_datacenter_json()
        try:
            entry = datacenter_response['value']
            for item in entry:
                if item:       # checking to see if an entry is empty, if so, skip to the next entry
                    try:
                        if item['name'] == datacenter_name:
                            datacenter_id = item['datacenter']
                            logger.info(f'The datacenter name that the VM is associated with is {datacenter_id}')
                    except Exception as e:
                        logger.error(f'Unable to retrieve Key Value Pair for {item}')
                        logger.debug(str(e))
        except Exception as e:
            msg = f'Unable to obtain the datacenterMoref value for datacenter {datacenter_name}'
            logger.error(msg)
            logger.error(str(e))

        # Get the cluster json response and process it to find the clusterMoref value and
        if cluster_name == 'null':
            cluster_id = ''
        else:
            cluster_response = glb_o.vcenter_server.get_clusters_json()
            try:
                entry = cluster_response['value']
                for item in entry:
                    if item:  # checking to see if an entry is empty, if so, skip to the next entry
                        try:
                            if item['name'] == cluster_name:
                                cluster_id = item['cluster']
                                logger.info(f'The cluster name that the VM is associated with is {cluster_id}')
                        except Exception as e:
                            logger.error(f'Unable to retrieve Key Value Pair for {item}')
                            logger.debug(str(e))
            except Exception as e:
                msg = f'TUnable to obtain the datacenterMoref value for datacenter {cluster_name}'
                logger.error(msg)
                logger.error(str(e))

        # Creating the payload package for the instant access recovery
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
                                      "dataCenterMoref": datacenter_id,
                                      "clusterMoref": cluster_id,
                                      "hostMoref": esx_host,
                                      "dataStoreMoref": data_store,
                                      "vmPowerOn": True,
                                      "vmReconnectNic": False
                                  }
                              }
                              })
        return payload

    except Exception as e:
        msg = f'Unable to extract information for instant access recovery of vm {vm}'
        logger.error(msg)
        logger.debug(str(e))
