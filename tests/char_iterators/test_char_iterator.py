import pytest

from vdsh.core.errors import CharIteratorIsOverError
from vdsh.core.pipeline import CharIterator


def test_iterates_all_characters() -> None:
    it = CharIterator("abc")

    assert it.is_over() is False
    assert it.next() == "a"
    assert it.is_over() is False
    assert it.next() == "b"
    assert it.is_over() is False
    assert it.next() == "c"
    assert it.is_over() is True


def test_empty__is_over_immediately() -> None:
    it = CharIterator("")

    assert it.is_over() is True
    with pytest.raises(CharIteratorIsOverError):
        it.next()


def test_stop_iteration_after_end() -> None:
    it = CharIterator("x")

    assert it.next() == "x"
    assert it.is_over() is True

    with pytest.raises(CharIteratorIsOverError):
        it.next()


def test_is_over_does_not_advance() -> None:
    it = CharIterator("ab")

    assert it.is_over() is False
    assert it.is_over() is False
    assert it.next() == "a"


def test_multiple_calls_past_end() -> None:
    it = CharIterator("a")

    assert it.next() == "a"
    assert it.is_over() is True

    for _ in range(3):
        with pytest.raises(CharIteratorIsOverError):
            it.next()


def test_unicode_characters() -> None:
    it = CharIterator("אβ🙂")

    assert it.next() == "א"
    assert it.next() == "β"
    assert it.next() == "🙂"
    assert it.is_over() is True


def test_single_character_invariant() -> None:
    it = CharIterator("hello")

    while not it.is_over():
        ch = it.next()
        assert isinstance(ch, str)
        assert len(ch) == 1
