import pytest

from vdsh.core.errors import CharIteratorIsOverError
from vdsh.core.iterator import PeekableIterator
from vdsh.core.pipeline import CharIterator


def test_peek_does_not_consume() -> None:
    it = PeekableIterator(CharIterator("ab"))

    assert it.peek() == "a"
    assert it.peek() == "a"
    assert it.next() == "a"
    assert it.next() == "b"
    assert it.is_over() is True


def test_next_after_peek() -> None:
    it = PeekableIterator(CharIterator("x"))

    assert it.peek() == "x"
    assert it.next() == "x"
    assert it.is_over() is True


def test_next_without_peek() -> None:
    it = PeekableIterator(CharIterator("ab"))

    assert it.next() == "a"
    assert it.peek() == "b"
    assert it.next() == "b"
    assert it.is_over() is True


def test_is_over_false_when_peeked() -> None:
    it = PeekableIterator(CharIterator("a"))

    assert it.peek() == "a"
    assert it.is_over() is False
    assert it.next() == "a"
    assert it.is_over() is True


def test_is_over_true_only_when_underlying_is_over_and_not_peeked() -> None:
    it = PeekableIterator(CharIterator("a"))

    assert it.is_over() is False
    assert it.next() == "a"
    assert it.is_over() is True


def test_peek_past_end_raises() -> None:
    it = PeekableIterator(CharIterator(""))

    assert it.is_over() is True
    with pytest.raises(CharIteratorIsOverError):
        it.peek()


def test_next_past_end_raises() -> None:
    it = PeekableIterator(CharIterator("a"))

    assert it.next() == "a"
    with pytest.raises(CharIteratorIsOverError):
        it.next()


def test_interleaved_peek_and_next() -> None:
    it = PeekableIterator(CharIterator("abc"))

    assert it.peek() == "a"
    assert it.next() == "a"
    assert it.peek() == "b"
    assert it.next() == "b"
    assert it.peek() == "c"
    assert it.next() == "c"
    assert it.is_over() is True


def test_unicode_support() -> None:
    it = PeekableIterator(CharIterator("א🙂β"))

    assert it.peek() == "א"
    assert it.next() == "א"
    assert it.peek() == "🙂"
    assert it.next() == "🙂"
    assert it.peek() == "β"
    assert it.next() == "β"
    assert it.is_over() is True


def test_single_character_invariant() -> None:
    it = PeekableIterator(CharIterator("hello"))

    while not it.is_over():
        ch = it.peek()
        assert isinstance(ch, str)
        assert len(ch) == 1
        assert it.next() == ch
