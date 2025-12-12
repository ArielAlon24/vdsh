import typer
from rich.console import Console

from vdsh.__version__ import __VERSION__

console = Console()
misc_typer = typer.Typer()


@misc_typer.command("version")
def version_command() -> None:
    console.print(f"[blue]VDSH[/blue] Version: [bold yellow]{__VERSION__}[/bold yellow]")
