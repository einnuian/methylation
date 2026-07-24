import json
from pathlib import Path

# Shared with the analysis and report scripts, so it lives at the repo root
CONFIG_FILE = Path(__file__).resolve().parent.parent / ".methylation_config.json"

DEFAULTS = {
    "positive_control": "HCT116",
}

# Settings key holding the report template for each assay type
TEMPLATE_KEYS = {"bws": "template_bws", "rss": "template_rss"}


def load_settings():
    """
    Read the saved settings, falling back to defaults for anything unset

    Returns:
        settings (dict): the saved settings merged over the defaults
    """
    settings = dict(DEFAULTS)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                settings.update(json.load(f))
        except (json.JSONDecodeError, OSError):
            pass
    return settings


def save_setting(key, value):
    """
    Persist a single setting, leaving anything else in the file intact

    Args:
        key (str): name of the setting
        value: value to store
    """
    current = {}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                current = json.load(f)
        except (json.JSONDecodeError, OSError):
            current = {}

    current[key] = value
    with open(CONFIG_FILE, "w") as f:
        json.dump(current, f, indent=2)
