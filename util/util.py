import pandas as pd
import tkinter as tk
import platform
from tkinter import filedialog
import statistics
from collections import defaultdict

class Helper:
            
    # Filter out controls according to targets
    def filter_ctrl_by_target(df, target):
        target_m = target.upper() + "_M"
        target_um = target.upper() + "_UM"
        control_df = df[(df["Target"].isin([target_m, target_um])) & 
                        (df["Sample"].str.contains("control", case=False))]
        return control_df
    
    """
    Identify the unique existing targets dynamically

    Args:
        df: the panda dataframe to be processed

    Return:
        target_pairs: dict with base names as keys and pairs of target as values
    """
    def make_target_pairs(df):
        target_list = df["Target"].unique()
        if len(target_list) % 2 != 0:
            raise ValueError("Number of unique targets must be even.")

        # Dictionary to hold pairs
        target_pairs = defaultdict(list)

        # Group target by base name (i.e. "ICR1")
        for target in target_list:
            base = target.split("_")[0] # Get the base name of the target
            target_pairs[base].append(target)

        return target_pairs
    
    """
    Transform the given df to calculate and add the dEqCq column

    Args:
        df: the panda dataframe to be processed
        m_target: name of the methylated target
        um_target: name of the unmethylated target

    Return:
        pivoted: the transformed dataframe
    """
    def add_deqcq(df, m_target, um_target):
        target_df = df[df["Target"].isin([m_target, um_target])]
        pivoted = target_df.pivot(index=["Sample", "Well", "Well Position"], 
                                  columns="Target", 
                                  values="Cq").reset_index() # Move Sample and Well back into the dataframe
        pivoted["dEqCq"] = pivoted[m_target] - pivoted[um_target] #Assuming the endogenous control is UM
        pivoted = pivoted.sort_values("Well")
        return pivoted
    
    """
    Find the mean dEqCq values by target given a data frame
    """
    def calculate_mean_deqcq(df):
        pass
    
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

        #TODO: Check for data with high standard deviation 

        to_omit = -1
        for key, value in std_dict.items():
            if value == min_val: 
                to_omit = key
                break
        return to_omit
    
    """
    Find outliers to be omitted for each set of technical replicates according to the target

    Args:
        df (DataFrame):     pandas dataframe to be processed
        m_target (string):  name of the methylated target
        um_target (string): name of the unmethylated target
    
    Returns:
        omitted_wells (list): list of positions of wells to be omitted
    """
    def wells_to_omit(df, m_target, um_target):
        new_df = Helper.add_deqcq(df, m_target, um_target)

        omitted_wells = []

        for i in range(0, len(new_df), 4):
            val_1 = new_df["dEqCq"].iloc[i]
            val_2 = new_df["dEqCq"].iloc[i+1]
            val_3 = new_df["dEqCq"].iloc[i+2]
            val_4 = new_df["dEqCq"].iloc[i+3]

            outlier = Helper.find_outliers(val_1, val_2, val_3, val_4)

            # Check if find_outliers detected a stdev >= 3%
            if outlier >= 4:
                print("Warning: ", new_df["Sample"].iloc[i], " has a standard deviation of ", outlier, "%% among its replicates" )
                omitted_wells.append("X")
            else:
                to_omit = new_df["Well Position"].iloc[outlier + i]
                omitted_wells.append(to_omit)
            #Omit from the original table
            #target_df = target_df[~(df["Well"] == to_omit)]

        return(omitted_wells)