from collections.abc import Callable
from typing import TypeGuard

from vdsh.core.errors import (
    BlockMissingInitialBraceError,
    InvalidArgumentDeclarationError,
    MisingIdentifierInAssignmentError,
    MissingAssignInAssignmentError,
    MissingIdentifierInFuncDeclerationError,
    MissingLeftParenInFuncDeclerationError,
    MissingRightParenInFuncDeclerationError,
    MissingSemicolonError,
    MissingTypeIdentifierError,
    ParserError,
    UnclosedParenError,
    UnexpectedTokenError,
)
from vdsh.core.iterator import PeekableIterator
from vdsh.core.iterator.base_iterator import BaseIterator
from vdsh.core.models.ast import (
    ArgumentNode,
    ArgumentsNode,
    AssignmentNode,
    BaseASTNode,
    BinaryOperationNode,
    BlockNode,
    FuncDeclerationNode,
    FuncStatementNode,
    IdentifierNode,
    LetStatementNode,
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
from vdsh.core.types import BaseCreator

type ParserPredicate[T] = Callable[[BaseToken], TypeGuard[T]]
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


class Parser(BaseCreator[BaseASTNode]):
    def __init__(self, token_iterator: BaseIterator[BaseToken]) -> None:
        self.token_iterator = PeekableIterator(token_iterator)
        self._reached_eof = False

    def create(self) -> BaseASTNode:
        return self._parse_statement()

    def _consume(self) -> BaseToken:
        return self.token_iterator.next()

    def _expect[T](self, predicate: ParserPredicate[T], error: ParserError) -> T:
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

            left = BinaryOperationNode(left=left, right=right, operator=next_token)

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
                operator=next_token,
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
            return NumberLiteralNode(number=next_token)

        if is_identifier(next_token):
            return IdentifierNode(identifier=next_token)

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

    def _parse_statement(self) -> BaseASTNode:
        next_token = self.token_iterator.peek()

        if is_keyword(next_token, keyword=Keyword.LET):
            self._consume()
            assignment = self._parse_assignment()
            self._expect(
                create_operator_predicate(Operator.SEMICOLON),
                error=MissingSemicolonError(actual=self.token_iterator.peek()),
            )
            return LetStatementNode(let=next_token, assignment=assignment)

        if is_keyword(next_token, keyword=Keyword.FUNC):
            self._consume()
            func_decleration = self._parse_func_decleration()
            return FuncStatementNode(func=next_token, decelration=func_decleration)

        return self._parse_bool_expression()

    def _parse_assignment(self) -> AssignmentNode:
        identifier = self._expect(
            is_identifier,
            error=MisingIdentifierInAssignmentError(actual=self.token_iterator.peek()),
        )

        self._expect(
            create_operator_predicate(Operator.ASSIGN),
            error=MissingAssignInAssignmentError(
                identifier_name=identifier.name,
                actual=self.token_iterator.peek(),
            ),
        )

        value = self._parse_statement()

        return AssignmentNode(identifier=identifier, value=value)

    def _parse_argument(self) -> ArgumentNode | None:
        identifier_token = self.token_iterator.peek()

        if not is_identifier(identifier_token):
            return None
        self._consume()

        self._expect(
            create_operator_predicate(Operator.COLON),
            error=InvalidArgumentDeclarationError(
                expected=Operator.COLON,
                actual=self.token_iterator.peek(),
            ),
        )

        type_token = self.token_iterator.peek()
        if not is_identifier(type_token):
            raise MissingTypeIdentifierError(
                argument_name=identifier_token.name,
                actual=type_token,
            )
        self._consume()

        return ArgumentNode(identifier=identifier_token, type_identifier=type_token)

    def _parse_arguments(self) -> ArgumentsNode:
        arguments = []

        argument = self._parse_argument()
        while argument is not None:
            arguments.append(argument)

            if not is_operator(self.token_iterator.peek(), Operator.COMMA):
                break
            self._consume()

            argument = self._parse_argument()

        return ArgumentsNode(arguments=arguments)

    def _parse_block(self) -> BlockNode:
        self._expect(
            create_operator_predicate(Operator.LEFT_BRACE),
            error=BlockMissingInitialBraceError(actual=self.token_iterator.peek()),
        )
        statements = []

        while not is_operator(self.token_iterator.peek(), operator=Operator.RIGHT_BRACE):
            statements.append(self._parse_statement())

        return BlockNode(statements=statements)

    def _parse_func_decleration(self) -> FuncDeclerationNode:
        identifier = self._expect(
            is_identifier,
            error=MissingIdentifierInFuncDeclerationError(actual=self.token_iterator.peek()),
        )

        self._expect(
            predicate=create_operator_predicate(Operator.LEFT_PAREN),
            error=MissingLeftParenInFuncDeclerationError(actual=self.token_iterator.peek()),
        )
        arguments = self._parse_arguments()
        self._expect(
            predicate=create_operator_predicate(Operator.RIGHT_PAREN),
            error=MissingRightParenInFuncDeclerationError(actual=self.token_iterator.peek()),
        )
        block = self._parse_block()

        return FuncDeclerationNode(identifier=identifier, arguments=arguments, block=block)
