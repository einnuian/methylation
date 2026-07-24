import click

from cli.commands.analysis import analysis
from cli.commands.config import config
from cli.commands.report import report


@click.group()
@click.version_option()
def methyl():
    """Methylation analysis and reporting tools."""
    pass


methyl.add_command(analysis)
methyl.add_command(config)
methyl.add_command(report)


if __name__ == "__main__":
    methyl()
