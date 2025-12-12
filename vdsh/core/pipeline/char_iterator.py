from vdsh.core.errors import CharIteratorIsOverError
from vdsh.core.iterator.base_iterator import BaseIterator


class CharIterator(BaseIterator[str]):
    def __init__(self, data: str) -> None:
        self._data = data
        self._position = 0

    def next(self) -> str:
        if self.is_over():
            raise CharIteratorIsOverError(
                "Attempted to get the next character in an exhausted iterator",
            )

        ch = self._data[self._position]
        self._position += 1
        return ch

    def is_over(self) -> bool:
        return self._position >= len(self._data)
