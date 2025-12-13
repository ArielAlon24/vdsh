from collections.abc import Sequence

from vdsh.core.errors import IteratorIsOverError
from vdsh.core.iterator.base_iterator import BaseIterator


class SequenceIterator[T](BaseIterator[T]):
    def __init__(self, sequence: Sequence[T]) -> None:
        self.sequence = sequence
        self._position = 0

    def next(self) -> T:
        if self.is_over():
            raise IteratorIsOverError(
                "Attempted to get the next character in an exhausted iterator",
            )

        ch = self.sequence[self._position]
        self._position += 1
        return ch

    def is_over(self) -> bool:
        return self._position >= len(self.sequence)
