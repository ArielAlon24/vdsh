# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "rich",
# ]
# ///

import base64
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Protocol

from rich.console import Console

console = Console()


class ShellcodeRepr(Protocol):
    def __call__(self, name: str, shellcode: bytes) -> str: ...


TARGETS: List[str] = ["clock_gettime", "any_syscall"]
CROSS: str = "aarch64-linux-musl-"
SHELLCODE_TEMPLATE = "{name}_SHELLCODE = bytes([{values}])"
PYTHON_MAX_SHELLCODE_WIDTH = 64


class ScriptError(Exception):
    def __init__(self, message: str, return_code: int = 1) -> None:
        super().__init__(message)

        self.message = message
        self.return_code = return_code


def log(tag: str, message: str) -> None:
    console.print(f"{tag} {message}")


def info(message: str) -> None:
    log(tag="[bold green]\\[+][/bold green]", message=message)


def error(message: str) -> None:
    log(tag="[bold red]\\[!][/bold red]", message=message)


@dataclass
class CommandResult:
    return_code: int
    stdout: bytes
    stderr: bytes


def run_command(command: List[str]) -> CommandResult:
    info(f"Running: [blue]{' '.join(command)}[/blue]")
    try:
        result = subprocess.run(command, check=True, capture_output=True)
        return CommandResult(
            return_code=result.returncode, stdout=result.stdout, stderr=result.stderr
        )
    except subprocess.SubprocessError as e:
        raise ScriptError(f"Failed to run command {command}: {e}")
    except FileNotFoundError as e:
        raise ScriptError(f"Executable not found: {command[0]}")


def python_shellcode_repr(name: str, shellcode: bytes) -> str:
    hex_data = shellcode.hex()

    chunks = [
        hex_data[i : i + PYTHON_MAX_SHELLCODE_WIDTH]
        for i in range(0, len(hex_data), PYTHON_MAX_SHELLCODE_WIDTH)
    ]

    joined = '"\n    "'.join(chunks)

    return f"{name.upper()}_SHELLCODE = bytes.fromhex(\n" f'    "{joined}"\n' f")"


def bash_shellcode_repr(name: str, shellcode: bytes) -> str:
    return f'{name.upper()}_SHELLCODE_B64="{base64.b64encode(shellcode).decode()}"'


SHELLCODE_REPRS: List[ShellcodeRepr] = [python_shellcode_repr, bash_shellcode_repr]


def build(target: Path) -> None:
    try:
        run_command([f"{CROSS}as", f"{target}.S", "-o", f"{target}.o"])
        run_command([f"{CROSS}objcopy", "-O", "binary", f"{target}.o", f"{target}.bin"])

        result = run_command(["hexdump", "-v", "-e", '1/1 "%02x"', f"{target}.bin"])
        shellcode = bytes.fromhex(result.stdout.decode())
        name = target.name

        for shellcode_repr in SHELLCODE_REPRS:
            info(
                f"[bold]{shellcode_repr.__qualname__}[/bold]:\n{shellcode_repr(name, shellcode)}"
            )

    finally:
        run_command(["rm", "-f", f"{target}.bin"])
        run_command(["rm", "-f", f"{target}.o"])


def main() -> None:
    try:
        for target in TARGETS:
            build(Path(sys.argv[0]).parent / target)
    except ScriptError as e:
        error(e.message)
        sys.exit(e.return_code)


if __name__ == "__main__":
    main()
