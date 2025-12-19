from vdsh.core.models.ast import (
    ArgumentNode,
    ArgumentsNode,
    BaseASTNode,
    BinaryOperationNode,
    BlockNode,
    FuncStatementNode,
    IdentifierNode,
    LetStatementNode,
    NumberLiteralNode,
    StringLiteralNode,
    UnaryOperationNode,
)
from vdsh.core.types import BaseTransformer

VDSH_IDENTIFIER_FORMAT = "__VDSH__{name}"


class CodeGenerator(BaseTransformer[BaseASTNode, str]):
    def transform(self, data: BaseASTNode) -> str:
        return self._generate(data)

    def _generate(self, node: BaseASTNode) -> str:
        generators = {
            BinaryOperationNode: self._generate_binary_operation,
            UnaryOperationNode: self._generate_unary_operation,
            StringLiteralNode: self._generate_string_literal,
            IdentifierNode: self._generate_identifier,
            NumberLiteralNode: self._generate_number_literal,
            ArgumentsNode: self._generate_arguments,
            LetStatementNode: self._generate_let_statement,
            FuncStatementNode: self._generate_func_statement,
            BlockNode: self._generate_block,
        }

        return generators[type(node)](node)

    def _generate_binary_operation(self, node: BinaryOperationNode) -> str:
        return f"$(({self._generate(node.left)}{node.operator.kind.value}{self._generate(node.right)}))"

    def _generate_unary_operation(self, node: UnaryOperationNode) -> str:
        return f"$(({node.operator.kind.value}{self._generate(node.value)}))"

    def _generate_string_literal(self, node: StringLiteralNode) -> str:
        return f'"{node.string}"'

    def _generate_identifier(self, node: IdentifierNode) -> str:
        return f"${VDSH_IDENTIFIER_FORMAT.format(name=node.identifier.name)}"

    def _generate_number_literal(self, node: NumberLiteralNode) -> str:
        if node.number.value.is_integer():
            return str(int(node.number.value))

        return str(node.number)

    def _generate_arguments(self, node: ArgumentsNode) -> str:
        assingments = ""

        for index, argument in enumerate(node.arguments):
            assingments += (
                f"local {VDSH_IDENTIFIER_FORMAT.format(name=argument.identifier.name)}=${index}\n"
            )

        return assingments

    def _generate_argument(self, node: ArgumentNode) -> str:
        return VDSH_IDENTIFIER_FORMAT.format(name=node.identifier.name)

    def _generate_block(self, node: BlockNode) -> str:
        inner = "\n".join([self._generate(statement) for statement in node.statements])

        return "{\n" + inner + "\n}"

    def _generate_let_statement(self, node: LetStatementNode) -> str:
        return f"local {VDSH_IDENTIFIER_FORMAT.format(name=node.assignment.identifier.name)}={self._generate(node.assignment.value)}"

    def _generate_func_statement(self, node: FuncStatementNode) -> str:
        signature = (
            f"function {VDSH_IDENTIFIER_FORMAT.format(name=node.decelration.identifier.name)}()"
        )

        arguments = self._generate_arguments(node.decelration.arguments)
        body = "\n".join(
            self._generate(statement) for statement in node.decelration.block.statements
        )

        return signature + "{\n" + arguments + body + "\n}"
