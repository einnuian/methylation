import pandas as pd
from util.util import Helper

class Target:
    def __init__(self, df: pd.DataFrame, m_target: str, um_target: str):
        self.df = df
        self.m_target = m_target
        self.um_target = um_target

    def remove_hela_ntc(self):
        """
        Trim the dataframe to remove Hela and NTC

        Args:
            df (DataFrame): pandas dataframe to be processed
        
        Returns:
            trimmed_df (DataFrame): trimmed dataframe with only relevant rows
        """
        trimmed_df = self.df[~self.df["Sample"].str.contains("Hela", case=False)]
        trimmed_df = trimmed_df[~trimmed_df["Sample"].str.contains("NTC", case=False)]
        return trimmed_df

    def add_deqcq(self):
        """
        Transform the given dataframe to calculate and add the dEqCq column.

        Args:
            df: the panda dataframe to be processed
            m_target: name of the methylated target
            um_target: name of the unmethylated target

        Return:
            pivoted: the transformed dataframe
        """
        target_df = self.df[self.df["Target"].isin([self.m_target, self.um_target])]
        pivoted = target_df.pivot(index=["Sample", "Well", "Well Position"], 
                                  columns="Target", 
                                  values="Cq").reset_index() # Move Sample and Well back into the dataframe
        pivoted["dEqCq"] = pivoted[self.m_target] - pivoted[self.um_target] #Assuming the endogenous control is UM
        pivoted = pivoted.sort_values("Well")
        return pivoted
    
    def add_rq_min_max_diff(self):
        """
        Calculate and add the RQ min and max columns and their difference to the given dataframe.
        This function assumes that the dataframe has a column "dEqCq" already calculated.

        Args:
            df: the panda dataframe to be processed
            m_target: name of the methylated target
            um_target: name of the unmethylated target
        
        Return:
        """
        rq_df = self.df.copy()
        return
    
    def pick_reference_sample(self):
        pass

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
        new_df = self.remove_hela_ntc()
        new_df = self.add_deqcq().reset_index(drop=True)

        samples_list = new_df["Sample"].unique()

        # Calcuate the original median and mean of dEqCq
        # Check for skewness of the data
        original_median = new_df["dEqCq"].median()
        original_mean = new_df["dEqCq"].mean()
        skewness_percent = abs((original_median - original_mean) / original_median) * 100
        if skewness_percent >= 10:
            print("Warning: The dEqCq values are skewed by more than 10% from the median. Please examine the data before proceeding.")
        
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