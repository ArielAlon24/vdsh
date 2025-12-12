check_lint:
    ruff check vdsh tests

check_type:
    mypy vdsh tests

test:
    pytest tests
