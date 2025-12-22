"""CLI detection utilities for finding Claude Code executable."""

import os
import platform
import shutil
from pathlib import Path


def find_claude_cli() -> str:
    """Find Claude Code CLI binary.

    Searches for the Claude CLI executable in the following order:
    1. System PATH via shutil.which('claude')
    2. Common installation directories (platform-specific)
    3. Platform-specific package manager locations

    Returns:
        str: Absolute path to the Claude CLI executable.

    Raises:
        CLINotFoundError: If Claude CLI cannot be found in any location.

    Example:
        >>> cli_path = find_claude_cli()
        >>> print(cli_path)
        '/usr/local/bin/claude'
    """
    # First, try to find in PATH
    if cli := shutil.which("claude"):
        return cli

    # Build platform-specific fallback locations
    system = platform.system()
    home = Path.home()

    # Base locations that work on all platforms
    locations = [
        home / ".npm-global/bin/claude",
        home / ".local/bin/claude",
        home / "node_modules/.bin/claude",
        home / ".yarn/bin/claude",
        home / ".claude/local/claude",
    ]

    # Add platform-specific locations
    if system == "Darwin":  # macOS
        locations.extend([
            Path("/usr/local/bin/claude"),  # Homebrew Intel
            Path("/opt/homebrew/bin/claude"),  # Homebrew ARM
        ])
    elif system == "Linux":
        locations.extend([
            Path("/usr/local/bin/claude"),
            Path("/usr/bin/claude"),
        ])
    elif system == "Windows":
        # On Windows, check for .exe and .cmd extensions
        appdata = Path(os.environ.get("LOCALAPPDATA", home / "AppData/Local"))
        roaming = Path(os.environ.get("APPDATA", home / "AppData/Roaming"))

        locations.extend([
            appdata / "npm/claude.cmd",
            roaming / "npm/claude.cmd",
            home / ".claude/bin/claude.exe",
            home / ".claude/bin/claude.cmd",
        ])

    # Check each location
    for path in locations:
        if path.exists() and path.is_file():
            return str(path.absolute())

    # If we get here, Claude CLI was not found
    # Use ClaudeCodeNotFoundError with default comprehensive message
    from .._errors import ClaudeCodeNotFoundError
    raise ClaudeCodeNotFoundError()
