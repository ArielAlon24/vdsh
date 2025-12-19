from vdsh.core.models.ast import BaseASTNode
from vdsh.core.types import BaseValidator


class TypeChecker(BaseValidator[BaseASTNode]):
    def validate(self, data: BaseASTNode) -> None:
        return None
