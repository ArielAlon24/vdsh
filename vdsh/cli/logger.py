from dataclasses import dataclass
from typing import Any

from rich.console import Console
from rich.pretty import pprint

from vdsh.core.errors import VDSHError

console = Console()


@dataclass
class Logger:
    verbose: bool = False

    def info(self, message: str) -> None:
        console.print(f"[bold green]\\[+][/bold green] {message}")

    def warning(self, message: str) -> None:
        console.print(f"[bold yellow]\\[!][/bold yellow] {message}")

    def error(self, value: VDSHError) -> None:
        console.print("[bold red]\\[!][/bold red] ", end="")
        pprint(value)

        if self.verbose:
            raise value

    def pretty_print(self, value: Any, oneline: bool = False) -> None:
        pprint(value, expand_all=not oneline)

    def print(self, value: str) -> None:
        console.print(value)
