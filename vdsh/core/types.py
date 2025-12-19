from typing import Protocol


class BaseCreator[T](Protocol):
    def create(self) -> T: ...


class BaseTransformer[I, O](Protocol):
    def transform(self, data: I) -> O: ...


class BaseValidator[T](Protocol):
    def validate(self, data: T) -> None: ...


class StaticCreator[T](BaseCreator[T]):
    def __init__(self, value: T) -> None:
        self.value = value

    def create(self) -> T:
        return self.value


class StaticTransformer[O](BaseTransformer[None, O]):
    def __init__(self, value: O) -> None:
        self.value = value

    def transform(self, data: None = None) -> O:
        return data or self.value
