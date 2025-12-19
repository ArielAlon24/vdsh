import typer

from vdsh.__version__ import __VERSION__
from vdsh.cli.logger import Logger

misc_app = typer.Typer()


@misc_app.command("version")
def version_command() -> None:
    logger = Logger()
    logger.print(f"[blue]VDSH[/blue] Version: [bold yellow]{__VERSION__}[/bold yellow]")
