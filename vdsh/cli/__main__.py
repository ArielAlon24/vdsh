import typer

from vdsh.cli.commands import misc_typer


def main() -> None:
    app = typer.Typer()
    app.add_typer(misc_typer)

    app()
