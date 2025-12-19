from typing import Annotated

import typer

from vdsh.cli.context import create_context
from vdsh.core.errors import ParserError

parse_app = typer.Typer()


@parse_app.command("parse")
def parse(
    src: Annotated[str, typer.Argument()],
    verbose: Annotated[bool, typer.Option()] = False,
    code: Annotated[bool, typer.Option()] = False,
    oneline: Annotated[bool, typer.Option()] = False,
) -> None:
    context = create_context(verbose=verbose, code=code, src=src)
    parser = context.create_parser()
    logger = context.create_logger()

    try:
        logger.pretty_print(parser.create(), oneline=oneline)
    except ParserError as e:
        logger.error(e)
