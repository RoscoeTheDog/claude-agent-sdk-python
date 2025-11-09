"""Abstract base classes for the rendering system.

This module defines the core abstractions for message rendering:
- Formatter: Abstract base class for formatting messages
- Handler: Abstract base class for output handlers
- MessageRenderer: Main coordinator for rendering messages
"""

from abc import ABC, abstractmethod
from threading import Lock
from typing import TYPE_CHECKING

from ..types import (
    AssistantMessage,
    Message,
    ResultMessage,
    StreamEvent,
    SystemMessage,
    UserMessage,
)
from .config import RendererConfig

if TYPE_CHECKING:
    from .config import SystemMessageLevel



def _detect_system_message_severity(message: SystemMessage) -> "SystemMessageLevel":
    """Detect the severity level of a system message.

    Parses the message subtype to determine severity. Falls back to INFO
    if the severity cannot be determined.

    Args:
        message: SystemMessage to analyze

    Returns:
        SystemMessageLevel indicating the severity
    """
    from .config import SystemMessageLevel

    # Parse subtype to detect severity
    subtype_lower = message.subtype.lower()

    if "critical" in subtype_lower:
        return SystemMessageLevel.CRITICAL
    elif "error" in subtype_lower or "fail" in subtype_lower:
        return SystemMessageLevel.ERROR
    elif "warning" in subtype_lower or "warn" in subtype_lower:
        return SystemMessageLevel.WARNING
    elif "debug" in subtype_lower:
        return SystemMessageLevel.DEBUG
    else:
        # Default to INFO for "info" and unknown types
        return SystemMessageLevel.INFO

class Formatter(ABC):
    """Abstract base class for message formatters.

    Formatters convert Message objects into formatted strings according to
    a specific rendering style (e.g., Claude Code CLI format, JSON, etc.).

    Example:
        class MyFormatter(Formatter):
            def format_user_message(self, message: UserMessage) -> str:
                return f"User: {message.content}"

            def format_assistant_message(self, message: AssistantMessage) -> str:
                # ... format logic
                pass

            # Implement other abstract methods...
    """

    def __init__(self, config: RendererConfig | None = None) -> None:
        """Initialize formatter with configuration.

        Args:
            config: Rendering configuration. If None, uses default RendererConfig.
        """
        self.config = config or RendererConfig()

    def format(self, message: Message) -> str:
        """Format a message based on its type.

        This is the main entry point for formatting. It dispatches to
        the appropriate type-specific method.

        Args:
            message: The message to format

        Returns:
            Formatted string representation of the message
        """
        if isinstance(message, UserMessage):
            return self.format_user_message(message)
        elif isinstance(message, AssistantMessage):
            return self.format_assistant_message(message)
        elif isinstance(message, SystemMessage):
            return self.format_system_message(message)
        elif isinstance(message, ResultMessage):
            return self.format_result_message(message)
        else:  # StreamEvent
            return self.format_stream_event(message)

    @abstractmethod
    def format_user_message(self, message: UserMessage) -> str:
        """Format a user message.

        Args:
            message: UserMessage to format

        Returns:
            Formatted string
        """
        pass

    @abstractmethod
    def format_assistant_message(self, message: AssistantMessage) -> str:
        """Format an assistant message.

        Args:
            message: AssistantMessage to format

        Returns:
            Formatted string
        """
        pass

    @abstractmethod
    def format_system_message(self, message: SystemMessage) -> str:
        """Format a system message.

        Args:
            message: SystemMessage to format

        Returns:
            Formatted string
        """
        pass

    @abstractmethod
    def format_result_message(self, message: ResultMessage) -> str:
        """Format a result message.

        Args:
            message: ResultMessage to format

        Returns:
            Formatted string
        """
        pass

    @abstractmethod
    def format_stream_event(self, message: StreamEvent) -> str:
        """Format a stream event.

        Args:
            message: StreamEvent to format

        Returns:
            Formatted string
        """
        pass

    def _truncate_text(
        self, text: str, max_length: int, indicator: str = "... +{n} lines"
    ) -> str:
        """Truncate text with an indicator of how much was hidden.

        Args:
            text: Text to truncate
            max_length: Maximum number of characters to keep
            indicator: Format string for truncation indicator. Use {n} for number of lines.
                      Default: "... +{n} lines"

        Returns:
            Truncated text with indicator if text was truncated
        """
        if len(text) <= max_length:
            return text

        # Truncate and count hidden lines
        truncated = text[:max_length]
        remaining_text = text[max_length:]
        num_hidden_lines = remaining_text.count("\n") + 1

        # Add indicator
        if "{n}" in indicator:
            suffix = indicator.format(n=num_hidden_lines)
        else:
            suffix = indicator

        return truncated + "\n" + suffix

    def _indent_lines(self, text: str, indent: str = "  ") -> str:
        """Indent all lines in text with the given prefix.

        Args:
            text: Text to indent
            indent: Prefix to add to each line (default: two spaces)

        Returns:
            Indented text
        """
        lines = text.split("\n")
        return "\n".join(indent + line for line in lines)


class Handler(ABC):
    """Abstract base class for output handlers.

    Handlers control WHERE messages are rendered (e.g., stdout, file, etc.)
    and apply filtering logic to decide which messages to render.

    Example:
        class ConsoleHandler(Handler):
            def emit(self, formatted_output: str, message: Message) -> None:
                print(formatted_output)
    """

    def __init__(
        self, formatter: Formatter, config: RendererConfig | None = None
    ) -> None:
        """Initialize handler with formatter and configuration.

        Args:
            formatter: Formatter instance to use for formatting messages
            config: Rendering configuration. If None, uses formatter's config.
        """
        self.formatter = formatter
        self.config = config or formatter.config

    @abstractmethod
    def emit(self, formatted_output: str, message: Message) -> None:
        """Emit formatted output to the handler's destination.

        This method must be implemented by concrete handlers to
        define where/how the output is written.

        Args:
            formatted_output: Pre-formatted string to output
            message: Original message (for metadata)
        """
        pass

    def should_render(self, message: Message) -> bool:
        """Determine if a message should be rendered based on configuration.

        This implements the filtering logic based on:
        - Message type include/exclude lists
        - Render level
        - System message severity levels
        - Message-specific metadata

        Args:
            message: Message to evaluate

        Returns:
            True if message should be rendered, False otherwise
        """
        # Get message type name
        message_type = type(message).__name__

        # Check explicit exclusions first
        if message_type in self.config.exclude_message_types:
            return False

        # Check explicit inclusions
        if (
            self.config.include_message_types
            and message_type not in self.config.include_message_types
        ):
            return False

        # Apply render level filtering
        from .config import RenderLevel, SystemMessageLevel

        level = self.config.render_level

        # SystemMessage filtering with render-level-based severity control
        if isinstance(message, SystemMessage):
            # Map render levels to minimum severity thresholds
            # MINIMAL: only critical
            # STANDARD: error and above
            # DETAILED: all messages (debug and above)
            # DEBUG: all messages (debug and above)
            # ALL: all messages (debug and above)
            if level >= RenderLevel.DETAILED:
                # At DETAILED/DEBUG/ALL, show all system messages (DEBUG and above)
                min_severity = SystemMessageLevel.DEBUG
            elif level == RenderLevel.STANDARD:
                # At STANDARD, show ERROR and above (use configured default)
                min_severity = self.config.min_system_message_level
            elif level == RenderLevel.MINIMAL:
                # At MINIMAL, show only CRITICAL
                min_severity = SystemMessageLevel.CRITICAL
            else:
                # Below MINIMAL, hide all system messages
                return False

            severity = _detect_system_message_severity(message)
            return severity >= min_severity

        # StreamEvent only at ALL
        # All other message types pass
        return not (isinstance(message, StreamEvent) and level < RenderLevel.ALL)

    def handle(self, message: Message) -> None:
        """Handle a message: filter, format, and emit.

        This is the main entry point for processing a message.
        It orchestrates filtering, formatting, and output.

        Args:
            message: Message to handle
        """
        if not self.should_render(message):
            return

        formatted = self.formatter.format(message)
        if formatted:  # Only emit if there's content
            self.emit(formatted, message)


class MessageRenderer:
    """Main rendering coordinator with handler management.

    This class manages multiple handlers and dispatches messages to them.
    It provides thread safety for concurrent rendering.

    Example:
        renderer = MessageRenderer()
        renderer.add_handler(StreamHandler(formatter))
        renderer.add_handler(FileHandler(formatter, "output.txt"))
        renderer.render(message)
    """

    def __init__(self) -> None:
        """Initialize message renderer with empty handler list."""
        self._handlers: list[Handler] = []
        self._lock = Lock()

    def add_handler(self, handler: Handler) -> None:
        """Add a handler to the renderer.

        Args:
            handler: Handler instance to add
        """
        with self._lock:
            if handler not in self._handlers:
                self._handlers.append(handler)

    def remove_handler(self, handler: Handler) -> None:
        """Remove a handler from the renderer.

        Args:
            handler: Handler instance to remove
        """
        with self._lock:
            if handler in self._handlers:
                self._handlers.remove(handler)

    def clear_handlers(self) -> None:
        """Remove all handlers."""
        with self._lock:
            self._handlers.clear()

    def render(self, message: Message) -> None:
        """Render a message through all registered handlers.

        If a handler raises an exception, it is logged and rendering
        continues with other handlers.

        Args:
            message: Message to render
        """
        with self._lock:
            handlers = list(self._handlers)  # Copy to avoid lock during emit

        for handler in handlers:
            try:
                handler.handle(message)
            except Exception as e:
                # Log error but don't stop other handlers
                # In a production system, this would use a proper logger
                import sys

                print(
                    f"Error in handler {handler.__class__.__name__}: {e}",
                    file=sys.stderr,
                )
