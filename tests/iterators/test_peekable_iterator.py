import pytest

from vdsh.core.errors import IteratorIsOverError
from vdsh.core.iterator import PeekableIterator, SequenceIterator


def test_peek_does_not_consume() -> None:
    it = PeekableIterator(SequenceIterator("ab"))

    assert it.peek() == "a"
    assert it.peek() == "a"
    assert it.next() == "a"
    assert it.next() == "b"
    assert it.is_over() is True


def test_next_after_peek() -> None:
    it = PeekableIterator(SequenceIterator("x"))

    assert it.peek() == "x"
    assert it.next() == "x"
    assert it.is_over() is True


def test_next_without_peek() -> None:
    it = PeekableIterator(SequenceIterator("ab"))

    assert it.next() == "a"
    assert it.peek() == "b"
    assert it.next() == "b"
    assert it.is_over() is True


def test_is_over_false_when_peeked() -> None:
    it = PeekableIterator(SequenceIterator("a"))

    assert it.peek() == "a"
    assert it.is_over() is False
    assert it.next() == "a"
    assert it.is_over() is True


def test_is_over_true_only_when_underlying_is_over_and_not_peeked() -> None:
    it = PeekableIterator(SequenceIterator("a"))

    assert it.is_over() is False
    assert it.next() == "a"
    assert it.is_over() is True


def test_peek_past_end_raises() -> None:
    it = PeekableIterator(SequenceIterator(""))

    assert it.is_over() is True
    with pytest.raises(IteratorIsOverError):
        it.peek()


def test_next_past_end_raises() -> None:
    it = PeekableIterator(SequenceIterator("a"))

    assert it.next() == "a"
    with pytest.raises(IteratorIsOverError):
        it.next()


def test_interleaved_peek_and_next() -> None:
    it = PeekableIterator(SequenceIterator("abc"))

    assert it.peek() == "a"
    assert it.next() == "a"
    assert it.peek() == "b"
    assert it.next() == "b"
    assert it.peek() == "c"
    assert it.next() == "c"
    assert it.is_over() is True


def test_single_character_invariant() -> None:
    it = PeekableIterator(SequenceIterator("hello"))

    while not it.is_over():
        ch = it.peek()
        assert isinstance(ch, str)
        assert len(ch) == 1
        assert it.next() == ch
