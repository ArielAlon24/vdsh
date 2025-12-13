import operator
from dataclasses import dataclass

import pytest

from vdsh.core.errors import (
    InvalidNumberError,
    TokenizerError,
    UnexpectedCharacterError,
    UnterminatedStringError,
)
from vdsh.core.iterator import SequenceIterator
from vdsh.core.models.position import Position
from vdsh.core.models.token import (
    BaseToken,
    EOFToken,
    IdentifierToken,
    Keyword,
    KeywordToken,
    NumberToken,
    Operator,
    OperatorToken,
    StringToken,
)
from vdsh.core.pipeline import Tokenizer


@dataclass
class Candidate:
    name: str
    code: str


@dataclass
class HappyCandidate(Candidate):
    tokens: list[BaseToken]


@dataclass
class BadCandidate(Candidate):
    error: TokenizerError


HAPPY_CANDIDATES = [
    HappyCandidate(
        name="single-number",
        code="1",
        tokens=[
            NumberToken(
                start=Position(1, 1),
                end=Position(1, 1),
                value=1.0,
            ),
            EOFToken(start=Position(1, 2), end=Position(1, 2)),
        ],
    ),
    HappyCandidate(
        name="multi-digit-numbers",
        code="123 45.6",
        tokens=[
            NumberToken(
                start=Position(1, 1),
                end=Position(1, 3),
                value=123.0,
            ),
            NumberToken(
                start=Position(1, 5),
                end=Position(1, 8),
                value=45.6,
            ),
            EOFToken(start=Position(1, 9), end=Position(1, 9)),
        ],
    ),
    HappyCandidate(
        name="string-literal",
        code='"hi"',
        tokens=[
            StringToken(
                start=Position(1, 1),
                end=Position(1, 4),
                value="hi",
            ),
            EOFToken(start=Position(1, 5), end=Position(1, 5)),
        ],
    ),
    HappyCandidate(
        name="2-string-literals",
        code='"hi""by"',
        tokens=[
            StringToken(
                start=Position(1, 1),
                end=Position(1, 4),
                value="hi",
            ),
            StringToken(
                start=Position(1, 5),
                end=Position(1, 8),
                value="by",
            ),
            EOFToken(start=Position(1, 9), end=Position(1, 9)),
        ],
    ),
    HappyCandidate(
        name="keywords-and-identifiers",
        code="for x if y",
        tokens=[
            KeywordToken(start=Position(1, 1), end=Position(1, 3), kind=Keyword.FOR),
            IdentifierToken(start=Position(1, 5), end=Position(1, 5), name="x"),
            KeywordToken(start=Position(1, 7), end=Position(1, 8), kind=Keyword.IF),
            IdentifierToken(start=Position(1, 10), end=Position(1, 10), name="y"),
            EOFToken(start=Position(1, 11), end=Position(1, 11)),
        ],
    ),
    HappyCandidate(
        name="operators-mixed",
        code="a!=b == c",
        tokens=[
            IdentifierToken(start=Position(1, 1), end=Position(1, 1), name="a"),
            OperatorToken(start=Position(1, 2), end=Position(1, 3), kind=Operator("!=")),
            IdentifierToken(start=Position(1, 4), end=Position(1, 4), name="b"),
            OperatorToken(start=Position(1, 6), end=Position(1, 7), kind=Operator("==")),
            IdentifierToken(start=Position(1, 9), end=Position(1, 9), name="c"),
            EOFToken(start=Position(1, 10), end=Position(1, 10)),
        ],
    ),
    HappyCandidate(
        name="2-operators",
        code="==!===",
        tokens=[
            OperatorToken(start=Position(1, 1), end=Position(1, 2), kind=Operator("==")),
            OperatorToken(start=Position(1, 3), end=Position(1, 4), kind=Operator("!=")),
            OperatorToken(start=Position(1, 5), end=Position(1, 6), kind=Operator("==")),
            EOFToken(start=Position(1, 7), end=Position(1, 7)),
        ],
    ),
    HappyCandidate(
        name="complex-expression",
        code='1 + 2* "hi" >= x',
        tokens=[
            NumberToken(start=Position(1, 1), end=Position(1, 1), value=1.0),
            OperatorToken(start=Position(1, 3), end=Position(1, 3), kind=Operator("+")),
            NumberToken(start=Position(1, 5), end=Position(1, 5), value=2.0),
            OperatorToken(start=Position(1, 6), end=Position(1, 6), kind=Operator("*")),
            StringToken(start=Position(1, 8), end=Position(1, 11), value="hi"),
            OperatorToken(start=Position(1, 13), end=Position(1, 14), kind=Operator(">=")),
            IdentifierToken(start=Position(1, 16), end=Position(1, 16), name="x"),
            EOFToken(start=Position(1, 17), end=Position(1, 17)),
        ],
    ),
]

BAD_CANDIDATES = [
    BadCandidate(
        name="invalid-number",
        code="1.2.3",
        error=InvalidNumberError(
            start=Position(1, 1),
            end=Position(1, 5),
            value="1.2.3",
        ),
    ),
    BadCandidate(
        name="unterminated-string",
        code='"hello',
        error=UnterminatedStringError(
            start=Position(1, 1),
        ),
    ),
    BadCandidate(
        name="unexpected-character",
        code="@",
        error=UnexpectedCharacterError(
            char="@",
            position=Position(1, 1),
        ),
    ),
]


@pytest.mark.parametrize(
    "candidate",
    HAPPY_CANDIDATES,
    ids=operator.attrgetter("name"),
)
def test_happy_flow(candidate: HappyCandidate) -> None:
    actual = _tokenize(candidate.code)
    assert candidate.tokens == actual


@pytest.mark.parametrize("candidate", BAD_CANDIDATES, ids=operator.attrgetter("name"))
def test_bad_flow(candidate: BadCandidate) -> None:
    with pytest.raises(type(candidate.error)) as exc_info:
        _tokenize(candidate.code)

    assert candidate.error == exc_info.value


def _tokenize(code: str) -> list[BaseToken]:
    char_iterator = SequenceIterator(code)
    tokenizer = Tokenizer(char_iterator)

    tokens = []
    while not tokenizer.is_over():
        tokens.append(tokenizer.next())

    return tokens
