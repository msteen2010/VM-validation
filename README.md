# VM-validation

Welcome to the VM image backup validation utility.

This utility currently supports NetWorker (NW) and PowerProtect Data Manager (PPDM) backup applications.  Credentials for both the backup server and vCenter are required to validate VM backups and is performed through VM Instant Access recovery of the latest VM backup for VMs provided in a list. The VM is then powered on through vCenter or by the backup recovery process and the utility will monitor the status of VMtools until it is running.

This utility will determine if a backup of a VM in valid if the VMtools is running during the instant access recovery.

This utility requires the following information:
1. Credentials for the backup server with an account that has recovery permission.
2. Credentials for the VMware vCenter server with an account that has read only role, plus power on VM.
3. A text file with a list of VMs to be validated.

Please note that VMtools must be installed on the VM for the validation to be completed.

config.ini file needs to exist in the root directory where the vm_validation.py or vm_validation-v1.2.0.exe distribution if run from.

This config.ini file contains the following options:

![image](https://github.com/msteen2010/VM-validation/assets/50894364/4dbee04b-0ed7-413c-b1e9-f3fc9046f0c7)

A Windows based executable has been created using pyinstaller and will present the following screen after a few seconds

![image](https://github.com/msteen2010/VM-validation/assets/50894364/1ccb5f76-3086-421f-a8af-9925d7b5041b)

Provide the required credentials, output directory and text file that contains the list of VMs to validation. Please note that the names of the VMs as they are regestered in VMware is case sensetive. 

If you are not sure of the correct spelling of the VMs, select a blank text file for the VMs to be validated, validate the credentials and once successful, select 'Get list of all protected VM' and open this text file from the output directory.  Then copy the required VMs from this list to your 'VM validation list'.
