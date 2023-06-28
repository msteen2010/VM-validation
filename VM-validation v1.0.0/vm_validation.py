#!/usr/bin/env python3
"""
This script performs validation of VM backups by performing instant access recovery, starting the VM and
checking for the status of VMtools

Written by Mike van der Steen
Version 1.00

Last updated 28 June 2023
"""


from utils import log, script
from utils import globals as glb


logger = log.custom_logger()


def main():
    """
    This is the main function that will start the GUI and all actions will be performed from the GUI
    """

    # Load the welcome script to the main output text box of the UI
    script.welcome()

    # Run the main UI and loop through it for the duration of the application
    msg = 'Starting the main gui window'
    logger.info(msg)
    glb.main_ui.mainloop()


if __name__ == "__main__":

    # Configure the logger
    logger = log.custom_logger()
    logger.info('Starting the validation script')

    # Run main function
    main()
