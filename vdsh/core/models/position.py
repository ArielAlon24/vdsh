from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Position:
    row: int
    column: int

    def copy(self) -> Position:
        return Position(row=self.row, column=self.column)
