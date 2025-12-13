from dataclasses import dataclass
from enum import Enum

from vdsh.core.models.position import Position


@dataclass(frozen=True)
class BaseToken:
    start: Position
    end: Position


@dataclass(frozen=True)
class EOFToken(BaseToken):
    pass


@dataclass(frozen=True)
class NumberToken(BaseToken):
    value: float


@dataclass(frozen=True)
class StringToken(BaseToken):
    value: str


class Keyword(Enum):
    FOR = "for"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    RETURN = "return"
    FUNC = "func"
    STRUCT = "struct"


@dataclass(frozen=True)
class KeywordToken(BaseToken):
    kind: Keyword


@dataclass(frozen=True)
class IdentifierToken(BaseToken):
    name: str


class Operator(Enum):
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    POWER = "**"
    PERCENT = "%"

    ASSIGN = "="

    EQUALS = "=="
    NOT_EQUALS = "!="
    LESS = "<"
    LESS_EQUAL = "<="
    MORE = ">"
    MORE_EQUAL = ">="

    AND = "&&"
    OR = "||"
    NOT = "!"

    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"

    COMMA = ","
    COLON = ":"
    SEMICOLON = ";"
    DOUBLE_COLON = "::"

    ARROW = "->"


@dataclass(frozen=True)
class OperatorToken(BaseToken):
    kind: Operator
