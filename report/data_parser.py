#!/usr/bin/env python3
"""Data access helpers for qPCR methylation data."""

from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from core.parser import read_results


def parse_qpcr_csv(file_path: Path) -> pd.DataFrame:
    """
    Parse a qPCR CSV export file.

    Args:
        file_path: Path to the CSV file

    Returns:
        DataFrame with one row per well/target and a numeric 'Cq' column
    """
    return read_results(file_path)


def replicate_values(data: pd.DataFrame, sample_name: str, target: str) -> List[Optional[float]]:
    """
    Collect the Cq values of one sample/target, in plate order.

    Args:
        data: Parsed data for the file containing this target
        sample_name: Name of the sample to extract
        target: Full target name, e.g. 'ICR1_M'

    Returns:
        List of Cq values, with None wherever the well has no reading
    """
    match = data[(data["Sample"] == sample_name) & (data["Target"] == target)]

    # The report writes None into Excel to leave a cell untouched, so NaN is translated
    return [None if pd.isna(cq) else float(cq) for cq in match["Cq"]]


def extract_sample_data(target1_data: pd.DataFrame, target2_data: pd.DataFrame, sample_name: str,
                        target1_name: str = 'ICR1', target2_name: str = 'ICR2') -> Dict:
    """
    Extract data for a specific sample from both target files.

    Args:
        target1_data: Parsed data from first target file (e.g., ICR1 or PEG)
        target2_data: Parsed data from second target file (e.g., ICR2 or GRB)
        sample_name: Name of the sample to extract
        target1_name: Name of first target (e.g., 'ICR1' or 'PEG')
        target2_name: Name of second target (e.g., 'ICR2' or 'GRB')

    Returns:
        Dictionary containing organized sample data:
        {
            'sample_name': str,
            'target1_m': [cq1, cq2, cq3],   # replicates for target1 methylated
            'target1_um': [cq1, cq2, cq3],  # replicates for target1 unmethylated
            'target2_m': [cq1, cq2, cq3],   # replicates for target2 methylated
            'target2_um': [cq1, cq2, cq3]   # replicates for target2 unmethylated
        }
    """
    return {
        'sample_name': sample_name,
        'target1_m': replicate_values(target1_data, sample_name, f'{target1_name}_M'),
        'target1_um': replicate_values(target1_data, sample_name, f'{target1_name}_UM'),
        'target2_m': replicate_values(target2_data, sample_name, f'{target2_name}_M'),
        'target2_um': replicate_values(target2_data, sample_name, f'{target2_name}_UM'),
    }


def get_all_samples(target1_data: pd.DataFrame, target2_data: pd.DataFrame) -> List[str]:
    """
    Get list of all unique sample names from both files.

    Args:
        target1_data: Parsed data from first target file
        target2_data: Parsed data from second target file

    Returns:
        Sorted list of unique sample names
    """
    samples = set(target1_data["Sample"]) | set(target2_data["Sample"])

    return sorted(samples)
