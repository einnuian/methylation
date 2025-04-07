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
        df = pd.read_csv(self.filename, skiprows=22, usecols=["Well", 
                                                                   "Well Position", 
                                                                   "Omit", "Sample", 
                                                                   "Target", "Cq", 
                                                                   "Cq Mean", "Cq SD", 
                                                                   "Threshold"])
        return df


