"""
Shared reader for qPCR result exports.

Both the analysis and report pipelines read the same instrument export, so they read it
through this module and share one in-memory representation: a pandas DataFrame with one
row per well/target and a numeric "Cq" column.
"""

import pandas as pd

# Cq value substituted for wells the instrument reported as "Undetermined"
UNDETERMINED_CQ = 40

# Columns kept from the raw export
COLUMNS = ["Well", "Well Position", "Omit", "Sample", "Target",
           "Cq", "Cq Mean", "Cq SD", "Threshold"]


def find_header_row(file_path):
    """
    Locate the header row, which sits below a variable-length block of run info

    Args:
        file_path: path to the exported csv file

    Returns:
        header_row (int): zero-based index of the header line
    """
    with open(file_path, "r") as f:
        for i, line in enumerate(f):
            # "Well" alone also matches run-info lines such as "# Block Type: 384-Well Block"
            if "Well" in line and "Sample" in line:
                return i

    raise ValueError(f"Could not find the header row in {file_path}")


def read_results(file_path):
    """
    Read an exported results file into the shared DataFrame representation

    Wells reported as "Undetermined" are given a Cq of UNDETERMINED_CQ. Anything else that
    cannot be read as a number becomes NaN rather than raising, so a single malformed well
    does not abort a whole plate.

    Args:
        file_path: path to the exported csv file

    Returns:
        df (DataFrame): one row per well/target, with a numeric "Cq" column
    """
    header_row = find_header_row(file_path)
    df = pd.read_csv(file_path, skiprows=header_row, usecols=COLUMNS)

    # Compared as text so that any casing is caught, and without checking the column's
    # dtype first: pandas may infer "str" or "object" depending on its version
    cq = df["Cq"].astype(str).str.strip()
    df["Cq"] = pd.to_numeric(cq.mask(cq.str.upper() == "UNDETERMINED", UNDETERMINED_CQ),
                             errors="coerce")

    return df
