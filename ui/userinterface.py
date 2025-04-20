import tkinter as tk
from tkinter import filedialog
from processor.processor import Processor

class UserInterface:
    def __init__(self, processor:Processor):
        self.processor = processor

    def start(self):
        # Ask the user for the type of methylation test
        test = ""
        while True:
            test = input("Enter BWS or RSS:")
            test = test.upper()
            if test in ["BWS", "RSS"]: break
            else: print("Invalid test.")

        target_1_to_omit = []
        target_2_to_omit = []
        if test == "BWS":
            target_1_to_omit = self.processor.process_ICR1()
            target_2_to_omit = self.processor.process_ICR2()
            print("--------ICR1--------\n", target_1_to_omit)
            print("--------ICR2--------\n", target_2_to_omit)
        elif test == "RSS":
            target_1_to_omit = self.processor.process_GRB()
            target_2_to_omit = self.processor.process_PEG()
            print("--------GRB--------\n", target_1_to_omit)
            print("--------PEG--------\n", target_2_to_omit)

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