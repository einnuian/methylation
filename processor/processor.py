import pandas as pd
import statistics
from datamanagement.da_parser import DAParser
from util.util import Helper
from collections import defaultdict
from config import GLOBAL_RQ_DIFF_THRESHOLD, GLOBAL_STD_THRESHOLD

class Processor:
    def __init__(self, parser:DAParser):
        self.parser = parser
        self.omitted_wells = defaultdict(list)
        self.reference = defaultdict(str)
        self.controls = defaultdict(list)
    
    def process(self):
        """
        Process the parsed dataframe and identify the wells to be omitted by target

        Return:
            omitted_wells: dict with targets as keys and list of wells be omitted as values
        """
        df = self.parser.readfile()
        target_pairs = Helper.make_target_pairs(df)

        for key, value in target_pairs.items():
            target = Target(df, value[0], value[1])
            self.omitted_wells[key] = target.wells_to_omit()
            self.reference[key] = target.reference
            self.controls[key] = target.controls
    

class Target:
    def __init__(self, orig_df: pd.DataFrame, m_target: str, um_target: str):
        self.orig_df = orig_df
        self.df = pd.DataFrame() # Empty df
        self.m_target = m_target
        self.um_target = um_target
        self.target = f"{m_target.split('_')[0]}"
        self.reference: str
        self.controls = [] # List of controls to be used for the target
    
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

    def calculate_rq_diff(self, values):
        """
        Calculate the difference between Rq min and Rq max of a given sample (using one stdev)

        Args:
            values: list of dEqCq values

        Returns:
            diff: the absolute difference 
        """
        reference_mean = self.get_reference_meanEqCq()
        mean = statistics.mean(values)
        std = statistics.stdev(values)
        rq_min = 2**(mean-reference_mean-std)
        rq_max = 2**(mean-reference_mean+std)
        diff = abs(rq_max - rq_min)
        return diff
    
    def set_reference(self, median):
        """
        Pick the reference sample according to the delta EqCq median
        This function operates on self.df

        Args:
            median: median of all delta EqCq values

        Returns:
            reference: the selected reference control whose dEqCq mean is closest to the median
        """
        # Retain only the controls
        ctrl_df = self.df[self.df["Sample"].str.contains("control", case=False)].copy()
        
        # Get the absolute difference from the median
        ctrl_df["Diff"] = abs(ctrl_df["dEqCq Mean"] - median)

        # Find the minimum difference
        while True:
            closest_idx = ctrl_df["Diff"].idxmin()
            sample = ctrl_df.loc[closest_idx, "Sample"]

            # If standard deviation is too high, omit this sample and repeat
            if ctrl_df.loc[closest_idx, 'dEqCq Std'] >= GLOBAL_STD_THRESHOLD:
                ctrl_df = ctrl_df[ctrl_df['Sample'] != sample]
            else:
                break
        
        self.reference = sample

    def get_reference_meanEqCq(self):
        mean = self.df[self.df["Sample"] == self.reference]["dEqCq Mean"].values[0]
        return mean
    
    def pick_controls(self, df, median):
        """
        Pick three controls as reference according to the delta EqCq median
        This function operates on self.df

        Args:
            median: median of all delta EqCq values

        Returns:
            controls: list containing the three selected controls
        """
        # Retain only the controls
        ctrl_df = df[df["Sample"].str.contains("control", case=False)].copy() # .copy() avoids the SettingWithCopyWarning
        #ctrl_df.reset_index(drop=True)

        # Get the absolute difference from the median
        ctrl_df["Diff"] = abs(ctrl_df["dEqCq Mean"] - median)

        count = 0
        controls = []
        # Find the minimum difference
        while count < 3:
            if ctrl_df.empty:
                print(f"Target {self.target} has no valid controls")
                break

            closest_idx = ctrl_df["Diff"].idxmin()
            sample = ctrl_df.loc[closest_idx, "Sample"]

            # Calculate the RQ difference for the sample
            values = ctrl_df[ctrl_df['Sample'] == sample]['dEqCq'].tolist()
            rq_diff = self.calculate_rq_diff(values)

            # If RQ difference is too high, omit this sample and repeat
            if rq_diff > GLOBAL_RQ_DIFF_THRESHOLD:
                ctrl_df = ctrl_df[ctrl_df["Sample"] != sample]
                #print(f"Warning: {sample} from target {self.target} an RQ difference of {rq_diff}. Omitted.")
            else:
                controls.append(ctrl_df.loc[closest_idx, "Sample"])
                ctrl_df = ctrl_df[ctrl_df["Sample"] != sample]
                count +=1

        return controls

    def find_outliers(self, values:list, num):
        """
        Find the value from a list of values that has the biggest difference from a provided number while minimizing the RQ difference
        This function operates on self.df

        Args:
            values (list): list containing the values

        Returns:
            to_omit (int): the index of the value to omit
        """
        # Keep track of min difference
        min_diff = 100
        index = -1

        for i in range(len(values)):
            # New list that doesn't contain the current value
            new = values[:i] + values[i+1:]
            diff = abs(statistics.mean(new) - num)
            rq_diff = self.calculate_rq_diff(new)
            if diff < min_diff and rq_diff <= GLOBAL_RQ_DIFF_THRESHOLD:
                min_diff = diff       
                index = i
        return index

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
        original_median = self.df["dEqCq"].median()
        original_mean = self.df["dEqCq"].mean()
        
        #print("Median: ", original_median)
        #print("Mean: ", original_mean)

        # Check for skewness of the data
        skewness_percent = abs((original_median - original_mean) / original_median) * 100
        if original_mean >= 0.01 and original_median >= 0.01 and skewness_percent >= 10:
            print(f"Warning: The dEqCq values of target {self.target} are skewed by more than 10% from the median. Please examine the data before proceeding.")
        
        # Set the reference control first
        self.set_reference(original_median)

        # Detect outliers
        omitted_wells = []
        for i in range(0, len(self.df), 4):
            values = [self.df["dEqCq"].iloc[i],
                      self.df["dEqCq"].iloc[i+1],
                      self.df["dEqCq"].iloc[i+2],
                      self.df["dEqCq"].iloc[i+3]]

            outlier = self.find_outliers(values, original_median)

            # Check if find_outliers detected a high stdev
            if outlier == -1:
                print(f"Warning: {self.df['Sample'].iloc[i]} has a high standard deviation among its {self.target} replicates" )
                omitted_wells.append("X")
            else:
                to_omit = self.df["Well Position"].iloc[outlier + i]
                omitted_wells.append(to_omit)

        # New df without the omitted wells. Update the dEqCq Mean column
        new_df = self.df[~self.df['Well Position'].isin(omitted_wells)].copy()
        new_df['dEqCq Mean'] = new_df.groupby("Sample")["dEqCq"].transform("mean")

        # Get the set of three controls
        new_median = new_df["dEqCq"].median()
        self.controls = self.pick_controls(new_df, new_median)

        return(omitted_wells)