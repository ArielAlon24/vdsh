from typing import Protocol


class Creator[T](Protocol):
    def create(self) -> T: ...


class Transformer[I, O](Protocol):
    def transform(self, data: I) -> O: ...


class StaticCreator[T](Creator[T]):
    def __init__(self, value: T) -> None:
        self.value = value

    def create(self) -> T:
        return self.value


class StaticTransformer[O](Transformer[None, O]):
    def __init__(self, value: O) -> None:
        self.value = value

    def transform(self, data: None = None) -> O:
        return data or self.value
