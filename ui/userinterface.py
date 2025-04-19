import tkinter as tk
from tkinter import filedialog
from processor.processor import Processor

class UserInterface:
    def __init__(self, processor):
        self.processor = processor

    def start(self):
        '''
        # Ask the user for the endogenous control
        endo_ctrl = ""
        while True:
            endo_ctrl = input("Enter your endogenous control:\n"
                                "1M for ICR1_M\n"
                                "1UM for ICR1_UM\n"
                                "2M for ICR2_M\n"
                                "2UM for ICR2_UM\n")
        
            endo_ctrl = endo_ctrl.capitalize()
        
            if endo_ctrl is ["1M", "1UM", "2M", "2UM"]:
                break
            else:
                print("Invalid value. Please try again")
        '''
                
        # TODO: Call processor functions to calculate depending on the endogenous control

        # TODO: Display wells to omit