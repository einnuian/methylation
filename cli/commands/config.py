import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import click

from cli.settings import CONFIG_FILE, TEMPLATE_KEYS, load_settings, save_setting


def select_template_file(assay):
    """
    Open a file dialog to choose the report template for an assay type

    Args:
        assay (str): assay type the template belongs to, e.g. "bws"

    Returns:
        path (Path): the chosen file, or None if cancelled
    """
    # Start from the currently configured template, if there is one
    configured = load_settings().get(TEMPLATE_KEYS[assay])
    start_dir = Path(configured).parent if configured and Path(configured).exists() else Path.cwd()

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title=f"Select the {assay.upper()} Report Template",
        filetypes=[("Excel macro-enabled workbooks", "*.xlsm"), ("All files", "*.*")],
        initialdir=start_dir,
    )

    root.destroy()

    return Path(file_path) if file_path else None


@click.group()
def config():
    """View and change saved settings."""
    pass


@config.command("show")
def config_show():
    """Print the current settings."""
    click.echo(f"Config file: {CONFIG_FILE}")
    if not CONFIG_FILE.exists():
        click.echo("(not created yet, showing defaults)")

    for key, value in load_settings().items():
        click.echo(f"  {key} = {value}")

    # No template ships with the tool, so an unset one blocks that assay type
    for assay, key in TEMPLATE_KEYS.items():
        if key not in load_settings():
            click.echo(f"  {key} = (unset, run: methyl config set-template {assay})")


@config.command("set-positive-control")
@click.argument("name")
def config_set_positive_control(name):
    """Set the positive control sample NAME, e.g. HCT116."""
    save_setting("positive_control", name)
    click.echo(f"positive_control = {name}")
    click.echo(f"Saved to {CONFIG_FILE}")


@config.command("set-template")
@click.argument("assay", type=click.Choice(list(TEMPLATE_KEYS), case_sensitive=False))
def config_set_template(assay):
    """Choose the report template for ASSAY (bws or rss) with a file picker."""
    assay = assay.lower()

    template = select_template_file(assay)
    if template is None:
        click.echo("No file selected. Nothing changed.")
        return

    save_setting(TEMPLATE_KEYS[assay], str(template))
    click.echo(f"{TEMPLATE_KEYS[assay]} = {template}")
    click.echo(f"Saved to {CONFIG_FILE}")
