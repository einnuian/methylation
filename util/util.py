import pandas as pd
import tkinter as tk
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
        to_omit = 0
        for key, value in std_dict.items():
            if value == min_val: 
                to_omit = key
                break
        return to_omit