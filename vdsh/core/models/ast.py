from dataclasses import dataclass

from vdsh.core.models.token import Operator


@dataclass(frozen=True)
class BaseASTNode:
    pass


@dataclass(frozen=True)
class BaseExpressionNode(BaseASTNode):
    pass


@dataclass(frozen=True)
class IdentifierNode(BaseExpressionNode):
    name: str


@dataclass(frozen=True)
class NumberLiteralNode(BaseExpressionNode):
    value: float


@dataclass(frozen=True)
class StringLiteralNode(BaseExpressionNode):
    value: str


@dataclass(frozen=True)
class UnaryOperationNode(BaseExpressionNode):
    value: BaseASTNode
    operator: Operator


@dataclass(frozen=True)
class BinaryOperationNode(BaseExpressionNode):
    left: BaseASTNode
    right: BaseASTNode
    operator: Operator
