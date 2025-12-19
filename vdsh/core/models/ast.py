from dataclasses import dataclass, field

from vdsh.core.models.token import (
    IdentifierToken,
    KeywordToken,
    NumberToken,
    OperatorToken,
    StringToken,
)

type StatementNode = LetStatementNode


@dataclass(frozen=True)
class BaseASTNode:
    pass


@dataclass(frozen=True)
class IdentifierNode(BaseASTNode):
    identifier: IdentifierToken


@dataclass(frozen=True)
class NumberLiteralNode(BaseASTNode):
    number: NumberToken


@dataclass(frozen=True)
class StringLiteralNode(BaseASTNode):
    string: StringToken


@dataclass(frozen=True)
class UnaryOperationNode(BaseASTNode):
    value: BaseASTNode
    operator: OperatorToken


@dataclass(frozen=True)
class BinaryOperationNode(BaseASTNode):
    left: BaseASTNode
    right: BaseASTNode
    operator: OperatorToken


@dataclass(frozen=True)
class ArgumentNode(BaseASTNode):
    identifier: IdentifierToken
    type_identifier: IdentifierToken


@dataclass(frozen=True)
class ArgumentsNode(BaseASTNode):
    arguments: list[ArgumentNode] = field(default_factory=list)


@dataclass(frozen=True)
class BlockNode(BaseASTNode):
    statements: list[StatementNode]


@dataclass(frozen=True)
class AssignmentNode(BaseASTNode):
    identifier: IdentifierToken
    value: BaseASTNode


@dataclass(frozen=True)
class LetStatementNode(BaseASTNode):
    let: KeywordToken
    assignment: AssignmentNode


@dataclass(frozen=True)
class FuncDeclerationNode(BaseASTNode):
    identifier: IdentifierToken
    arguments: ArgumentsNode
    block: BlockNode


@dataclass(frozen=True)
class FuncStatementNode(BaseASTNode):
    func: KeywordToken
    decelration: FuncDeclerationNode
