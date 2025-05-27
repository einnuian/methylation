import pandas as pd
import statistics
from datamanagement.da_parser import DAParser
from util.util import Helper
from collections import defaultdict
from config import GLOBAL_STD_THRESHOLD

class Processor:
    def __init__(self, parser:DAParser):
        self.parser = parser
    
    def process(self):
        """
        Process the parsed dataframe and identify the wells to be omitted by target

        Return:
            omitted_wells: dict with targets as keys and list of wells be omitted as values
        """
        df = self.parser.readfile()
        target_pairs = Helper.make_target_pairs(df)

        omitted_wells = defaultdict(list)

        for key, value in target_pairs.items():
            target = Target(df, value[0], value[1])
            omitted_wells[key] = target.wells_to_omit()
        
        return(omitted_wells)
    

class Target:
    def __init__(self, orig_df: pd.DataFrame, m_target: str, um_target: str):
        self.orig_df = orig_df
        self.df = pd.DataFrame() # Empty df
        self.m_target = m_target
        self.um_target = um_target

    def transform_df(self):
        """
        Transform the original df to the desired df to be processed
        """
        # Retain only the target of interest
        self.df = self.orig_df[self.orig_df["Target"].isin([self.m_target, self.um_target])]

        # Remove Hela and NTC
        self.df = self.df[~self.df["Sample"].str.contains("Hela", case=False)]
        self.df = self.df [~self.df ["Sample"].str.contains("NTC", case=False)]

        # Pivot and add dEqCq column
        self.df = self.df.pivot(index=["Sample", "Well", "Well Position"], 
                                  columns="Target", 
                                  values="Cq").reset_index() # Move Sample and Well back into the dataframe
        self.df["dEqCq"] = self.df[self.m_target] - self.df[self.um_target] #Assuming the endogenous control is UM
        self.df = self.df.sort_values("Well")

        # Add mean dEqCq and std dEqCq
        self.df["dEqCq Mean"] = self.df.groupby("Sample")["dEqCq"].transform("mean")
        self.df["dEqCq Std"] = self.df.groupby("Sample")["dEqCq"].transform("std")
    
    def pick_reference_samples(self, median):
        """
        Pick three reference samples according to the delta EqCq median
        This function operates on df

        Args:
            median: median of all delta EqCq values

        Returns:
            reference: name of control with mean delta EqCq value closest to the overall median and valid stdev
        """
        # Retain only the controls
        ctrl_df = self.df[self.df["Sample"].str.contains("control", case=False)].copy() # .copy() avoids the SettingWithCopyWarning

        # Get the absolute difference from the median
        ctrl_df["Diff"] = abs(ctrl_df["dEqCq Mean"] - median)

        count = 0
        controls = []
        # Find the minimum difference
        while count < 3:
            if ctrl_df.empty:
                print("No valid controls")
                break

            closest_idx = ctrl_df["Diff"].idxmin()
            sample = ctrl_df.loc[closest_idx, "Sample"]

            # If standard deviation is too high, omit this sample and repeat
            if ctrl_df.loc[closest_idx, "dEqCq Std"] >= GLOBAL_STD_THRESHOLD:
                ctrl_df = ctrl_df[ctrl_df["Sample"] != sample]
            else:
                controls.append(ctrl_df.loc[closest_idx, "Sample"])
                ctrl_df = ctrl_df[ctrl_df["Sample"] != sample]
                count +=1

        return controls

    def wells_to_omit(self):
        """
        Find outliers to be omitted for each set of technical replicates according to the target

        Args:
            df (DataFrame):     pandas dataframe to be processed
            m_target (string):  name of the methylated target
            um_target (string): name of the unmethylated target
        
        Returns:
            omitted_wells (list): list of positions of wells to be omitted
        """
        self.transform_df()

        samples_list = self.df["Sample"].unique()

        # Calcuate the original median and mean of dEqCq
        # Check for skewness of the data
        original_median = self.df["dEqCq"].median()
        original_mean = self.df["dEqCq"].mean()
        #print("Median: ", original_median)
        skewness_percent = abs((original_median - original_mean) / original_median) * 100
        if original_mean >= 0.01 and original_median >= 0.01 and skewness_percent >= 10:
            print(f"Warning: The dEqCq values of target {self.m_target.split('_')[0]} are skewed by more than 10% from the median. Please examine the data before proceeding.")
        
        # Get the set of three controls
        controls = self.pick_reference_samples(original_median)
        print(controls)
        omitted_wells = []

        # Detect outliers
        for i in range(0, len(self.df), 4):
            values = [self.df["dEqCq"].iloc[i],
                      self.df["dEqCq"].iloc[i+1],
                      self.df["dEqCq"].iloc[i+2],
                      self.df["dEqCq"].iloc[i+3]]

            outlier = Helper.find_outliers(values, original_median)

            # Check if find_outliers detected a stdev >= 3%
            if outlier == -1:
                print(f"Warning: {self.df['Sample'].iloc[i]} has a standard deviation of {statistics.stdev(values)} among its {self.m_target.split('_')[0]} replicates" )
                omitted_wells.append("X")
            else:
                to_omit = self.df["Well Position"].iloc[outlier + i]
                omitted_wells.append(to_omit)
            #Omit from the original table
            #target_df = target_df[~(df["Well"] == to_omit)]

        return(omitted_wells)