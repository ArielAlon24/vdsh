import typer

from vdsh.cli.commands import build_app, misc_app, parse_app, run_app, tokenize_app

app = typer.Typer()

for sub_app in [build_app, parse_app, tokenize_app, run_app, misc_app]:
    app.add_typer(sub_app)
