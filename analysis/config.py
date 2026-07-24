import json
from pathlib import Path

GLOBAL_STD_THRESHOLD = 0.17
GLOBAL_RQ_DIFF_THRESHOLD = 0.2

# Cq value substituted for "Undetermined" wells when the raw file is read
UNDETERMINED_CQ = 40

# Written by `methyl config set-positive-control`, kept at the repo root
SETTINGS_FILE = Path(__file__).resolve().parent.parent / ".methylation_config.json"
DEFAULT_POSITIVE_CONTROL = "HCT116"


def get_positive_control():
    """
    Read the configured positive control sample name

    The positive control is excluded from processing, so its expected "Undetermined"
    readings never reach the outlier detection.

    Returns:
        name (str): the saved sample name, or the default if none has been set
    """
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE) as f:
                return json.load(f).get("positive_control", DEFAULT_POSITIVE_CONTROL)
        except (json.JSONDecodeError, OSError):
            pass

    return DEFAULT_POSITIVE_CONTROL