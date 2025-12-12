from dataclasses import dataclass

from vdsh.core.models import Position


class VDSHError(Exception):
    pass


class CharIteratorIsOverError(VDSHError):
    pass


class TokenizerError(VDSHError):
    pass


@dataclass
class UnexpectedCharacterError(TokenizerError):
    char: str
    position: Position


@dataclass
class InvalidOperatorError(TokenizerError):
    start: Position
    end: Position
    value: str


@dataclass
class UnterminatedStringError(TokenizerError):
    start: Position


@dataclass
class InvalidNumberError(TokenizerError):
    start: Position
    end: Position
    value: str
