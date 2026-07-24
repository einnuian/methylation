import sys
import subprocess
from pathlib import Path

import click


_REPORT_DIR = Path(__file__).resolve().parent.parent.parent / "report"


@click.group()
def report():
    """Report generation commands."""
    pass


@report.command("run")
def report_run():
    """Launch the methylation report generator."""
    result = subprocess.run([sys.executable, "main.py"], cwd=_REPORT_DIR)
    sys.exit(result.returncode)
