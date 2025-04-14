# Run `poetry install`
install:
    poetry install

# run poetry to show deps
showdeps: install
    echo "CURRENT:"
    poetry show --tree
    echo
    echo "LATEST:"
    poetry show --latest

# Runs linting for python code
lint:
    poetry run mypy .

# Formats you code with Black, and sorts imports with isort
format:
    poetry run black .
    poetry run isort .

# Checks if the code is formatted correctly
check-format:
    poetry run black --check .
    poetry run isort --check .

# run pytest with coverage
test:
    poetry run pytest \
        --junitxml=pytest.xml \
        --cov-report=term-missing:skip-covered \
        --cov=klab_pytest_toolkit \
        tests
