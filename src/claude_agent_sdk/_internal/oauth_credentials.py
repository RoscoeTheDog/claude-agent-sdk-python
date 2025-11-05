"""OAuth credentials management for Claude Code authentication."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class OAuthCredentials:
    """OAuth credentials from ~/.claude/.credentials.json."""

    access_token: str
    refresh_token: str
    expires_at: int  # Unix timestamp in milliseconds
    scopes: list[str]
    subscription: str  # e.g., "max"

    @property
    def is_expired(self) -> bool:
        """Check if access token is expired (with 5-minute buffer)."""
        if self.expires_at is None:
            return True

        current_time_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        # Add 5-minute buffer (300,000 ms) to prevent edge cases
        buffer_ms = 5 * 60 * 1000
        return current_time_ms >= (self.expires_at - buffer_ms)

    @property
    def is_valid(self) -> bool:
        """Check if credentials are valid (tokens present and not expired)."""
        return (
            bool(self.access_token)
            and bool(self.refresh_token)
            and not self.is_expired
        )


class CredentialsError(Exception):
    """Base exception for credentials-related errors."""
    pass


class CredentialsNotFoundError(CredentialsError):
    """Credentials file not found."""
    pass


class CredentialsInvalidError(CredentialsError):
    """Credentials file is invalid or corrupted."""
    pass


class TokenFormatError(CredentialsError):
    """Token format is invalid."""
    pass


def get_credentials_path() -> Path:
    """
    Get the path to the Claude credentials file.

    Returns:
        Path to ~/.claude/.credentials.json (cross-platform)
    """
    home = Path.home()
    return home / ".claude" / ".credentials.json"


def validate_token_format(token: str, token_type: str) -> None:
    """
    Validate OAuth token format.

    Args:
        token: Token string to validate
        token_type: Either "access" or "refresh"

    Raises:
        TokenFormatError: If token format is invalid
    """
    if not token:
        raise TokenFormatError(f"{token_type} token is empty")

    if token_type == "access":
        expected_prefix = "sk-ant-oat01-"
    elif token_type == "refresh":
        expected_prefix = "sk-ant-ort01-"
    else:
        raise ValueError(f"Invalid token_type: {token_type}")

    if not token.startswith(expected_prefix):
        raise TokenFormatError(
            f"{token_type} token must start with '{expected_prefix}', "
            f"got: '{token[:15]}...'"
        )

    # Basic validation: should be alphanumeric + hyphens after prefix
    if not re.match(r'^sk-ant-o[ar]t01-[\w-]+$', token):
        raise TokenFormatError(
            f"{token_type} token has invalid format: '{token[:15]}...'"
        )


def read_credentials() -> Optional[OAuthCredentials]:
    """
    Read OAuth credentials from ~/.claude/.credentials.json.

    Returns:
        OAuthCredentials if file exists and is valid, None otherwise

    Raises:
        CredentialsNotFoundError: If credentials file doesn't exist
        CredentialsInvalidError: If credentials file is malformed
        TokenFormatError: If token formats are invalid
    """
    creds_path = get_credentials_path()

    if not creds_path.exists():
        raise CredentialsNotFoundError(
            f"Credentials file not found at: {creds_path}\n"
            "Run 'claude setup-token' to authenticate with your Claude subscription."
        )

    try:
        with open(creds_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise CredentialsInvalidError(
            f"Credentials file is not valid JSON: {e}"
        ) from e
    except Exception as e:
        raise CredentialsInvalidError(
            f"Failed to read credentials file: {e}"
        ) from e

    # Extract claudeAiOauth object
    oauth_data = data.get("claudeAiOauth")
    if not oauth_data:
        raise CredentialsInvalidError(
            "Credentials file missing 'claudeAiOauth' field"
        )

    # Extract required fields
    try:
        access_token = oauth_data["accessToken"]
        refresh_token = oauth_data["refreshToken"]
        expires_at = oauth_data["expiresAt"]
        scopes = oauth_data.get("scopes", [])
        subscription = oauth_data.get("subscription", "unknown")
    except KeyError as e:
        raise CredentialsInvalidError(
            f"Credentials file missing required field: {e}"
        ) from e

    # Validate token formats
    validate_token_format(access_token, "access")
    validate_token_format(refresh_token, "refresh")

    # Validate expires_at is a reasonable timestamp
    if not isinstance(expires_at, (int, float)) or expires_at < 0:
        raise CredentialsInvalidError(
            f"Invalid expiresAt value: {expires_at}"
        )

    return OAuthCredentials(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=int(expires_at),
        scopes=scopes if isinstance(scopes, list) else [],
        subscription=subscription
    )


def credentials_exist() -> bool:
    """
    Check if credentials file exists.

    Returns:
        True if ~/.claude/.credentials.json exists
    """
    return get_credentials_path().exists()


def get_valid_credentials() -> Optional[OAuthCredentials]:
    """
    Get valid OAuth credentials if available.

    Returns:
        OAuthCredentials if valid credentials exist, None otherwise

    Note:
        This function does not raise exceptions. It returns None if:
        - Credentials file doesn't exist
        - Credentials are invalid/corrupted
        - Tokens are expired
    """
    try:
        creds = read_credentials()
        if creds and creds.is_valid:
            return creds
        return None
    except (CredentialsError, Exception):
        # Gracefully handle any errors
        return None
