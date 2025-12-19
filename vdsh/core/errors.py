from dataclasses import dataclass

from vdsh.core.models import Position
from vdsh.core.models.ast import BaseASTNode
from vdsh.core.models.token import BaseToken, KeywordToken, Operator


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


@dataclass
class InvalidArgumentDeclarationError(ParserError):
    expected: Operator
    actual: BaseToken


@dataclass
class MisingIdentifierInAssignmentError(ParserError):
    actual: BaseToken


@dataclass
class MissingAssignInAssignmentError(ParserError):
    identifier_name: str
    actual: BaseToken


@dataclass
class MissingTypeIdentifierError(ParserError):
    argument_name: str
    actual: BaseToken


@dataclass
class MissingSemicolonError(ParserError):
    actual: BaseToken


@dataclass
class BlockMissingInitialBraceError(ParserError):
    actual: BaseToken


@dataclass
class MissingAssignmentStatementError(ParserError):
    identifier: BaseToken


@dataclass
class MissingIdentifierInFuncDeclerationError(ParserError):
    actual: BaseToken


@dataclass
class MissingRightParenInFuncDeclerationError(ParserError):
    actual: BaseToken


@dataclass
class MissingLeftParenInFuncDeclerationError(ParserError):
    actual: BaseToken
