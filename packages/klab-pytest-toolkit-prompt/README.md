# Klab Pytest Toolkit - Prompt

[![PyPI](https://img.shields.io/pypi/v/klab-pytest-toolkit-prompt)](https://pypi.org/project/klab-pytest-toolkit-prompt/)
[![Python](https://img.shields.io/pypi/pyversions/klab-pytest-toolkit-prompt)](https://pypi.org/project/klab-pytest-toolkit-prompt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)

Custom pytest fixtures for interactive user prompts during test execution using tkinter UI dialogs.
The goal is to allow testers to interact with the test process, providing confirmations or displaying important information.

At the moment the package provides the following components:

- `PromptFactory`: Factory for creating prompt interface instances. Use it directly (or from within your own fixtures).

## Installation

```bash
pip install klab-pytest-toolkit-prompt
```

## Usage

### UI Prompt

**Create the fixture**

Use the factory class `PromptFactory` directly (or from within your own fixture).

```python
from klab_pytest_toolkit_prompt import PromptFactory

@pytest.fixture
def ui_prompt() -> PromptInterface:
    """Fixture to provide a UI prompt interface for user interaction during tests."""
    return PromptFactory.create_prompt(prompt_type=PromptFactory.PromptType.UI_PROMPT)
```

**Functions**

The following functions are available on the `PromptInterface` instance:

**Show Information Dialog**

```python
def test_with_info(ui_prompt):
    """Display information to the user."""
    ui_prompt.show_info("Test is about to perform a critical operation")
    
    # Continue with test
    perform_operation()
```

**Get User Confirmation**

```python
def test_with_confirmation(ui_prompt):
    """Get user confirmation before proceeding."""
    if ui_prompt.confirm_action("Continue with destructive test?"):
        # User clicked Yes
        perform_destructive_operation()
    else:
        # User clicked No
        pytest.skip("User cancelled the test")
```

**With Timeout (Auto-close)**

```python
def test_with_timeout(ui_prompt):
    """Show dialog that auto-closes after timeout."""
    # Dialog closes automatically after 5 seconds
    ui_prompt.show_info("This will auto-close in 5 seconds", timeout=5)
    
    # Confirmation dialog with timeout (returns False if timeout expires)
    result = ui_prompt.confirm_action(
        "Click within 10 seconds",
        timeout=10
    )
```

## Examples

See the `tests` directory for example test cases demonstrating the usage of the prompt components.

## Links

- [Source code](https://github.com/klab365/klab-pytest-toolkit/tree/main/packages/klab-pytest-toolkit-prompt)
- [PyPI](https://pypi.org/project/klab-pytest-toolkit-prompt/)
- [Issue tracker](https://github.com/klab365/klab-pytest-toolkit/issues)

## License

MIT
