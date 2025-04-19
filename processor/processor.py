import pandas as pd
from datamanagement.da_parser import DAParser

class Processor:
    def __init__(self, parser):
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