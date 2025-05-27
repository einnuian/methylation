import pandas as pd
import tkinter as tk
from tkinter import filedialog
from util.util import Helper
from collections import defaultdict

"""
Ask the user for the file to be processed
"""

def choose_file():
    # Hide the main tkinter window
    root = tk.Tk()
    root.withdraw()

    # Show the file dialog
    file_path = filedialog.askopenfilename(
                initialdir="/mnt/c/Users/Anh Nguyen/Documents/GUI Automation/DA2", 
                title='Select A File',
                filetypes=[('csv files', "*.csv")] # '*.csv' = any_name.csv
                )

    if file_path:
        print("Selected file:", file_path)
        # Now you can process this file
        return file_path
    else:
        print("No file selected.")
        return None

# Usage example
'''file = choose_file()
if file:
    # Do something with the file
    pass'''


#to print the whole dataframe
pd.set_option('display.max_rows', None)

df = pd.read_csv("results.csv", skiprows=22, usecols=["Well", "Well Position", "Omit", 
                                                      "Sample", "Target", 
                                                      "Cq", "Cq Mean", 
                                                      "Threshold"])
# Set "Undetermined" to 40 and cast Cq values to type float
df["Cq"] = df["Cq"].replace("Undetermined", 40)
df["Cq"] = pd.to_numeric(df["Cq"])
#print(df.dtypes)
#print(df.head(10))

def test_find_outliers(df):
    '''
    Find outliers for each sample in the df
    '''
    icr1_df = df[df["Target"].isin(["ICR1_M", "ICR1_UM"])]
    pivoted = icr1_df.pivot(index=["Sample", "Well", "Well Position"], columns="Target", values="Cq").reset_index() # Move Sample and Well back into the dataframe
    pivoted["dEqCq"] = pivoted["ICR1_M"] - pivoted["ICR1_UM"] #Assuming the endogenous control is UM
    pivoted = pivoted.sort_values("Well")
    #print(icr1_df)
    #print(pivoted)
    #print(len(pivoted))

    #print(len(icr1_df))

    omitted_wells = []

    for i in range(0, len(pivoted), 4):
        val_1 = pivoted["dEqCq"].iloc[i]
        val_2 = pivoted["dEqCq"].iloc[i+1]
        val_3 = pivoted["dEqCq"].iloc[i+2]
        val_4 = pivoted["dEqCq"].iloc[i+3]
        to_omit = pivoted["Well Position"].iloc[Helper.find_outliers(val_1, val_2, val_3, val_4) + i]
        omitted_wells.append(to_omit)
        #Omit from the original table
        icr1_df = icr1_df[~(df["Well"] == to_omit)]

    #print(icr1_df)
    #print(omitted_wells)

def test_make_target_list(df):
    '''
    Make list of target pairs
    '''
    target_list = df["Target"].unique()
    if len(target_list) % 2 != 0:
       raise ValueError("Number of unique targets must be even.")

    # Dictionary to hold pairs
    target_pairs = defaultdict(list)

    # Group target by base name (i.e. "ICR1")
    for target in target_list:
        base = target.split("_")[0] # Get the base name of the target
        target_pairs[base].append(target)

#test_make_target_list(df)

def test_mean_EqCq(df):
    mean_df = df.groupby("Sample")["Cq"].mean().reset_index()