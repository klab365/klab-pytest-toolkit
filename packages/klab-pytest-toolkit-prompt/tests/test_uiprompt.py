import subprocess
import threading
import time

from klab_pytest_toolkit_prompt.core import PromptFactory, PromptInterface
import pytest


def _click_dialog_button(button_name: str, delay: float = 1.0) -> None:
    """Click a button in a tkinter dialog using xdotool.

    Args:
        button_name: The button text to click (e.g., "Yes", "No", "OK")
        delay: Delay before clicking to allow dialog to appear
    """
    time.sleep(delay)
    try:
        # Find the window and send key based on button
        if button_name.lower() in ("yes", "ok"):
            # Tab to Yes/OK and press Enter, or just press Enter (default)
            subprocess.run(["xdotool", "key", "Return"], check=True, timeout=2)
        elif button_name.lower() == "no":
            # Tab to No button and press Enter
            subprocess.run(["xdotool", "key", "Tab", "Return"], check=True, timeout=2)
    except (subprocess.SubprocessError, FileNotFoundError):
        pass  # xdotool not available or failed


def _type_and_submit(text: str, delay: float = 1.0) -> None:
    """Type text into input dialog and submit.

    Args:
        text: The text to type
        delay: Delay before typing to allow dialog to appear
    """
    time.sleep(delay)
    try:
        # Find and focus the dialog window first
        result = subprocess.run(
            ["xdotool", "search", "--name", "Input Required"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0 and result.stdout.strip():
            window_id = result.stdout.strip().split("\n")[0]
            # Use windowfocus instead of windowactivate for xvfb without window manager
            subprocess.run(
                ["xdotool", "windowfocus", "--sync", window_id],
                check=True,
                timeout=2,
            )
        subprocess.run(["xdotool", "type", "--", text], check=True, timeout=2)
        subprocess.run(["xdotool", "key", "Return"], check=True, timeout=2)
    except (subprocess.SubprocessError, FileNotFoundError):
        pass  # xdotool not available or failed


@pytest.fixture
def ui_prompt(prompt_factory: PromptFactory) -> PromptInterface:
    """
    Convenience fixture that provides a ready-to-use UI prompt instance.

    Returns:
        PromptInterface: A UI prompt instance ready to use
    """
    return prompt_factory.create_prompt(prompt_type=PromptFactory.PromptType.UI_PROMPT)


def test_show_info_displays_and_closes(ui_prompt: PromptInterface):
    """Test that show_info displays a dialog that can be dismissed."""
    # Start a thread to click OK after dialog appears
    clicker = threading.Thread(target=_click_dialog_button, args=("ok",))
    clicker.start()

    # This should not raise and should complete when OK is clicked
    ui_prompt.show_info("This is an informational message.")

    clicker.join(timeout=5)


def test_confirm_action_returns_true_on_yes(ui_prompt: PromptInterface):
    """Test that confirm_action returns True when Yes is clicked."""
    clicker = threading.Thread(target=_click_dialog_button, args=("yes",))
    clicker.start()

    result = ui_prompt.confirm_action("Do you want to proceed?")

    clicker.join(timeout=5)
    assert result is True


def test_confirm_action_returns_false_on_no(ui_prompt: PromptInterface):
    """Test that confirm_action returns False when No is clicked."""
    clicker = threading.Thread(target=_click_dialog_button, args=("no",))
    clicker.start()

    result = ui_prompt.confirm_action("Do you want to proceed?")

    clicker.join(timeout=5)
    assert result is False


def test_confirm_action_returns_false_on_timeout(ui_prompt: PromptInterface):
    """Test that confirm_action returns False when timeout expires."""
    result = ui_prompt.confirm_action("This will timeout.", timeout=1)
    assert result is False


def test_get_user_input_returns_typed_text(ui_prompt: PromptInterface):
    """Test that get_user_input returns the text typed by user."""
    expected_input = "TestUser"
    typer = threading.Thread(target=_type_and_submit, args=(expected_input,))
    typer.start()

    result = ui_prompt.get_user_input("Please enter your name:")

    typer.join(timeout=5)
    assert result == expected_input


def test_get_user_input_returns_none_on_timeout(ui_prompt: PromptInterface):
    """Test that get_user_input returns None when timeout expires."""
    result = ui_prompt.get_user_input("This will timeout.", timeout=1)
    assert result is None
