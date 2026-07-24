from core.parser import read_results

class DAParser:
    def __init__(self, filename):
        self.filename = filename

    def readfile(self):
        """
        Read the raw results file through the shared parser

        Returns:
            df: the DataFrame containing the content of the csv file
        """
        return read_results(self.filename)
