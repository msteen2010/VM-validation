"""
This file is used create the main GUI for this utility

author: Mike van der Steen
last updated: 31 July 2023
"""

import tkinter as tk
from tkinter import filedialog
from sys import exit

from core import core_logic
from utils import log
from utils import global_variables as glb_v

logger = log.custom_logger()
handler = logger.handlers[0]
logger_path = handler.baseFilename


class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        """
        group all the frames together to it makes it easier to understand
        """

        self.title('VMware VM Backup validation Utility v1.2.0')
        self.option_add('*font', 'Arial 9')

        # Label Frame configuration and layout
        self.backup_labelframe = tk.LabelFrame(text='Backup server and associated credentials', font='Arial 9')
        self.backup_labelframe.config(highlightbackground='red')
        self.vcenter_labelframe = tk.LabelFrame(text='vCenter server and associated credentials')
        self.directories_labelframe = tk.LabelFrame(text='Directories')
        self.progress_labelframe = tk.LabelFrame(text='Progress')
        self.button_labelframe = tk.LabelFrame(text='Options')
        self.output_labelframe = tk.LabelFrame(text='VM validation output')
        self.backup_labelframe.grid(row=0, column=0, sticky='NW', padx=5, pady=5, ipadx=5, ipady=5)
        self.vcenter_labelframe.grid(row=0, column=1, sticky='NW', padx=5, pady=5, ipadx=5, ipady=5)
        self.directories_labelframe.grid(row=1, column=0, columnspan=2, sticky='NW', padx=5, pady=5, ipadx=5, ipady=5)
        self.progress_labelframe.grid(row=1, column=2, sticky='NW', padx=5, pady=5, ipadx=5, ipady=5)
        self.button_labelframe.grid(row=0, column=2, sticky='NW', padx=5, pady=5, ipadx=5, ipady=5)
        self.output_labelframe.grid(row=2, column=0, columnspan=3, sticky='NW', padx=5, pady=5, ipadx=5, ipady=5)
        self.backup_labelframe.grid_propagate(True)
        self.vcenter_labelframe.grid_propagate(True)
        self.directories_labelframe.grid_propagate(True)
        self.progress_labelframe.grid_propagate(True)
        self.button_labelframe.grid_propagate(True)
        self.output_labelframe.grid_propagate(True)

        # Configure backup server and apply it to the respective frame
        self.backup_server_label = tk.Label(self.backup_labelframe, text='Server FQDN/IP:')
        self.backup_server_input = tk.Entry(self.backup_labelframe, width=40, name='backup server fqdn/ip')
        self.backup_user_label = tk.Label(self.backup_labelframe, text='Username:')
        self.backup_user_input = tk.Entry(self.backup_labelframe, width=40, name='backup server username')
        self.backup_pass_label = tk.Label(self.backup_labelframe, text='Password:')
        self.backup_pass_input = tk.Entry(self.backup_labelframe, width=40, show='*', name='backup server password')
        self.backup_verify_label = tk.Label(self.backup_labelframe, text='Credentials verified:')
        self.backup_verified_label = tk.Label(self.backup_labelframe, text='No')
        self.backup_server_label.grid(row=0, column=0, sticky='W', padx=5, pady=5)
        self.backup_server_input.grid(row=0, column=1, sticky='W', pady=5)
        self.backup_user_label.grid(row=1, column=0, sticky='W', padx=5, pady=5)
        self.backup_user_input.grid(row=1, column=1, sticky='W', pady=5)
        self.backup_pass_label.grid(row=2, column=0, sticky='W', padx=5, pady=5)
        self.backup_pass_input.grid(row=2, column=1, sticky='W', pady=5)
        self.backup_verify_label.grid(row=3, column=0, sticky='W', padx=5, pady=5)
        self.backup_verified_label.grid(row=3, column=1, sticky='W', padx=5, pady=5)

        # Configure vCenter server and apply it to the respective frame
        self.vcenter_server_label = tk.Label(self.vcenter_labelframe, text='Server FQDN/IP:')
        self.vcenter_server_input = tk.Entry(self.vcenter_labelframe, width=40, name='vcenter server fqdn/ip')
        self.vcenter_user_label = tk.Label(self.vcenter_labelframe, text='Username:')
        self.vcenter_user_input = tk.Entry(self.vcenter_labelframe, width=40, name='vcenter server username')
        self.vcenter_pass_label = tk.Label(self.vcenter_labelframe, text='Password:')
        self.vcenter_pass_input = tk.Entry(self.vcenter_labelframe, width=40, show='*', name='vcenter server password')
        self.vcenter_verify_label = tk.Label(self.vcenter_labelframe, text='Credentials verified:')
        self.vcenter_verified_label = tk.Label(self.vcenter_labelframe, text='No')
        self.vcenter_server_label.grid(row=0, column=0, sticky='W', padx=5, pady=5)
        self.vcenter_server_input.grid(row=0, column=1, sticky='W', pady=5)
        self.vcenter_user_label.grid(row=1, column=0, sticky='W', padx=5, pady=5)
        self.vcenter_user_input.grid(row=1, column=1, sticky='W', pady=5)
        self.vcenter_pass_label.grid(row=2, column=0, sticky='W', padx=5, pady=5)
        self.vcenter_pass_input.grid(row=2, column=1, sticky='W', pady=5)
        self.vcenter_verify_label.grid(row=3, column=0, sticky='W', padx=5, pady=5)
        self.vcenter_verified_label.grid(row=3, column=1, sticky='W', padx=5, pady=5)

        # Configure user directories and apply it to the respective frame
        self.directories_output_label = tk.Label(self.directories_labelframe, text='Output Directory:')
        self.directories_output_path = tk.Entry(self.directories_labelframe, width=95, name='output directory')
        self.directories_output_browse = tk.Button(self.directories_labelframe, text="Browse ...",
                                                   command=self.output_director)
        self.directories_vm_label = tk.Label(self.directories_labelframe, text='VM validation file:')
        self.directories_vm_path = tk.Entry(self.directories_labelframe, width=95, name='vm validation file')
        self.directories_vm_browse = tk.Button(self.directories_labelframe, text="Browse ...",
                                               command=self.vm_list_filename)
        self.directories_output_label.grid(row=0, column=0, sticky='W', padx=5, pady=5)
        self.directories_output_path.grid(row=0, column=1, sticky='W', pady=5)
        self.directories_output_browse.grid(row=0, column=2, sticky='W', padx=5, pady=5)
        self.directories_vm_label.grid(row=1, column=0, sticky='W', padx=5, pady=5)
        self.directories_vm_path.grid(row=1, column=1, sticky='W', pady=5)
        self.directories_vm_browse.grid(row=1, column=2, sticky='W', padx=5, pady=5)

        # Configure button and apply it to the respective frame
        self.button_validate = tk.Button(self.button_labelframe, text='Validate Credentials', width=24,
                                         command=core_logic.validation_of_credentials)
        self.button_get_vms = tk.Button(self.button_labelframe, text='Get List of all Protected VMs', width=24,
                                        command=core_logic.get_list_protected_vms, state='disabled')
        self.button_validate_vms = tk.Button(self.button_labelframe, text='Validate VMs', width=24,
                                             command=core_logic.validate_vms, state='disabled')
        self.button_quit = tk.Button(self.button_labelframe, text='Exit Utility', width=24, command=self.quit_utility)
        self.button_validate.grid(row=0, column=0, sticky='EW', padx=5, pady=5)
        self.button_get_vms.grid(row=1, column=0, sticky='EW', padx=5, pady=5)
        self.button_validate_vms.grid(row=2, column=0, sticky='EW', padx=5, pady=5)
        self.button_quit.grid(row=4, column=0, sticky='EW', padx=5, pady=5)

        # Configure Progress status and apply it to the respective frame
        self.progress_total_vms_label = tk.Label(self.progress_labelframe, text='Total number of VMs:')
        self.progress_total_vms_amount = tk.Label(self.progress_labelframe, text='')
        self.progressed_vms_label = tk.Label(self.progress_labelframe, text='Number of VMs processed:')
        self.progressed_vms_amount = tk.Label(self.progress_labelframe, text='')
        self.progress_total_vms_label.grid(row=0, column=0, sticky='W', padx=5, pady=5)
        self.progress_total_vms_amount.grid(row=0, column=1, sticky='E', padx=5, pady=5)
        self.progressed_vms_label.grid(row=1, column=0, sticky='W', padx=5, pady=5)
        self.progressed_vms_amount.grid(row=1, column=1, sticky='E', padx=5, pady=5)

        # Configure output and apply it to the respective frame
        self.output_screen = tk.Text(self.output_labelframe, height=glb_v.number_of_lines, width=146)
        self.vertical_scroll_bar = tk.Scrollbar(self.output_labelframe, orient='vertical',
                                                command=self.output_screen.yview)
        self.output_screen.configure(state='disabled', wrap='word', yscrollcommand=self.vertical_scroll_bar.set)
        self.output_screen.grid(row=0, column=0, sticky='NSEW', padx=5, pady=5)
        self.vertical_scroll_bar.grid(row=0, column=1, sticky='NES', padx=5, pady=5)

        # List of variables to be used by methods of this class
        self.input_list = [self.backup_server_input,
                           self.backup_user_input,
                           self.backup_pass_input,
                           self.vcenter_server_input,
                           self.vcenter_user_input,
                           self.vcenter_pass_input,
                           self.directories_output_path,
                           self.directories_vm_path]
        self.number_empty_fields = 0
        self.all_inputs_provided = False

    def append_to_output(self, msg: str, new_line: bool) -> None:
        """
        Output text sent to this function to the output text box on the GUI
        """
        # Enable the text box, print the msg content and this disable the text box
        self.output_screen.configure(state='normal')
        if new_line:
            self.output_screen.insert(tk.END, msg + '\n')
        else:
            self.output_screen.insert(tk.END, msg)
        self.output_screen.configure(state='disabled')
        # Autoscroll to the bottom
        self.output_screen.yview('end')

    def write_to_output(self, msg: str) -> None:
        """
        Output text sent to this function to the output text box on the GUI
        """
        # Reset the gui output window
        self.clear_output()
        # Enable the text box, print the msg content and this disable the text box
        self.output_screen.configure(state='normal')
        self.output_screen.insert(1.0, msg)
        self.output_screen.configure(state='disabled')
        # Autoscroll to the bottom
        self.output_screen.yview('end')

    def clear_output(self) -> None:
        """
        Clear the output text box of any content
        """
        # Delete all text from the output text box
        self.output_screen.configure(state='normal')
        self.output_screen.delete('1.0', tk.END)
        self.output_screen.configure(state='disabled')

    def vm_list_filename(self) -> None:
        """
        Get the full path for a file that contains the VMs to validate
        """
        # Clear the contents of the output_directory first, before the new location is selected
        self.directories_vm_path.delete(0, 'end')
        filename = filedialog.askopenfilename()
        self.directories_vm_path.insert(0, filename)
        msg = f'The location of the VM list to validate is: {filename}'
        logger.info(msg)

    def output_director(self) -> None:
        """
        Get the full path of the directory to output information about the VM validation
        """
        # Clear the contents of the output_directory first, before the new location is selected
        self.directories_output_path.delete(0, 'end')
        directory = filedialog.askdirectory()
        self.directories_output_path.insert(0, directory)
        msg = f'The location of the output directory is: {directory}'
        logger.info(msg)

    @staticmethod
    def quit_utility() -> None:
        """
        Closing the GUI and exiting the application
        """
        msg = 'Utility closed'
        logger.info(msg)
        exit(0)

    @staticmethod
    def close_window() -> None:
        """
        Exit the GUI when the Cross is pressed on the GUI
        """
        msg = 'Utility closed'
        logger.info(msg)
        exit(0)
