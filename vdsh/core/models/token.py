from dataclasses import dataclass
from enum import Enum

from vdsh.core.models.position import Position


@dataclass
class BaseToken:
    start: Position
    end: Position


@dataclass
class EOFToken(BaseToken):
    pass


@dataclass
class NumberToken(BaseToken):
    value: float


@dataclass
class StringToken(BaseToken):
    value: str


class Keyword(Enum):
    FOR = "for"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    RETURN = "return"
    FUNC = "func"
    TRUE = "true"
    FALSE = "false"
    STRUCT = "struct"


@dataclass
class KeywordToken(BaseToken):
    kind: Keyword


@dataclass
class IndetifierToken(BaseToken):
    value: str


class Operator(Enum):
    # Arithmetic
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"

    # Assignment
    ASSIGN = "="

    # Comparison
    EQUALS = "=="
    NOT_EQUALS = "!="
    LESS = "<"
    LESS_EQUAL = "<="
    GREATER = ">"
    GREATER_EQUAL = ">="

    # Logical
    AND = "&&"
    OR = "||"
    NOT = "!"

    # Grouping / punctuation (optional, but commonly treated as operators)
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    COMMA = ","
    SEMICOLON = ";"


@dataclass
class OperatorToken(BaseToken):
    kind: Operator
