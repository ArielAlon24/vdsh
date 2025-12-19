import operator
from dataclasses import dataclass

import pytest

from vdsh.core.errors import UnclosedParenError, UnexpectedTokenError
from vdsh.core.iterator.sequence_iterator import SequenceIterator
from vdsh.core.models.ast import (
    BaseASTNode,
    BinaryOperationNode,
    IdentifierNode,
    NumberLiteralNode,
    UnaryOperationNode,
)
from vdsh.core.models.position import Position
from vdsh.core.models.token import (
    BaseToken,
    EOFToken,
    IdentifierToken,
    NumberToken,
    Operator,
    OperatorToken,
)
from vdsh.core.pipeline import Parser


@dataclass
class Candidate:
    name: str
    tokens: list[BaseToken]


@dataclass
class HappyCandidate(Candidate):
    ast: BaseASTNode


@dataclass
class BadCandidate(Candidate):
    error: Exception


HAPPY_CANDIDATES = [
    HappyCandidate(
        name="1-plus-2",
        tokens=[
            NumberToken(Position(1, 1), Position(1, 1), value=1.0),
            OperatorToken(Position(1, 3), Position(1, 3), kind=Operator.PLUS),
            NumberToken(Position(1, 5), Position(1, 5), value=2.0),
            EOFToken(Position(1, 6), Position(1, 6)),
        ],
        ast=BinaryOperationNode(
            left=NumberLiteralNode(number=1.0),
            right=NumberLiteralNode(number=2.0),
            operator=Operator.PLUS,
        ),
    ),
    HappyCandidate(
        name="neg-5-times-3",
        tokens=[
            OperatorToken(Position(1, 1), Position(1, 1), kind=Operator.MINUS),
            NumberToken(Position(1, 2), Position(1, 2), value=5.0),
            OperatorToken(Position(1, 4), Position(1, 4), kind=Operator.STAR),
            NumberToken(Position(1, 6), Position(1, 6), value=3.0),
            EOFToken(Position(1, 7), Position(1, 7)),
        ],
        ast=BinaryOperationNode(
            left=UnaryOperationNode(
                operator=Operator.MINUS,
                value=NumberLiteralNode(number=5.0),
            ),
            right=NumberLiteralNode(number=3.0),
            operator=Operator.STAR,
        ),
    ),
    HappyCandidate(
        name="x-leq-10",
        tokens=[
            IdentifierToken(Position(1, 1), Position(1, 1), name="x"),
            OperatorToken(Position(1, 3), Position(1, 4), kind=Operator.LESS_EQUAL),
            NumberToken(Position(1, 6), Position(1, 6), value=10.0),
            EOFToken(Position(1, 7), Position(1, 7)),
        ],
        ast=BinaryOperationNode(
            left=IdentifierNode(name="x"),
            right=NumberLiteralNode(number=10.0),
            operator=Operator.LESS_EQUAL,
        ),
    ),
    HappyCandidate(
        name="1-neq-2-and-flag",
        tokens=[
            NumberToken(Position(1, 1), Position(1, 1), value=1.0),
            OperatorToken(Position(1, 3), Position(1, 4), kind=Operator.NOT_EQUALS),
            NumberToken(Position(1, 6), Position(1, 6), value=2.0),
            OperatorToken(Position(1, 8), Position(1, 10), kind=Operator.AND),
            IdentifierToken(Position(1, 12), Position(1, 12), name="flag"),
            EOFToken(Position(1, 13), Position(1, 13)),
        ],
        ast=BinaryOperationNode(
            left=BinaryOperationNode(
                left=NumberLiteralNode(number=1.0),
                right=NumberLiteralNode(number=2.0),
                operator=Operator.NOT_EQUALS,
            ),
            right=IdentifierNode(name="flag"),
            operator=Operator.AND,
        ),
    ),
    HappyCandidate(
        name="complex-bool-logic",
        tokens=[
            NumberToken(Position(1, 1), Position(1, 1), value=1.0),
            OperatorToken(Position(1, 3), Position(1, 3), kind=Operator.LESS),
            NumberToken(Position(1, 5), Position(1, 5), value=2.0),
            OperatorToken(Position(1, 7), Position(1, 9), kind=Operator.AND),
            NumberToken(Position(1, 11), Position(1, 11), value=3.0),
            OperatorToken(Position(1, 13), Position(1, 14), kind=Operator.EQUALS),
            NumberToken(Position(1, 16), Position(1, 16), value=3.0),
            OperatorToken(Position(1, 18), Position(1, 20), kind=Operator.OR),
            OperatorToken(Position(1, 22), Position(1, 24), kind=Operator.NOT),
            IdentifierToken(Position(1, 26), Position(1, 26), name="x"),
            EOFToken(Position(1, 27), Position(1, 27)),
        ],
        ast=BinaryOperationNode(
            left=BinaryOperationNode(
                left=BinaryOperationNode(
                    left=NumberLiteralNode(1.0),
                    right=NumberLiteralNode(2.0),
                    operator=Operator.LESS,
                ),
                right=BinaryOperationNode(
                    left=NumberLiteralNode(3.0),
                    right=NumberLiteralNode(3.0),
                    operator=Operator.EQUALS,
                ),
                operator=Operator.AND,
            ),
            right=UnaryOperationNode(
                operator=Operator.NOT,
                value=IdentifierNode(name="x"),
            ),
            operator=Operator.OR,
        ),
    ),
    HappyCandidate(
        name="paren-arithmetic-nested",
        tokens=[
            OperatorToken(Position(1, 1), Position(1, 1), kind=Operator.LEFT_PAREN),
            NumberToken(Position(1, 2), Position(1, 2), value=1.0),
            OperatorToken(Position(1, 4), Position(1, 4), kind=Operator.PLUS),
            NumberToken(Position(1, 6), Position(1, 6), value=2.0),
            OperatorToken(Position(1, 7), Position(1, 7), kind=Operator.RIGHT_PAREN),
            OperatorToken(Position(1, 9), Position(1, 9), kind=Operator.STAR),
            OperatorToken(Position(1, 11), Position(1, 11), kind=Operator.LEFT_PAREN),
            NumberToken(Position(1, 12), Position(1, 12), value=3.0),
            OperatorToken(Position(1, 14), Position(1, 14), kind=Operator.MINUS),
            OperatorToken(Position(1, 16), Position(1, 16), kind=Operator.LEFT_PAREN),
            NumberToken(Position(1, 17), Position(1, 17), value=4.0),
            OperatorToken(Position(1, 19), Position(1, 19), kind=Operator.SLASH),
            NumberToken(Position(1, 21), Position(1, 21), value=2.0),
            OperatorToken(Position(1, 22), Position(1, 22), kind=Operator.RIGHT_PAREN),
            OperatorToken(Position(1, 23), Position(1, 23), kind=Operator.RIGHT_PAREN),
            EOFToken(Position(1, 24), Position(1, 24)),
        ],
        ast=BinaryOperationNode(
            left=BinaryOperationNode(
                left=NumberLiteralNode(1.0),
                right=NumberLiteralNode(2.0),
                operator=Operator.PLUS,
            ),
            right=BinaryOperationNode(
                left=NumberLiteralNode(3.0),
                right=BinaryOperationNode(
                    left=NumberLiteralNode(4.0),
                    right=NumberLiteralNode(2.0),
                    operator=Operator.SLASH,
                ),
                operator=Operator.MINUS,
            ),
            operator=Operator.STAR,
        ),
    ),
]


BAD_CANDIDATES = [
    BadCandidate(
        name="unexpected-token",
        tokens=[
            OperatorToken(Position(1, 1), Position(1, 1), kind=Operator.PLUS),
            OperatorToken(Position(1, 2), Position(1, 2), kind=Operator.PLUS),
            EOFToken(Position(1, 3), Position(1, 3)),
        ],
        error=UnexpectedTokenError(token=EOFToken(Position(1, 3), Position(1, 3))),
    ),
    BadCandidate(
        name="missing-right-paren",
        tokens=[
            OperatorToken(Position(1, 1), Position(1, 1), kind=Operator.LEFT_PAREN),
            NumberToken(Position(1, 2), Position(1, 2), value=1.0),
            EOFToken(Position(1, 3), Position(1, 3)),
        ],
        error=UnclosedParenError(
            opening_token=OperatorToken(Position(1, 1), Position(1, 1), kind=Operator.LEFT_PAREN),
            parsed_value=NumberLiteralNode(1.0),
            expected=Operator.RIGHT_PAREN,
            actual=EOFToken(Position(1, 3), Position(1, 3)),
        ),
    ),
]


@pytest.mark.parametrize("candidate", HAPPY_CANDIDATES, ids=operator.attrgetter("name"))
def test_parser_happy_flow(candidate: HappyCandidate) -> None:
    ast = _parse(candidate.tokens)
    assert ast == candidate.ast


@pytest.mark.parametrize("candidate", BAD_CANDIDATES, ids=operator.attrgetter("name"))
def test_parser_bad_flow(candidate: BadCandidate) -> None:
    with pytest.raises(type(candidate.error)):
        _parse(candidate.tokens)


def _parse(tokens: list[BaseToken]) -> BaseASTNode:
    token_iterator = SequenceIterator(tokens)
    parser = Parser(token_iterator)

    return parser.create()
