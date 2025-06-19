import statistics
from collections import defaultdict
from config import GLOBAL_STD_THRESHOLD

class Helper:
            
    # Filter out controls according to targets
    def filter_ctrl_by_target(df, target):
        target_m = target.upper() + "_M"
        target_um = target.upper() + "_UM"
        control_df = df[(df["Target"].isin([target_m, target_um])) & 
                        (df["Sample"].str.contains("control", case=False))]
        return control_df
    
    def make_target_pairs(df):
        """
        Identify the unique existing targets dynamically

        Args:
            df: the panda dataframe to be processed

        Return:
            target_pairs: dict with base names as keys and pairs of target as values
        """
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

    def minimize_stdev(values:list):
        """
        Find the outlier given four values

        Args:
            values (list): list containing the four values to be compared

        Returns:
            to_omit (int): the index of the value to omit such that the stdev is minimized
        """
        val_1 = values[0]
        val_2 = values[1]
        val_3 = values[2]  
        val_4 = values[3]

        # Calculate the standard deviation for remaining wells
        std_1 = statistics.stdev([val_2, val_3, val_4]) #stdev does not contain well 1
        std_2 = statistics.stdev([val_1, val_3, val_4]) #stdev does not contain well 2
        std_3 = statistics.stdev([val_1, val_2, val_4]) #stdev does not contain well 3
        std_4 = statistics.stdev([val_1, val_2, val_3]) #stdev does not contain well 4
        std_dict = {0:std_1, 1:std_2, 2:std_3, 3:std_4}
        min_val = min(std_dict.values())

        to_omit = -1
        for key, value in std_dict.items():
            if value == min_val: 
                to_omit = key
                break
        return to_omit

    def find_outliers(values:list, num):
        """
        Find the value from a list of values that has the biggest difference from a provided number while minimizing the std

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
            std = statistics.stdev(new)
            if diff < min_diff and std <= GLOBAL_STD_THRESHOLD:
                min_diff = diff       
                index = i
        return index