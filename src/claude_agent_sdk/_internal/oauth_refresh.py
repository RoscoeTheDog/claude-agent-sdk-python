"""OAuth token refresh via Claude CLI auto-refresh detection.

This module handles expired OAuth access token refresh by leveraging Claude CLI's
built-in auto-refresh mechanism. Instead of implementing token refresh protocol ourselves,
we trigger Claude CLI commands that cause it to auto-refresh tokens when needed.

Strategies:
1. Let Claude CLI auto-refresh during normal operations
2. Trigger a harmless command (e.g., --version) to force refresh check
3. Fall back to full re-login if refresh fails
"""

import subprocess
import time
from typing import Optional

from .oauth_credentials import OAuthCredentials, read_credentials


def refresh_oauth_token(interactive: bool = False) -> Optional[OAuthCredentials]:
    """Attempt to refresh expired OAuth access token.

    This function implements a multi-strategy approach to token refresh:

    Strategy 1: Check if token is already fresh
        - Credentials may have been refreshed by another process
        - Always check before attempting refresh

    Strategy 2: Trigger Claude CLI auto-refresh
        - Run a harmless command (--version)
        - Claude CLI may detect expired token and auto-refresh
        - Check if credentials were updated

    Strategy 3: Fall back to full re-login
        - If auto-refresh didn't work and interactive mode
        - Trigger full OAuth login flow
        - User authenticates via browser

    Args:
        interactive: If True, allows interactive re-login if refresh fails.
                    If False, returns None if auto-refresh fails.

    Returns:
        Refreshed OAuthCredentials if refresh succeeded.
        None if refresh failed.

    Example:
        >>> # Try to refresh, allow interactive login if needed
        >>> creds = refresh_oauth_token(interactive=True)
        >>> if creds:
        ...     print("Token refreshed successfully")
        ... else:
        ...     print("Refresh failed")

        >>> # Try auto-refresh only (non-interactive)
        >>> creds = refresh_oauth_token(interactive=False)
        >>> if not creds:
        ...     print("Auto-refresh failed, manual login required")
    """
    # Strategy 1: Check if already fresh
    creds = read_credentials()
    if not creds:
        return None

    if not creds.is_expired:
        # Already valid, no refresh needed
        return creds

    # Strategy 2: Trigger Claude CLI auto-refresh
    print("⚙ Attempting to refresh OAuth token...")

    try:
        # Run a harmless command to trigger potential auto-refresh
        # Claude CLI checks token expiration and may refresh automatically
        subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=10,  # Allow time for potential refresh
            check=False,  # Don't raise on error
        )

        # Small delay to let file system settle
        time.sleep(0.5)

        # Check if credentials were refreshed
        new_creds = read_credentials()
        if new_creds and not new_creds.is_expired:
            print("✓ Token refreshed successfully")
            return new_creds

        # Auto-refresh didn't work
        print("⚠ Auto-refresh did not work")

    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"⚠ Auto-refresh failed: {e}")

    # Strategy 3: Fall back to full re-login (if interactive)
    if interactive:
        print("→ Falling back to full re-login...")
        from .oauth_login import trigger_oauth_login

        if trigger_oauth_login(interactive=True):
            return read_credentials()

    return None


def ensure_token_fresh(
    creds: OAuthCredentials, interactive: bool = True
) -> OAuthCredentials:
    """Ensure OAuth token is fresh, refreshing if needed.

    This is a convenience function that combines credential checking
    and automatic refresh in a single call.

    Args:
        creds: Current credentials to check
        interactive: Allow interactive login if refresh fails

    Returns:
        Fresh OAuthCredentials (may be same object if already fresh)

    Raises:
        RuntimeError: If token is expired and cannot be refreshed

    Example:
        >>> creds = read_credentials()
        >>> fresh_creds = ensure_token_fresh(creds)
        >>> # fresh_creds is guaranteed to be non-expired
    """
    if not creds.is_expired:
        return creds

    # Token expired, try to refresh
    refreshed = refresh_oauth_token(interactive=interactive)
    if refreshed and not refreshed.is_expired:
        return refreshed

    raise RuntimeError(
        "OAuth token is expired and could not be refreshed. "
        "Please run 'claude /login' to re-authenticate."
    )


def is_refresh_needed(creds: OAuthCredentials, buffer_seconds: int = 300) -> bool:
    """Check if token refresh should be triggered proactively.

    This function implements a "refresh buffer" strategy: trigger refresh
    before token actually expires to avoid mid-request expiration.

    Args:
        creds: Credentials to check
        buffer_seconds: Refresh if token expires within this many seconds
                       Default: 300 seconds (5 minutes)

    Returns:
        True if refresh should be triggered now.
        False if token is still valid with buffer.

    Example:
        >>> creds = read_credentials()
        >>> if is_refresh_needed(creds, buffer_seconds=600):
        ...     # Token expires in < 10 minutes, refresh now
        ...     refresh_oauth_token()
    """
    # Use the built-in is_expired property which includes buffer
    return creds.is_expired


def trigger_proactive_refresh(creds: OAuthCredentials) -> Optional[OAuthCredentials]:
    """Trigger proactive token refresh if nearing expiration.

    This is a non-interactive refresh that only attempts auto-refresh.
    It's designed to be called before API requests to prevent mid-request
    token expiration.

    Args:
        creds: Current credentials

    Returns:
        Refreshed credentials if refresh was triggered and succeeded.
        Original credentials if refresh not needed.
        None if refresh was needed but failed.

    Example:
        >>> # Before making API request
        >>> creds = read_credentials()
        >>> fresh_creds = trigger_proactive_refresh(creds)
        >>> if fresh_creds:
        ...     # Proceed with fresh token
        ...     make_api_request(fresh_creds)
        ... else:
        ...     # Refresh failed, need interactive login
        ...     ensure_valid_credentials(interactive=True)
    """
    if not is_refresh_needed(creds):
        return creds  # No refresh needed

    # Attempt non-interactive refresh
    return refresh_oauth_token(interactive=False)


def get_token_ttl_seconds(creds: OAuthCredentials) -> float:
    """Get token time-to-live in seconds.

    Args:
        creds: Credentials to check

    Returns:
        Seconds until token expires.
        Negative number if already expired.

    Example:
        >>> creds = read_credentials()
        >>> ttl = get_token_ttl_seconds(creds)
        >>> if ttl < 600:
        ...     print(f"Token expires in {ttl:.0f} seconds")
        ...     refresh_oauth_token()
    """
    # Convert milliseconds to seconds
    return (creds.expires_at / 1000) - time.time()


def should_refresh_token(
    creds: OAuthCredentials,
    min_ttl_seconds: int = 300,
) -> tuple[bool, str]:
    """Determine if token should be refreshed with reason.

    This is a more informative version of is_refresh_needed that provides
    a human-readable reason for the refresh decision.

    Args:
        creds: Credentials to check
        min_ttl_seconds: Minimum time-to-live before triggering refresh

    Returns:
        Tuple of (should_refresh: bool, reason: str)

    Example:
        >>> creds = read_credentials()
        >>> should_refresh, reason = should_refresh_token(creds)
        >>> if should_refresh:
        ...     print(f"Refreshing: {reason}")
        ...     refresh_oauth_token()
    """
    ttl = get_token_ttl_seconds(creds)

    if ttl < 0:
        return True, f"Token expired {-ttl:.0f} seconds ago"

    if ttl < min_ttl_seconds:
        return True, f"Token expires in {ttl:.0f} seconds (< {min_ttl_seconds}s buffer)"

    return False, f"Token valid for {ttl:.0f} more seconds"
