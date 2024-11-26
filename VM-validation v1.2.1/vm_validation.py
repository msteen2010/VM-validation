#!/usr/bin/env python3
"""
This script performs validation of VM backups by performing instant access recovery, starting the VM and
checking for the status of VMtools

author: Mike van der Steen
last updated: 31 July 2023
"""

from utils import log, script
from utils import global_objects as glb_o

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
    glb_o.main_ui.mainloop()


if __name__ == "__main__":

    logger.info('Starting the validation script')
    # Run main function
    main()
