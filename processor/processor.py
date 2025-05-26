import pandas as pd
from datamanagement.da_parser import DAParser
from util.util import Helper
from collections import defaultdict

class Processor:
    def __init__(self, parser:DAParser):
        self.parser = parser
    
    def find_reference_control(cq_values):
        pass
    
    def calculate_eqcq(cq_values):
        pass
    
    # Calculate delta Cq values
    def calculate_delta_eqcq(eqcq_m, eqcq_um):
        """
        Calculate the delta EqCq values
        
        Args:
            eqcq_m (float): equivalent quantification - mean Cq values of all M target of the same sample
            eqcq_um (float): equivalnt quantification - mean Cq values of all UM target of the same sample
        
        Returns:
            float: the difference between the two mean_cq values 
        """
        return 0
    
    """
    Process the parsed dataframe and identify the wells to be omitted by target

    Return:
        omitted_wells: dict with targets as keys and list of wells be omitted as values
    """
    def process(self):
        df = self.parser.readfile()
        target_pairs = Helper.make_target_pairs(df)

        omitted_wells = defaultdict(list)

        for key, value in target_pairs.items():
            omitted_wells[key] = Helper.wells_to_omit(df, value[0], value[1])
        
        return(omitted_wells)
    
