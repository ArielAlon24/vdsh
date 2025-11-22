# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyelftools",
#     "rich",
# ]
# ///

from __future__ import annotations

import io
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from elftools.elf.elffile import ELFFile
from rich.console import Console

CLOCK_GETTIME_SYMBOL: str = "__kernel_clock_gettime"
CLOCK_GETTIME_SHELLCODE = bytes(
    [0x28, 0x0E, 0x80, 0xD2, 0x01, 0x00, 0x00, 0xD4, 0xC0, 0x03, 0x5F, 0xD6]
)


console = Console()


def log(tag: str, message: str) -> None:
    console.print(f"{tag} {message}")


def info(message: str) -> None:
    log(tag="[bold green]\\[+][/bold green]", message=message)


def error(message: str) -> None:
    console.print(f"[bold red]\\[!][/bold red] {message}")


def find_elf_symbol_address(data: bytes, symbol: str) -> Optional[int]:
    elf = ELFFile(io.BytesIO(data))

    for section in elf.iter_sections():
        if section.header.sh_type in ("SHT_SYMTAB", "SHT_DYNSYM"):
            for sym in section.iter_symbols():
                if sym.name == symbol:
                    return sym["st_value"]

    return None


def read_process_memory(pid: int, address: int, size: int) -> bytes:
    mem_path = Path(f"/proc/{pid}/mem")

    with mem_path.open("rb", buffering=0) as mem:
        mem.seek(address)
        return mem.read(size)


def write_process_memory(pid: int, address: int, data: bytes) -> int:
    mem_path = Path(f"/proc/{pid}/mem")

    with mem_path.open("rb+", buffering=0) as mem:
        mem.seek(address)
        return mem.write(data)


@dataclass
class ProcMap:
    pid: int
    start: int
    end: int
    perms: str
    offset: int
    dev: str
    inode: int
    pathname: Optional[str]

    @classmethod
    def from_str(cls, pid: int, line: str) -> ProcMap:
        parts = line.split(maxsplit=5)

        addr_range, perms, offset, dev, inode = parts[:5]
        pathname = parts[5] if len(parts) == 6 else None

        start_str, end_str = addr_range.split("-")

        return cls(
            pid=pid,
            start=int(start_str, 16),
            end=int(end_str, 16),
            perms=perms,
            offset=int(offset, 16),
            dev=dev,
            inode=int(inode),
            pathname=pathname,
        )

    def read_bytes(
        self, size: Optional[int] = None, offset: Optional[int] = None
    ) -> bytes:
        return read_process_memory(
            self.pid,
            address=self.start + (offset or 0),
            size=size or (self.end - self.start),
        )


def parse_proc_maps(pid: int) -> List[ProcMap]:
    maps_path = Path(f"/proc/{pid}/maps")
    lines = maps_path.read_text().splitlines()
    return [ProcMap.from_str(pid=pid, line=line) for line in lines]


def main() -> None:
    pid = os.getpid()
    info(f"PID: {pid}")

    # 1. Locate the `[vdso]` memory map
    maps = parse_proc_maps(pid)
    vdso = next(m for m in maps if m.pathname and "[vdso]" in m.pathname)
    info(f"[yellow]vdso[/yellow] at {hex(vdso.start)} - {hex(vdso.end)}")

    # 2. Find the address of an exported symbol in it (e.g. CLOCK_GETTIME)
    vdso_data = vdso.read_bytes()
    info(f"Searching for '{CLOCK_GETTIME_SYMBOL}'")
    symbol_address = find_elf_symbol_address(
        data=vdso_data, symbol=CLOCK_GETTIME_SYMBOL
    )

    if symbol_address is None:
        error(f"Failed to find '{CLOCK_GETTIME_SYMBOL}'!")
        return

    info(f"Found '{CLOCK_GETTIME_SYMBOL}' at {hex(symbol_address)}")

    # 3. Write the shellcode to that address
    write_process_memory(
        pid=pid,
        address=vdso.start + symbol_address,
        data=CLOCK_GETTIME_SHELLCODE,
    )
    info(f"Wrote `clock_gettime` shellcode to '{CLOCK_GETTIME_SYMBOL}'")

    vdso_data = vdso.read_bytes()
    vdso_dump = Path.home() / "out/vdso-dump.bin"
    vdso_dump.parent.mkdir(exist_ok=True)
    vdso_dump.write_bytes(vdso_data)
    info(f"Dumped [yellow]vdso[/yellow] to {vdso_dump}")

    # 4. Trigger a call
    info(f"Triggering '{CLOCK_GETTIME_SYMBOL}'")
    info(f"Current time: {time.monotonic()}")


if __name__ == "__main__":
    main()
