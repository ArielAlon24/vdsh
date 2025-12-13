from collections.abc import Callable
from typing import TypeGuard

from vdsh.core.errors import ParserError, UnclosedParenError, UnexpectedTokenError
from vdsh.core.iterator import PeekableIterator
from vdsh.core.iterator.base_iterator import BaseIterator
from vdsh.core.models.ast import (
    BaseASTNode,
    BinaryOperationNode,
    IdentifierNode,
    NumberLiteralNode,
    UnaryOperationNode,
)
from vdsh.core.models.token import (
    BaseToken,
    EOFToken,
    IdentifierToken,
    Keyword,
    KeywordToken,
    NumberToken,
    Operator,
    OperatorToken,
)
from vdsh.core.types import Creator

type ParserPredicate = Callable[[BaseToken], bool]
type ASTNodeParser = Callable[[], BaseASTNode]


def is_number(token: BaseToken) -> TypeGuard[NumberToken]:
    return isinstance(token, NumberToken)


def is_operator(token: BaseToken, operator: Operator) -> TypeGuard[OperatorToken]:
    return isinstance(token, OperatorToken) and token.kind == operator


def is_keyword(token: BaseToken, keyword: Keyword) -> TypeGuard[KeywordToken]:
    return isinstance(token, KeywordToken) and token.kind == keyword


def is_any_keyword(token: BaseToken, keywords: list[Keyword]) -> TypeGuard[KeywordToken]:
    return isinstance(token, KeywordToken) and any(keyword == token.kind for keyword in keywords)


def is_any_operator(token: BaseToken, operators: list[Operator]) -> TypeGuard[OperatorToken]:
    return isinstance(token, OperatorToken) and any(
        operator == token.kind for operator in operators
    )


def is_identifier(token: BaseToken) -> TypeGuard[IdentifierToken]:
    return isinstance(token, IdentifierToken)


def is_eof(token: BaseToken) -> TypeGuard[EOFToken]:
    return isinstance(token, EOFToken)


def create_operator_predicate(operator: Operator) -> ParserPredicate:
    def predicate(token: BaseToken) -> TypeGuard[OperatorToken]:
        return is_operator(token, operator=operator)

    return predicate


class Parser(Creator[BaseASTNode]):
    def __init__(self, token_iterator: BaseIterator[BaseToken]) -> None:
        self.token_iterator = PeekableIterator(token_iterator)
        self._reached_eof = False

    def create(self) -> BaseASTNode:
        return self._parse_bool_expression()

    def _consume(self) -> BaseToken:
        return self.token_iterator.next()

    def _expect(self, predicate: ParserPredicate, error: ParserError) -> BaseToken:
        next_token = self.token_iterator.peek()
        if not predicate(next_token):
            raise error

        self._consume()

        return next_token

    def _parse_binary_operation(
        self,
        left_parser: ASTNodeParser,
        right_parser: ASTNodeParser,
        operators: list[Operator],
        repeated: bool = True,
    ) -> BaseASTNode:
        left = left_parser()

        next_token = self.token_iterator.peek()
        while is_any_operator(next_token, operators=operators):
            self._consume()
            right = right_parser()
            left = BinaryOperationNode(left=left, right=right, operator=next_token.kind)

            if not repeated:
                break

            next_token = self.token_iterator.peek()

        return left

    def _parse_unary_operation(
        self,
        parser: ASTNodeParser,
        operators: list[Operator],
    ) -> BaseASTNode:
        next_token = self.token_iterator.peek()
        if is_any_operator(next_token, operators=operators):
            self._consume()

            return UnaryOperationNode(
                value=self._parse_unary_operation(parser, operators=operators),
                operator=next_token.kind,
            )

        return parser()

    def _parse_atom(self) -> BaseASTNode:
        next_token = self._consume()

        if is_operator(next_token, operator=Operator.LEFT_PAREN):
            expression = self._parse_expression()
            self._expect(
                create_operator_predicate(Operator.RIGHT_PAREN),
                error=UnclosedParenError(
                    opening_token=next_token,
                    parsed_value=expression,
                    expected=Operator.RIGHT_PAREN,
                    actual=self.token_iterator.peek(),
                ),
            )

            return expression

        if is_number(next_token):
            return NumberLiteralNode(value=next_token.value)

        if is_identifier(next_token):
            return IdentifierNode(name=next_token.name)

        raise UnexpectedTokenError(token=next_token)

    def _parse_power(self) -> BaseASTNode:
        return self._parse_binary_operation(
            left_parser=self._parse_atom,
            right_parser=self._parse_factor,
            operators=[Operator.POWER],
        )

    def _parse_factor(self) -> BaseASTNode:
        return self._parse_unary_operation(
            parser=self._parse_power,
            operators=[Operator.PLUS, Operator.MINUS],
        )

    def _parse_term(self) -> BaseASTNode:
        return self._parse_binary_operation(
            left_parser=self._parse_factor,
            right_parser=self._parse_factor,
            operators=[Operator.STAR, Operator.SLASH, Operator.PERCENT],
        )

    def _parse_expression(self) -> BaseASTNode:
        return self._parse_binary_operation(
            left_parser=self._parse_term,
            right_parser=self._parse_expression,
            operators=[Operator.PLUS, Operator.MINUS],
        )

    def _parse_comparison(self) -> BaseASTNode:
        return self._parse_binary_operation(
            left_parser=self._parse_expression,
            right_parser=self._parse_expression,
            operators=[
                Operator.EQUALS,
                Operator.NOT_EQUALS,
                Operator.LESS,
                Operator.LESS_EQUAL,
                Operator.MORE,
                Operator.MORE_EQUAL,
            ],
            repeated=False,
        )

    def _parse_bool_factor(self) -> BaseASTNode:
        return self._parse_unary_operation(
            parser=self._parse_comparison,
            operators=[Operator.NOT],
        )

    def _parse_bool_term(self) -> BaseASTNode:
        return self._parse_binary_operation(
            left_parser=self._parse_bool_factor,
            right_parser=self._parse_bool_term,
            operators=[Operator.AND],
        )

    def _parse_bool_expression(self) -> BaseASTNode:
        return self._parse_binary_operation(
            left_parser=self._parse_bool_term,
            right_parser=self._parse_bool_expression,
            operators=[Operator.OR],
        )
