from __future__ import annotations

from typing import TYPE_CHECKING

from vdsh.core.errors import (
    InvalidNumberError,
    InvalidOperatorError,
    UnexpectedCharacterError,
    UnterminatedStringError,
)
from vdsh.core.iterator import BaseIterator, PeekableIterator
from vdsh.core.models import Position
from vdsh.core.models.token import (
    BaseToken,
    EOFToken,
    IndetifierToken,
    Keyword,
    KeywordToken,
    NumberToken,
    Operator,
    OperatorToken,
    StringToken,
)

if TYPE_CHECKING:
    from collections.abc import Callable


def _build_operators_by_first_char(operators_name_map: dict[str, Operator]) -> dict[str, list[str]]:
    operators_by_first: dict[str, list[str]] = {}

    for spelling in operators_name_map:
        first = spelling[0]
        operators_by_first.setdefault(first, []).append(spelling)

    for lst in operators_by_first.values():
        lst.sort(key=len, reverse=True)

    return operators_by_first


OPERATORS_NAME_MAP = {operator.value: operator for operator in Operator}
OPERATORS_BY_FIRST_CHAR = _build_operators_by_first_char(OPERATORS_NAME_MAP)
STRING_TERMINATOR = '"'


class Tokenizer(BaseIterator[BaseToken]):
    def __init__(self, char_iterator: PeekableIterator[str]) -> None:
        self.char_iterator = char_iterator
        self.position = Position(row=1, column=1)
        self._reached_eof = False

    def _advance_position(self, char: str) -> None:
        if char == "\n":
            self.position.row += 1
            self.position.column = 0
        else:
            self.position.column += 1

    def _consume(self) -> str:
        char = self.char_iterator.next()
        self.last_position = self.position.copy()
        self._advance_position(char)

        return char

    def _read_while(self, predicate: Callable[[str], bool]) -> str:
        result = []
        while not self.char_iterator.is_over():
            ch = self.char_iterator.peek()
            if not predicate(ch):
                break
            result.append(self._consume())
        return "".join(result)

    def _skip_whitespace(self) -> None:
        self._read_while(str.isspace)

    def _read_number_text(self) -> str:
        return self._read_while(self._is_number_char)

    @staticmethod
    def _is_number_char(ch: str) -> bool:
        return ch.isdigit() or ch == "."

    def _read_number(self) -> NumberToken:
        start = self.position.copy()
        text = self._read_number_text()
        end = self.last_position.copy()

        try:
            value = float(text)
        except ValueError as exc:
            raise InvalidNumberError(start=start, end=end, value=text) from exc

        return NumberToken(start=start, end=end, value=value)

    def _read_string(self) -> StringToken:
        start = self.position.copy()
        self._consume()

        value = ""
        while not self.char_iterator.is_over():
            char = self._consume()

            if char == STRING_TERMINATOR:
                end = self.last_position.copy()
                return StringToken(start=start, end=end, value=value)

            value += char

        raise UnterminatedStringError(start=start)

    def _read_identifier_text(self) -> str:
        return self._read_while(str.isalpha)

    def _read_identifier_or_keyword(self) -> BaseToken:
        start = self.position.copy()
        text = self._read_identifier_text()
        end = self.last_position.copy()

        for kw in Keyword:
            if text == kw.value:
                return KeywordToken(start=start, end=end, kind=kw)

        return IndetifierToken(start=start, end=end, value=text)

    def _read_operator(self, candidates: list[str]) -> OperatorToken:
        start = self.position.copy()
        value = self._consume()
        value = self._extend_operator(value, candidates)
        end = self.last_position.copy()

        if value not in Operator:
            raise InvalidOperatorError(start=start, end=end, value=value)

        return OperatorToken(start=start, end=end, kind=Operator(value))

    def _extend_operator(self, current: str, candidates: list[str]) -> str:
        while not self.char_iterator.is_over():
            nxt = self.char_iterator.peek()
            trial = current + nxt

            if not any(op.startswith(trial) for op in candidates):
                break

            current += self._consume()

        return current

    def next(self) -> BaseToken:
        self._skip_whitespace()

        if self.char_iterator.is_over():
            self._reached_eof = True
            pos = self.position.copy()
            return EOFToken(start=pos, end=pos)

        ch = self.char_iterator.peek()

        if ch.isdigit():
            return self._read_number()

        if ch == STRING_TERMINATOR:
            return self._read_string()

        if ch.isalpha():
            return self._read_identifier_or_keyword()

        if ch in OPERATORS_BY_FIRST_CHAR:
            return self._read_operator(OPERATORS_BY_FIRST_CHAR[ch])

        raise UnexpectedCharacterError(char=ch, position=self.position.copy())

    def is_over(self) -> bool:
        return self._reached_eof
