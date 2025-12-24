"""CLI detection utilities for finding Claude Code executable."""

import os
import platform
import shutil
import subprocess
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
        locations.extend(
            [
                Path("/usr/local/bin/claude"),  # Homebrew Intel
                Path("/opt/homebrew/bin/claude"),  # Homebrew ARM
            ]
        )
    elif system == "Linux":
        locations.extend(
            [
                Path("/usr/local/bin/claude"),
                Path("/usr/bin/claude"),
            ]
        )
    elif system == "Windows":
        # On Windows, check for .exe and .cmd extensions
        appdata = Path(os.environ.get("LOCALAPPDATA", home / "AppData/Local"))
        roaming = Path(os.environ.get("APPDATA", home / "AppData/Roaming"))

        locations.extend(
            [
                appdata / "npm/claude.cmd",
                roaming / "npm/claude.cmd",
                home / ".claude/bin/claude.exe",
                home / ".claude/bin/claude.cmd",
            ]
        )

    # Check each location
    for path in locations:
        if path.exists() and path.is_file():
            return str(path.absolute())

    # If we get here, Claude CLI was not found
    # Use ClaudeCodeNotFoundError with default comprehensive message
    from .._errors import ClaudeCodeNotFoundError

    raise ClaudeCodeNotFoundError()


def get_claude_cli_or_install() -> str:
    """Find Claude CLI, attempting auto-install if not found.

    First attempts standard detection via find_claude_cli().
    If detection fails AND nodejs-bin is installed, attempts to
    auto-install @anthropic-ai/claude-code to ~/.claude-sdk/.

    Returns:
        str: Path to Claude CLI executable

    Raises:
        ClaudeCodeNotFoundError: If CLI not found and auto-install fails

    Example:
        >>> cli_path = get_claude_cli_or_install()
        >>> # May trigger npm install on first run
    """
    from .._errors import ClaudeCodeNotFoundError

    try:
        return find_claude_cli()
    except ClaudeCodeNotFoundError:
        # Attempt auto-install if nodejs-bin available
        return _attempt_auto_install()


def _attempt_auto_install() -> str:
    """Attempt to auto-install Claude Code using nodejs-bin.

    Raises:
        ClaudeCodeNotFoundError: If nodejs-bin not available or install fails
    """
    from .._errors import ClaudeCodeNotFoundError

    try:
        from nodejs import npm  # type: ignore[import-not-found]
    except ImportError:
        # nodejs-bin not installed - fall back to original error
        raise ClaudeCodeNotFoundError(
            message=(
                "Claude Code CLI not found. "
                "Install with 'pip install claude-agent-sdk[auto-oauth]' "
                "for automatic installation."
            )
        ) from None

    # Determine install directory (cross-platform)
    home = Path.home()
    install_dir = home / ".claude-sdk"
    install_dir.mkdir(parents=True, exist_ok=True)

    # Run npm install
    try:
        npm.run(
            [
                "install",
                "-g",
                "@anthropic-ai/claude-code",
                "--prefix",
                str(install_dir),
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=300,  # 5 minute timeout
        )

        # After install, search for the CLI in the new location
        system = platform.system()
        if system == "Windows":
            cli_candidates = [
                install_dir / "bin" / "claude.cmd",
                install_dir / "bin" / "claude.exe",
            ]
        else:
            cli_candidates = [
                install_dir / "bin" / "claude",
            ]

        for cli_path in cli_candidates:
            if cli_path.exists() and cli_path.is_file():
                return str(cli_path.absolute())

        # Install succeeded but CLI not found where expected
        raise ClaudeCodeNotFoundError(
            message=(
                f"Auto-install completed but CLI not found at {install_dir}/bin/. "
                "Try manual installation: npm install -g @anthropic-ai/claude-code"
            )
        )

    except subprocess.TimeoutExpired:
        raise ClaudeCodeNotFoundError(
            message="Auto-install timed out. Try manual installation."
        ) from None
    except subprocess.CalledProcessError as e:
        raise ClaudeCodeNotFoundError(
            message=(
                f"Auto-install failed (exit code {e.returncode}). "
                f"Error: {e.stderr}\n"
                "Try manual installation: npm install -g @anthropic-ai/claude-code"
            )
        ) from None
    except Exception as e:
        raise ClaudeCodeNotFoundError(message=f"Auto-install failed: {e}") from None
