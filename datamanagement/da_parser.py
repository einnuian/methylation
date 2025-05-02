import pandas as pd

class DAParser:
    def __init__(self, filename):
        self.filename = filename
    
    def readfile(self):
        """
        Read the raw results file, skipping the first 22 rows containing the run info

        Args:
            filename: name of the csv file to be read
        
        Returns:
            df: the DataFrame containing the content of the csv file
        """
        with open(self.filename, "r") as f:
            for i, line in enumerate(f):
                if "Well" in line and "Sample" in line:
                    header_row = i
                    break
        
        df = pd.read_csv(self.filename, skiprows=header_row, usecols=["Well", 
                                                                   "Well Position", 
                                                                   "Omit", "Sample", 
                                                                   "Target", "Cq", 
                                                                   "Cq Mean", "Cq SD", 
                                                                   "Threshold"])
        # Set "Undetermined" to 40 and cast Cq values to type float
        df["Cq"] = df["Cq"].replace("Undetermined", 40)
        df["Cq"] = df["Cq"].replace("UNDETERMINED", 40)
        # Convert all CQ values to numeric
        df["Cq"] = pd.to_numeric(df["Cq"])
        return df


