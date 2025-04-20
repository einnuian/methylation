import pandas as pd
from datamanagement.da_parser import DAParser
from util.util import Helper

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
    
    def process_ICR1(self):
        df = self.parser.readfile()
        omitted_wells = Helper.process(df, "ICR1_M", "ICR1_UM")
        return(omitted_wells)
    
    def process_ICR2(self):
        df = self.parser.readfile()
        omitted_wells = Helper.process(df, "ICR2_M", "ICR2_UM")
        return(omitted_wells)
    
    def process_GRB(self):
        df = self.parser.readfile()
        omitted_wells = Helper.process(df, "GRB_M", "GRB_UM")
        return(omitted_wells)
    
    def process_PEG(self):
        df = self.parser.readfile()
        omitted_wells = Helper.process(df, "PEG_M", "PEG_UM")
        return(omitted_wells)