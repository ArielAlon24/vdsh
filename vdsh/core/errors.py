from dataclasses import dataclass

from vdsh.core.models import Position
from vdsh.core.models.ast import BaseASTNode
from vdsh.core.models.token import BaseToken, Operator


class VDSHError(Exception):
    pass


class IteratorIsOverError(VDSHError):
    pass


class TokenizerError(VDSHError):
    pass


class ParserError(VDSHError):
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


@dataclass
class UnclosedParenError(ParserError):
    opening_token: BaseToken
    parsed_value: BaseASTNode
    expected: Operator
    actual: BaseToken


@dataclass
class UnexpectedTokenError(ParserError):
    token: BaseToken
