import click

from cli.settings import CONFIG_FILE, load_settings, save_setting


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


@config.command("set-positive-control")
@click.argument("name")
def config_set_positive_control(name):
    """Set the positive control sample NAME, e.g. HCT116."""
    save_setting("positive_control", name)
    click.echo(f"positive_control = {name}")
    click.echo(f"Saved to {CONFIG_FILE}")
