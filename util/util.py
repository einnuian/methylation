import pandas as pd
import tkinter as tk
import platform
from tkinter import filedialog
import statistics

class Helper:
    def __init__(self, df):
        self.df = df

    # Uses the data frame containing the controls and the given target (ICR1 or ICR2) to select the reference sample
    def select_reference_control(self, target):
        assert target in ("ICR1", "ICR2"), "Target must be ICR1 or ICR2" 
        if target == "ICR1":
            return 0
        elif target == "ICR2":
            return 0
            
    # Filter out controls according to targets
    def filter_ctrl_by_target(self, target):
        target_m = target.upper() + "_M"
        target_um = target.upper() + "_UM"
        control_df = self.df[(self.df["Target"].isin([target_m, target_um])) & 
                             (self.df["Sample"].str.contains("control", case=False))]
        return control_df
    
    """
    Find the outlier given four values

    Args:
        val_1 (float)
        val_2 (float)
        val_3 (float)
        val_4 (float)

    Returns:
        to_omit (int): the index of the value to omit such that the stdev is minimized
    """
    def find_outliers(val_1, val_2, val_3, val_4):
        std_1 = statistics.stdev([val_2, val_3, val_4]) #stdev does not contain well 1
        std_2 = statistics.stdev([val_1, val_3, val_4]) #stdev does not contain well 2
        std_3 = statistics.stdev([val_1, val_2, val_4]) #stdev does not contain well 3
        std_4 = statistics.stdev([val_1, val_2, val_3]) #stdev does not contain well 4
        std_dict = {0:std_1, 1:std_2, 2:std_3, 3:std_4}
        min_val = min(std_dict.values())

        '''
        # Check if the smallest stdev is >= 3%
        if min_val >= 3:
            return min_val + 1 # min_val + 1 will be distinct from the to_omit value
        '''

        to_omit = 0
        for key, value in std_dict.items():
            if value == min_val: 
                to_omit = key
                break
        return to_omit
    
    """
    Find outliers for each set of technical replicates according to the target

    Args:
        df (DataFrame):     pandas dataframe to be processed
        m_target (string):  name of the methylated target
        um_target (string): name of the unmethylated target
    
    Returns:
        omitted_wells (list): list of positions of wells to be omitted
    """
    def process(df, m_target, um_target):
        target_df = df[df["Target"].isin([m_target, um_target])]
        pivoted = target_df.pivot(index=["Sample", "Well", "Well Position"], columns="Target", values="Cq").reset_index() # Move Sample and Well back into the dataframe
        pivoted["dEqCq"] = pivoted[m_target] - pivoted[um_target] #Assuming the endogenous control is UM
        pivoted = pivoted.sort_values("Well")

        omitted_wells = []

        for i in range(0, len(pivoted), 4):
            val_1 = pivoted["dEqCq"].iloc[i]
            val_2 = pivoted["dEqCq"].iloc[i+1]
            val_3 = pivoted["dEqCq"].iloc[i+2]
            val_4 = pivoted["dEqCq"].iloc[i+3]

            outlier = Helper.find_outliers(val_1, val_2, val_3, val_4)

            # Check if find_outliers detected a stdev >= 3%
            if outlier >= 4:
                print("Warning: ", pivoted["Sample"].iloc[i], " has a standard deviation of ", outlier, "%% among its replicates" )
                omitted_wells.append("X")
            else:
                to_omit = pivoted["Well Position"].iloc[outlier + i]
                omitted_wells.append(to_omit)
            #Omit from the original table
            #target_df = target_df[~(df["Well"] == to_omit)]

        return(omitted_wells)
    
    def detect_os():
        os_type = platform.system()

        if os_type == "Windows":
            print("Running on Windows")
        elif os_type == "Linux":
            print("Running on Linux")
        elif os_type == "Darwin":
            print("Running on macOS")
        else:
            print("Running on unknown OS: {os_type}")

        return os_type