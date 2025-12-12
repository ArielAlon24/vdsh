from typing import Protocol


class BaseIterator[T](Protocol):
    """A generic iterator like `typing.Iterator`"""

    def next(self) -> T: ...

    def is_over(self) -> bool: ...
