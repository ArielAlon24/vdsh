from typing import Annotated

import typer

from vdsh.cli.context import create_context
from vdsh.core.errors import TokenizerError

tokenize_app = typer.Typer()


@tokenize_app.command("tokenize")
def tokenize(
    src: Annotated[str, typer.Argument()],
    verbose: Annotated[bool, typer.Option()] = False,
    code: Annotated[bool, typer.Option()] = False,
    oneline: Annotated[bool, typer.Option()] = False,
) -> None:
    context = create_context(verbose=verbose, code=code, src=src)
    tokenizer = context.create_token_iterator()
    logger = context.create_logger()

    try:
        while not tokenizer.is_over():
            logger.pretty_print(tokenizer.next(), oneline=oneline)
    except TokenizerError as e:
        logger.error(e)
