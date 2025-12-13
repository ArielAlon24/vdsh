import typer

from vdsh.cli.commands import misc_typer, parser_typer, tokenizer_typer


def main() -> None:
    app = typer.Typer()

    app.add_typer(misc_typer)
    app.add_typer(tokenizer_typer)
    app.add_typer(parser_typer)

    app()
