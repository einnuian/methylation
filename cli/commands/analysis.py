import sys
import subprocess
from pathlib import Path

import click


_ANALYSIS_DIR = Path(__file__).resolve().parent.parent.parent / "analysis"


@click.group()
def analysis():
    """Analysis pipeline commands."""
    pass


@analysis.command("run")
def analysis_run():
    """Launch the interactive analysis tool."""
    result = subprocess.run([sys.executable, "main.py"], cwd=_ANALYSIS_DIR)
    sys.exit(result.returncode)
