"""Error types for Claude SDK."""

from typing import Any


class ClaudeSDKError(Exception):
    """Base exception for all Claude SDK errors."""


class CLIConnectionError(ClaudeSDKError):
    """Raised when unable to connect to Claude Code."""


class ClaudeCodeNotFoundError(CLIConnectionError):
    """Raised when Claude Code CLI is not found or not installed.

    Provides comprehensive installation instructions across multiple platforms
    and installation methods.
    """

    def __init__(self, message: str | None = None, cli_path: str | None = None):
        import platform as platform_module

        # Build comprehensive error message if not provided
        if message is None:
            message = "Claude Code CLI not found"

            # Add installation instructions
            message += "\n\nInstallation options:"
            message += "\n  1. npm (recommended - works on all platforms):"
            message += "\n     npm install -g @anthropic-ai/claude-code"

            # Add macOS-specific Homebrew option
            if platform_module.system() == "Darwin":
                message += "\n\n  2. Homebrew (macOS only):"
                message += "\n     brew install claude-code"

            # Add pip with auto-oauth extra option
            message += (
                "\n\n  "
                + ("3" if platform_module.system() == "Darwin" else "2")
                + ". pip with auto-oauth extra:"
            )
            message += "\n     pip install 'claude-agent-sdk[auto-oauth]'"

            # Add documentation link
            message += "\n\nFor more information, visit:"
            message += "\n  https://docs.anthropic.com/en/docs/claude-code/installation"

            # Add developer option
            message += "\n\nFor custom installations, use ClaudeAgentOptions:"
            message += "\n  ClaudeAgentOptions(cli_path='/path/to/claude')"

        # Append cli_path if provided
        if cli_path:
            message = f"{message}\n\nSearched path: {cli_path}"

        super().__init__(message)


# Backwards compatibility alias
CLINotFoundError = ClaudeCodeNotFoundError


class ProcessError(ClaudeSDKError):
    """Raised when the CLI process fails."""

    def __init__(
        self, message: str, exit_code: int | None = None, stderr: str | None = None
    ):
        self.exit_code = exit_code
        self.stderr = stderr

        if exit_code is not None:
            message = f"{message} (exit code: {exit_code})"
        if stderr:
            message = f"{message}\nError output: {stderr}"

        super().__init__(message)


class CLIJSONDecodeError(ClaudeSDKError):
    """Raised when unable to decode JSON from CLI output."""

    def __init__(self, line: str, original_error: Exception):
        self.line = line
        self.original_error = original_error
        super().__init__(f"Failed to decode JSON: {line[:100]}...")


class MessageParseError(ClaudeSDKError):
    """Raised when unable to parse a message from CLI output."""

    def __init__(self, message: str, data: dict[str, Any] | None = None):
        self.data = data
        super().__init__(message)
