from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.pretty import pprint

from vdsh.core.errors import ParserError
from vdsh.core.iterator import SequenceIterator
from vdsh.core.pipeline import Parser, Tokenizer

parser_typer = typer.Typer()
console = Console()


@parser_typer.command("parse")
def tokenize_command(
    src: Annotated[str, typer.Argument()],
    oneline: Annotated[bool, typer.Option()] = False,
    code: Annotated[bool, typer.Option()] = False,
) -> None:
    data = src if code else Path(src).read_text()
    char_iterator = SequenceIterator(data)
    tokenizer = Tokenizer(char_iterator)
    parser = Parser(tokenizer)

    try:
        pprint(parser.create(), expand_all=not oneline)
    except ParserError as e:
        console.print("[bold red]\\[!][/bold red] Error:")
        pprint(e, expand_all=True)
