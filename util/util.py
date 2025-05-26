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

    def find_outliers(val_1, val_2, val_3, val_4):
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
