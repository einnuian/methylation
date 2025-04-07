import pandas as pd

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
    
