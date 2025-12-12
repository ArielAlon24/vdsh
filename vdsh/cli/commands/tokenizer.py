from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.pretty import pprint

from vdsh.core.errors import TokenizerError
from vdsh.core.iterator import PeekableIterator
from vdsh.core.pipeline import CharIterator, Tokenizer

tokenizer_typer = typer.Typer()
console = Console()


@tokenizer_typer.command("tokenize")
def tokenize_command(
    src: Annotated[str, typer.Argument()],
    oneline: Annotated[bool, typer.Option()] = False,
    code: Annotated[bool, typer.Option()] = False,
) -> None:
    data = src if code else Path(src).read_text()
    char_iterator = CharIterator(data)
    tokenizer = Tokenizer(PeekableIterator(char_iterator))

    try:
        while not tokenizer.is_over():
            pprint(tokenizer.next(), expand_all=not oneline)
    except TokenizerError as e:
        console.print("[bold red]\\[!][/bold red] Error:")
        pprint(e, expand_all=True)
