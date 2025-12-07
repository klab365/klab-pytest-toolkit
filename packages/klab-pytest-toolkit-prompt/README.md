# Klab Pytest Toolkit - Prompt

Custom pytest fixtures for interactive user prompts during test execution using tkinter UI dialogs.

## Installation

```bash
pip install klab-pytest-toolkit-prompt
```

## Features

- 🎯 **UI Prompts** - Display informational messages and get user confirmations during tests
- ⏱️ **Timeout Support** - Auto-close dialogs after specified timeout
- 🖥️ **Tkinter-based** - Uses Python's built-in tkinter (no external dependencies)
- 🧪 **Test-Friendly** - Seamlessly integrates with pytest workflow

## Use Cases

- Manual test verification steps
- Confirming destructive operations in tests
- Pausing test execution for user inspection
- Interactive test scenarios requiring human input
- Visual inspection checkpoints

## Quick Start

### Show Information Dialog

```python
def test_with_info(ui_prompt):
    """Display information to the user."""
    ui_prompt.show_info("Test is about to perform a critical operation")
    
    # Continue with test
    perform_operation()
```

### Get User Confirmation

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

### Using the Factory

```python
def test_with_factory(ui_prompt_factory):
    """Create multiple prompt instances."""
    prompt1 = ui_prompt_factory.create_prompt()
    prompt2 = ui_prompt_factory.create_prompt()
    
    prompt1.show_info("First dialog")
    
    if prompt2.confirm_action("Proceed?"):
        # Do something
        pass
```

### With Timeout (Auto-close)

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

## Available Fixtures

### `ui_prompt`

Provides a ready-to-use `UiPrompt` instance.

**Methods:**
- `show_info(message: str, timeout: Optional[int] = None) -> None`
- `confirm_action(message: str, timeout: Optional[int] = None) -> bool`

**Example:**

```python
def test_example(ui_prompt):
    ui_prompt.show_info("Starting test")
    
    if ui_prompt.confirm_action("Ready to proceed?"):
        # Test continues
        pass
```

### `ui_prompt_factory`

Factory fixture for creating multiple prompt instances.

**Factory Method:**

```python
create_prompt() -> UiPrompt
```

**Example:**

```python
def test_example(ui_prompt_factory):
    prompt = ui_prompt_factory.create_prompt()
    prompt.show_info("Test information")
```

## API Reference

### UiPrompt

Main class for displaying UI prompts to users.

**Methods:**

#### `show_info(message: str, timeout: Optional[int] = None) -> None`

Display an informational message dialog.

**Parameters:**
- `message` (str) - The message to display
- `timeout` (Optional[int]) - Auto-close timeout in seconds

**Example:**

```python
ui_prompt.show_info("Operation completed successfully")
ui_prompt.show_info("Auto-closing message", timeout=3)
```

#### `confirm_action(message: str, timeout: Optional[int] = None) -> bool`

Display a confirmation dialog with Yes/No buttons.

**Parameters:**
- `message` (str) - The confirmation message
- `timeout` (Optional[int]) - Auto-close timeout in seconds (returns False if expires)

**Returns:**
- `bool` - True if user clicked Yes, False if No or timeout expired

**Example:**

```python
if ui_prompt.confirm_action("Delete all data?"):
    delete_data()
else:
    print("Cancelled")

# With timeout
result = ui_prompt.confirm_action("Quick decision needed", timeout=5)
```

### UiPromptFactory

Factory for creating `UiPrompt` instances.

**Methods:**

#### `create_prompt() -> UiPrompt`

Create a new UI prompt instance.

**Returns:**
- `UiPrompt` - A new prompt instance

**Example:**

```python
factory = UiPromptFactory()
prompt = factory.create_prompt()
```

## Real-World Examples

### Manual Verification Step

```python
def test_visual_inspection(ui_prompt, api_client):
    """Test with manual visual verification."""
    # Perform automated steps
    response = api_client.create_user({"name": "Test User"})
    
    # Ask user to verify in external system
    ui_prompt.show_info(
        f"Please verify user {response['id']} exists in the admin panel"
    )
    
    # Continue with automated verification
    assert api_client.get_user(response['id']) is not None
```

### Conditional Destructive Test

```python
def test_database_cleanup(ui_prompt, database):
    """Test that requires user confirmation for destructive action."""
    if not ui_prompt.confirm_action(
        "This will DELETE all test data. Continue?"
    ):
        pytest.skip("User cancelled destructive test")
    
    # Perform cleanup
    database.truncate_all_tables()
    
    # Verify
    assert database.count_records() == 0
```

### Debugging Pause Point

```python
def test_with_debug_pause(ui_prompt, app):
    """Pause test execution for debugging."""
    app.navigate_to("/dashboard")
    
    # Pause for manual inspection
    ui_prompt.show_info(
        "Application is now at dashboard. "
        "Inspect manually, then click OK to continue."
    )
    
    # Continue test
    app.click_button("Submit")
```

### Progressive Test Steps

```python
def test_multi_step_workflow(ui_prompt, app):
    """Guide user through multi-step test."""
    ui_prompt.show_info("Step 1: Navigate to login page")
    app.navigate_to("/login")
    
    if ui_prompt.confirm_action("Is the login page displayed correctly?"):
        ui_prompt.show_info("Step 2: Enter credentials")
        app.login("user@example.com", "password")
        
        if ui_prompt.confirm_action("Did login succeed?"):
            ui_prompt.show_info("Step 3: Verify dashboard")
            assert app.is_on_dashboard()
        else:
            pytest.fail("Login verification failed")
    else:
        pytest.fail("Login page not displayed correctly")
```

### Time-Limited User Input

```python
def test_time_sensitive_verification(ui_prompt, notification_service):
    """Test with time-limited user verification."""
    # Trigger notification
    notification_service.send_notification("Test Alert")
    
    # Give user 30 seconds to check their device
    result = ui_prompt.confirm_action(
        "Did you receive the notification on your device? "
        "(Auto-fail in 30 seconds)",
        timeout=30
    )
    
    assert result, "User did not confirm notification receipt"
```

## Direct Class Usage

You can also use the classes directly without fixtures:

```python
from klab_pytest_toolkit_prompt import UiPrompt, UiPromptFactory

# Direct instantiation
prompt = UiPrompt()
prompt.show_info("Direct usage example")

# Using factory
factory = UiPromptFactory()
prompt = factory.create_prompt()

if prompt.confirm_action("Continue?"):
    print("User confirmed")
```

## Running Manual Tests

The package includes manual tests that require user interaction. Run them with:

```bash
# Run only manual tests
pytest -m manual

# Run specific manual test
pytest tests/test_prompt.py::test_show_info_manual -m manual
```

## Configuration

### Pytest Markers

Add to your `pytest.ini` or `pyproject.toml`:

```ini
[tool.pytest.ini_options]
markers = [
    "manual: marks tests as requiring manual user interaction (deselect with '-m \"not manual\"')"
]
```

### Skipping Manual Tests

By default, tests marked with `@pytest.mark.manual` can be excluded:

```bash
# Run all tests except manual ones
pytest -m "not manual"
```

## Notes

- **Thread Safety**: Tkinter dialogs run in the main thread
- **Headless Environments**: Will fail in headless environments (no display)
- **Test CI/CD**: Skip prompt tests in CI/CD pipelines using markers
- **Timeout Behavior**: When timeout expires, `confirm_action` returns `False`

## Examples

See the test files for comprehensive examples:
- `tests/test_prompt.py` - UI prompt examples with manual test cases

## License

MIT
