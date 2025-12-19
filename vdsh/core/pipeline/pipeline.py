from dataclasses import dataclass

from vdsh.core.models.ast import BaseASTNode
from vdsh.core.types import BaseCreator, BaseTransformer, BaseValidator


@dataclass
class Pipeline:
    parser: BaseCreator[BaseASTNode]
    optimizer: BaseTransformer[BaseASTNode, BaseASTNode]
    type_checker: BaseValidator[BaseASTNode]
    code_generator: BaseTransformer[BaseASTNode, str]

    def run(self) -> str:
        ast = self.parser.create()
        ast = self.optimizer.transform(ast)
        self.type_checker.validate(ast)
        return self.code_generator.transform(ast)
