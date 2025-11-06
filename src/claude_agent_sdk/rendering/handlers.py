"""Concrete handler implementations for message output.

This module provides standard handlers for common output destinations:
- StreamHandler: Write to stdout/stderr or any text stream
- FileHandler: Write to files with UTF-8 encoding
- NullHandler: No-op handler for testing/silencing
"""

import contextlib
import sys
from io import TextIOWrapper
from pathlib import Path
from typing import TYPE_CHECKING, TextIO, cast

from ..types import Message
from .base import Handler
from .config import RendererConfig

if TYPE_CHECKING:
    from .base import Formatter


class StreamHandler(Handler):
    """Handler that writes formatted messages to a text stream (e.g., stdout).

    By default, writes to stdout with UTF-8 encoding. Can be configured to write
    to stderr or any other text stream. Follows Claude Code CLI convention of
    double newlines between messages.

    Example:
        # Console output (default)
        handler = StreamHandler(formatter)

        # Write to stderr
        handler = StreamHandler(formatter, stream=sys.stderr)

        # Auto-flush after each message
        handler = StreamHandler(formatter, auto_flush=True)
    """

    def __init__(
        self,
        formatter: "Formatter",
        config: RendererConfig | None = None,
        stream: TextIO | None = None,
        auto_flush: bool = False,
    ) -> None:
        """Initialize stream handler.

        Args:
            formatter: Formatter instance to use for formatting messages
            config: Rendering configuration. If None, uses formatter's config.
            stream: Text stream to write to. Defaults to sys.stdout.
            auto_flush: If True, flush stream after each message (default: False)
        """
        super().__init__(formatter, config)
        self.stream = stream or sys.stdout
        self.auto_flush = auto_flush

        # Ensure UTF-8 encoding for proper rendering of Unicode characters
        # Only reconfigure if it's a TextIOWrapper (not all streams support this)
        if isinstance(self.stream, TextIOWrapper):
            # If reconfigure fails (e.g., on some streams), just continue
            # The stream may already be configured correctly
            with contextlib.suppress(Exception):
                self.stream.reconfigure(encoding="utf-8")

    def emit(self, formatted_output: str, message: Message) -> None:
        """Write formatted output to the stream.

        Adds double newline after each message following Claude Code CLI convention.

        Args:
            formatted_output: Pre-formatted string to output
            message: Original message (for metadata, unused here)
        """
        # Write message with double newline separator (Claude Code CLI convention)
        self.stream.write(formatted_output)
        self.stream.write("\n\n")

        if self.auto_flush:
            self.stream.flush()


class FileHandler(Handler):
    """Handler that writes formatted messages to a file.

    Creates parent directories if they don't exist. Uses UTF-8 encoding by default.
    Supports both append and overwrite modes.

    Example:
        # Append to file (default)
        handler = FileHandler(formatter, "output.txt")

        # Overwrite file
        handler = FileHandler(formatter, "output.txt", mode="w")

        # Using Path object
        handler = FileHandler(formatter, Path("logs/session.log"))
    """

    def __init__(
        self,
        formatter: "Formatter",
        filepath: str | Path,
        config: RendererConfig | None = None,
        mode: str = "a",
        encoding: str = "utf-8",
    ) -> None:
        """Initialize file handler.

        Args:
            formatter: Formatter instance to use for formatting messages
            filepath: Path to output file (str or Path object)
            config: Rendering configuration. If None, uses formatter's config.
            mode: File open mode - 'a' for append (default), 'w' for overwrite
            encoding: File encoding (default: 'utf-8')
        """
        super().__init__(formatter, config)
        self.filepath = Path(filepath)
        self.mode = mode
        self.encoding = encoding
        self._file_handle: TextIO | None = None

        # Create parent directories if they don't exist
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

        # Open file handle using Path.open()
        self._file_handle = cast(TextIO, self.filepath.open(mode=self.mode, encoding=self.encoding))

    def emit(self, formatted_output: str, message: Message) -> None:
        """Write formatted output to the file.

        Adds double newline after each message following Claude Code CLI convention.

        Args:
            formatted_output: Pre-formatted string to output
            message: Original message (for metadata, unused here)
        """
        if self._file_handle is None or self._file_handle.closed:
            # Reopen file if it was closed
            self._file_handle = cast(TextIO, self.filepath.open(mode=self.mode, encoding=self.encoding))
            self._file_handle = cast(TextIO, self.filepath.open(mode=self.mode, encoding=self.encoding))
            self._file_handle = cast(TextIO, self.filepath.open(mode=self.mode, encoding=self.encoding))

        # Write message with double newline separator
        # At this point, _file_handle is guaranteed to be open
        assert self._file_handle is not None
        self._file_handle.write(formatted_output)
        self._file_handle.write("\n\n")
        self._file_handle.flush()  # Ensure data is written immediately

    def close(self) -> None:
        """Close the file handle explicitly.

        This is optional - the file will also be closed when the handler
        is garbage collected via __del__.
        """
        if self._file_handle is not None and not self._file_handle.closed:
            self._file_handle.close()

    def __del__(self) -> None:
        """Clean up file handle when handler is garbage collected."""
        self.close()


class NullHandler(Handler):
    """Handler that discards all output (no-op).

    Useful for testing or temporarily silencing output without removing handlers.

    Example:
        # Silence all output
        handler = NullHandler(formatter)
        renderer.add_handler(handler)
    """

    def emit(self, formatted_output: str, message: Message) -> None:
        """Do nothing (discard output).

        Args:
            formatted_output: Pre-formatted string (ignored)
            message: Original message (ignored)
        """
        # No-op: discard all output
        pass
