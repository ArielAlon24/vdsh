from vdsh.core.models.ast import BaseASTNode
from vdsh.core.types import BaseTransformer


class Optimizer(BaseTransformer[BaseASTNode, BaseASTNode]):
    def transform(self, data: BaseASTNode) -> BaseASTNode:
        optimized_data = data

        return optimized_data  # noqa: RET504
