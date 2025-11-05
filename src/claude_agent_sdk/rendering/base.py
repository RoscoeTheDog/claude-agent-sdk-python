"""Base abstractions for the rendering system.

This module provides abstract base classes for formatters and handlers,
along with the main MessageRenderer coordinator.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import Message


class Formatter(ABC):
    """Abstract base class for message formatters.

    Formatters define HOW messages are rendered (format style).
    Subclasses must implement format methods for each message type.
    """

    @abstractmethod
    def format(self, message: "Message") -> str:
        """Format a message into a string representation.

        Args:
            message: The message to format

        Returns:
            Formatted string representation
        """
        pass


class Handler(ABC):
    """Abstract base class for output handlers.

    Handlers define WHERE messages are rendered (console, file, etc.).
    Subclasses must implement the emit method for actual output.
    """

    @abstractmethod
    def emit(self, formatted_output: str, message: "Message") -> None:
        """Output the formatted message.

        Args:
            formatted_output: The formatted string to output
            message: The original message object
        """
        pass

    def should_render(self, message: "Message") -> bool:
        """Determine if this message should be rendered.

        Args:
            message: The message to check

        Returns:
            True if the message should be rendered, False otherwise
        """
        # Default: render all messages
        # Subclasses can override for filtering logic
        return True

    def handle(self, message: "Message", formatter: Formatter) -> None:
        """Process a message: filter, format, and emit.

        Args:
            message: The message to handle
            formatter: The formatter to use
        """
        if self.should_render(message):
            formatted = formatter.format(message)
            self.emit(formatted, message)


class MessageRenderer:
    """Main rendering coordinator that manages handlers.

    This class coordinates the rendering of messages by dispatching
    them to all registered handlers.
    """

    def __init__(self) -> None:
        """Initialize the message renderer."""
        self._handlers: list[Handler] = []

    def add_handler(self, handler: Handler) -> None:
        """Add a handler to the renderer.

        Args:
            handler: The handler to add
        """
        if handler not in self._handlers:
            self._handlers.append(handler)

    def remove_handler(self, handler: Handler) -> None:
        """Remove a handler from the renderer.

        Args:
            handler: The handler to remove
        """
        if handler in self._handlers:
            self._handlers.remove(handler)

    def render(self, message: "Message", formatter: Formatter) -> None:
        """Render a message using all registered handlers.

        Args:
            message: The message to render
            formatter: The formatter to use
        """
        for handler in self._handlers:
            try:
                handler.handle(message, formatter)
            except Exception:
                # One handler failure shouldn't stop others
                # In production, this should log the error
                pass
