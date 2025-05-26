from datamanagement.da_parser import DAParser
from util.util import Helper
from collections import defaultdict

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
            omitted_wells[key] = Helper.wells_to_omit(df, value[0], value[1])
        
        return(omitted_wells)
    
