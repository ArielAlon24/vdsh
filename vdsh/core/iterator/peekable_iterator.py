from dataclasses import dataclass

from vdsh.core.errors import IteratorIsOverError
from vdsh.core.iterator.base_iterator import BaseIterator


@dataclass
class PeekableIteratorState[T]:
    value: T


class PeekableIterator[T](BaseIterator[T]):
    def __init__(self, char_iterator: BaseIterator[T]) -> None:
        self._iterator = char_iterator
        self._peek_state: PeekableIteratorState[T] | None = None

    def peek(self) -> T:
        if self._peek_state is None:
            if self._iterator.is_over():
                raise IteratorIsOverError("Atempted to peek past iterator length")

            self._peek_state = PeekableIteratorState(self._iterator.next())

        return self._peek_state.value

    def next(self) -> T:
        if self._peek_state is not None:
            value = self._peek_state.value
            self._peek_state = None

            return value

        return self._iterator.next()

    def is_over(self) -> bool:
        if self._peek_state is not None:
            return False

        return self._iterator.is_over()
