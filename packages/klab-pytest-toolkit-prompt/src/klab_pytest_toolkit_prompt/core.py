import abc
from typing import Optional


class PromptInterface(abc.ABC):
    """Abstract base class for prompt interfaces."""

    @abc.abstractmethod
    def show_info(self, message: str, timeout: Optional[int] = None) -> None:
        """Display an informational message to the user."""
        raise NotImplementedError

    def confirm_action(self, message: str, timeout: Optional[int] = None) -> Optional[bool]:
        """Prompt the user to confirm an action."""
        raise NotImplementedError

    def get_user_input(self, prompt: str, timeout: Optional[int] = None) -> Optional[str]:
        """Prompt the user for input."""
        raise NotImplementedError
