# Klab Pytest Toolkit - Decorators

[![PyPI](https://img.shields.io/pypi/v/klab-pytest-toolkit-decorators)](https://pypi.org/project/klab-pytest-toolkit-decorators/)
[![Python](https://img.shields.io/pypi/pyversions/klab-pytest-toolkit-decorators)](https://pypi.org/project/klab-pytest-toolkit-decorators/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)

Custom pytest decorators for marking and annotating tests.

At the moment the package provides the following decorator:

- `@requirement(id: str)`: Marks a test with a requirement ID for traceability. The ID is added to the JUnit XML output.

## Installation

```bash
pip install klab-pytest-toolkit-decorators
```

## Usage

### Requirement Decorator

Mark tests with requirement IDs for traceability:

```python
from klab_pytest_toolkit_decorators import requirement

@requirement("REQ-001")
def test_something():
    assert True

@requirement("REQ-002")
async def test_async_something():
    assert True
```

The decorator works with both synchronous and asynchronous test functions. The requirement IDs are added to the JUnit XML output.

## Links

- [Source code](https://github.com/klab365/klab-pytest-toolkit/tree/main/packages/klab-pytest-toolkit-decorators)
- [PyPI](https://pypi.org/project/klab-pytest-toolkit-decorators/)
- [Issue tracker](https://github.com/klab365/klab-pytest-toolkit/issues)

## License

MIT
