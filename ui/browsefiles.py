import tkinter as tk
from tkinter import filedialog
from util.util import Helper

class Browser:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        # Detect the OS the program is running on
        os_type = Helper.detect_os()
        initial_dir = ""

        # Assuming that the user is running WSL and storing the file on the Window's file system
        if os_type == "Linux":
            username = input("Enter your Windows' username: ")
            initial_dir = "/mnt/c/Users/" + username
            print(initial_dir)
        else: pass


        self.file_path = filedialog.askopenfilename(
                initialdir=initial_dir, 
                title='Select A File',
                filetypes=[('csv files', "*.csv")] # '*.csv' = any_name.csv
                )

        if self.file_path:
            print("Selected file:", self.file_path)
        else:
            print("No file selected.")