from typing import Annotated

import typer

from vdsh.cli.context import create_context
from vdsh.core.errors import VDSHError

build_app = typer.Typer()


@build_app.command("build")
def build(
    src: Annotated[str, typer.Argument()],
    verbose: Annotated[bool, typer.Option()] = False,
    code: Annotated[bool, typer.Option()] = False,
) -> None:
    context = create_context(verbose=verbose, code=code, src=src)
    pipeline = context.create_pipeline()
    logger = context.create_logger()

    try:
        logger.print(pipeline.run())
    except VDSHError as e:
        logger.error(e)
