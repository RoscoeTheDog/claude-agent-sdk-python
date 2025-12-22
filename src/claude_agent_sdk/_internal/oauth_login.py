"""OAuth login flow via Claude CLI delegation.

This module handles OAuth authentication by delegating to the official Claude CLI.
Instead of implementing the OAuth protocol ourselves, we simply invoke `claude /login`
and let the CLI handle browser authentication, token exchange, and credential storage.

This approach is:
- Simpler: ~150 lines vs ~500 lines for full OAuth implementation
- More reliable: Uses official, tested implementation
- More maintainable: Anthropic updates OAuth, we automatically benefit
- Proven: Same strategy used by TypeScript and Go SDKs
"""

import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .oauth_credentials import OAuthCredentials, read_credentials


def trigger_oauth_login(interactive: bool = True) -> bool:
    """Trigger OAuth login via Claude CLI.

    Executes `claude /login` command to initiate browser-based OAuth authentication.
    The Claude CLI handles all OAuth protocol details including:
    - Opening browser with authorization URL
    - Starting local callback server
    - Exchanging authorization code for tokens
    - Saving credentials to ~/.claude/.credentials.json

    Args:
        interactive: If True, allows interactive browser login.
                    If False, raises error instead.

    Returns:
        True if login succeeded and valid credentials were created.
        False if login failed.

    Raises:
        RuntimeError: If non-interactive mode and no valid credentials exist.
        FileNotFoundError: If Claude CLI is not installed.

    Example:
        >>> if trigger_oauth_login():
        ...     print("Login successful!")
        ... else:
        ...     print("Login failed")
    """
    if not interactive:
        raise RuntimeError(
            "OAuth login required but running in non-interactive mode. "
            "Please run 'claude /login' manually or set ANTHROPIC_API_KEY environment variable."
        )

    print("\n" + "=" * 60)
    print("  OAuth Login Required")
    print("=" * 60)
    print("\nYou need to authenticate with your Claude Max subscription.")
    print("This will open your browser for login...\n")
    print("If the browser doesn't open automatically, you can run:")
    print("  claude /login")
    print("")

    try:
        # Run claude /login command
        # Don't capture output so user sees prompts and browser launch messages
        subprocess.run(
            ["claude", "/login"],
            check=True,
            text=True,
            # Let Claude CLI handle all interaction with user
        )

        # Verify credentials were created successfully
        creds = read_credentials()
        if creds and not creds.is_expired:
            print("\n" + "=" * 60)
            print("  Login Successful!")
            print("=" * 60)
            print(f"  Subscription: {creds.subscription.upper()}")
            # Convert milliseconds timestamp to datetime
            expires_dt = datetime.fromtimestamp(
                creds.expires_at / 1000, tz=timezone.utc
            )
            print(f"  Token expires: {expires_dt.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print("=" * 60 + "\n")
            return True
        else:
            print("\n" + "=" * 60)
            print("  Login Failed")
            print("=" * 60)
            print("  Credentials not found or expired after login")
            print("=" * 60 + "\n")
            return False

    except FileNotFoundError:
        print("\n" + "=" * 60)
        print("  Error: Claude CLI Not Found")
        print("=" * 60)
        print("  Please install Claude Code:")
        print("    npm install -g @anthropic-ai/claude-code")
        print("")
        print("  Or visit: https://docs.claude.com/en/docs/claude-code")
        print("=" * 60 + "\n")
        return False

    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print("  Login Failed")
        print("=" * 60)
        print(f"  Error: {e}")
        print("=" * 60 + "\n")
        return False

    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("  Login Cancelled")
        print("=" * 60)
        print("  Login was cancelled by user")
        print("=" * 60 + "\n")
        return False


def ensure_valid_credentials(interactive: bool = True) -> OAuthCredentials:
    """Ensure valid OAuth credentials exist, triggering login if needed.

    This is the main entry point for authentication. It checks if valid credentials
    exist and triggers login if necessary.

    Workflow:
    1. Check for existing credentials in ~/.claude/.credentials.json
    2. If valid, return them immediately
    3. If missing/expired and interactive=True, trigger `claude /login`
    4. If missing/expired and interactive=False, raise error

    Args:
        interactive: If True, allows interactive browser login when needed.
                    If False, raises error if credentials are invalid.

    Returns:
        Valid OAuthCredentials object

    Raises:
        RuntimeError: If credentials are invalid and cannot be obtained:
            - Non-interactive mode and no valid credentials
            - Login failed
            - Credentials still invalid after successful login

    Example:
        >>> # Interactive mode (default)
        >>> creds = ensure_valid_credentials()
        >>> print(f"Access token: {creds.access_token[:20]}...")

        >>> # Non-interactive mode (CI/CD)
        >>> try:
        ...     creds = ensure_valid_credentials(interactive=False)
        ... except RuntimeError:
        ...     print("No valid credentials in non-interactive mode")
    """
    creds = read_credentials()

    # Happy path: valid credentials already exist
    if creds and not creds.is_expired:
        return creds

    # Credentials missing or expired - need to login
    if creds and creds.is_expired:
        print("⚠ OAuth credentials expired")
        expires_dt = datetime.fromtimestamp(creds.expires_at / 1000, tz=timezone.utc)
        print(f"   Expired at: {expires_dt.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    else:
        print("⚠ No OAuth credentials found")
        print(f"   Expected location: {Path.home() / '.claude' / '.credentials.json'}")

    # Attempt login
    if not trigger_oauth_login(interactive=interactive):
        raise RuntimeError(
            "Failed to obtain valid OAuth credentials. "
            "Please run 'claude /login' manually or set ANTHROPIC_API_KEY."
        )

    # Re-read credentials after login
    creds = read_credentials()
    if not creds or creds.is_expired:
        # This should be rare - login succeeded but credentials invalid
        raise RuntimeError(
            "Login appeared to succeed but credentials are still invalid. "
            "This may indicate a problem with the Claude CLI installation. "
            "Try running 'claude /login' manually."
        )

    return creds


def check_claude_cli_installed() -> bool:
    """Check if Claude CLI is installed and available.

    Returns:
        True if Claude CLI is installed and can be executed.
        False otherwise.

    Example:
        >>> if check_claude_cli_installed():
        ...     print("Claude CLI is installed")
        ... else:
        ...     print("Please install Claude CLI")
    """
    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,  # Don't raise on non-zero exit
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_claude_cli_version() -> str | None:
    """Get the installed Claude CLI version.

    Returns:
        Version string (e.g., "1.0.123") if Claude CLI is installed.
        None if Claude CLI is not installed or version cannot be determined.

    Example:
        >>> version = get_claude_cli_version()
        >>> if version:
        ...     print(f"Claude CLI version: {version}")
    """
    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
        # Output format: "claude-code version 1.0.123"
        output = result.stdout.strip()
        if "version" in output:
            parts = output.split()
            if len(parts) >= 2:
                return parts[-1]  # Last part is version number
        return output  # Return full output if format unexpected
    except (
        FileNotFoundError,
        subprocess.TimeoutExpired,
        subprocess.CalledProcessError,
    ):
        return None
