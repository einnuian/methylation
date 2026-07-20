import tkinter as tk
from tkinter import filedialog

class Browser:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.file_path = filedialog.askopenfilename(
                title='Select A File',
                filetypes=[('csv files', "*.csv")] # '*.csv' = any_name.csv
                )

        if self.file_path:
            print("Selected file:", self.file_path)
        else:
            print("No file selected.")