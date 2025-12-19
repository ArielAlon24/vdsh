from typing import Annotated
import subprocess

import typer

from vdsh.cli.context import create_context
from vdsh.core.errors import VDSHError

run_app = typer.Typer()


@run_app.command("run")
def run(
    src: Annotated[str, typer.Argument()],
    verbose: Annotated[bool, typer.Option()] = False,
    code: Annotated[bool, typer.Option()] = False,
) -> None:
    context = create_context(verbose=verbose, code=code, src=src)
    pipeline = context.create_pipeline()
    logger = context.create_logger()

    try:
        bash = pipeline.run()
        subprocess.run(["bash", "-c", bash])
    except VDSHError as e:
        logger.error(e)
