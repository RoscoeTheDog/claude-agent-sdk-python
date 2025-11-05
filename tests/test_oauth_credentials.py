"""Tests for OAuth credentials management."""

from __future__ import annotations

import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from claude_agent_sdk._internal.oauth_credentials import (
    CredentialsError,
    CredentialsInvalidError,
    CredentialsNotFoundError,
    OAuthCredentials,
    TokenFormatError,
    credentials_exist,
    get_credentials_path,
    get_valid_credentials,
    read_credentials,
    validate_token_format,
)


class TestOAuthCredentials:
    """Test OAuthCredentials dataclass."""

    def test_is_expired_when_past_expiration(self):
        """Test is_expired returns True when token is expired."""
        # Expired 1 hour ago
        past_time_ms = int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp() * 1000)
        creds = OAuthCredentials(
            access_token="sk-ant-oat01-test",
            refresh_token="sk-ant-ort01-test",
            expires_at=past_time_ms,
            scopes=["user:inference"],
            subscription="max"
        )
        assert creds.is_expired is True

    def test_is_expired_when_within_buffer(self):
        """Test is_expired returns True when within 5-minute buffer."""
        # Expires in 2 minutes (within 5-minute buffer)
        near_future_ms = int((datetime.now(timezone.utc) + timedelta(minutes=2)).timestamp() * 1000)
        creds = OAuthCredentials(
            access_token="sk-ant-oat01-test",
            refresh_token="sk-ant-ort01-test",
            expires_at=near_future_ms,
            scopes=["user:inference"],
            subscription="max"
        )
        assert creds.is_expired is True

    def test_is_expired_when_future(self):
        """Test is_expired returns False when token expires in future."""
        # Expires in 1 hour (outside buffer)
        future_time_ms = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp() * 1000)
        creds = OAuthCredentials(
            access_token="sk-ant-oat01-test",
            refresh_token="sk-ant-ort01-test",
            expires_at=future_time_ms,
            scopes=["user:inference"],
            subscription="max"
        )
        assert creds.is_expired is False

    def test_is_valid_when_all_good(self):
        """Test is_valid returns True when tokens present and not expired."""
        future_time_ms = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp() * 1000)
        creds = OAuthCredentials(
            access_token="sk-ant-oat01-test",
            refresh_token="sk-ant-ort01-test",
            expires_at=future_time_ms,
            scopes=["user:inference"],
            subscription="max"
        )
        assert creds.is_valid is True

    def test_is_valid_when_expired(self):
        """Test is_valid returns False when expired."""
        past_time_ms = int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp() * 1000)
        creds = OAuthCredentials(
            access_token="sk-ant-oat01-test",
            refresh_token="sk-ant-ort01-test",
            expires_at=past_time_ms,
            scopes=["user:inference"],
            subscription="max"
        )
        assert creds.is_valid is False

    def test_is_valid_when_missing_access_token(self):
        """Test is_valid returns False when access token missing."""
        future_time_ms = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp() * 1000)
        creds = OAuthCredentials(
            access_token="",
            refresh_token="sk-ant-ort01-test",
            expires_at=future_time_ms,
            scopes=["user:inference"],
            subscription="max"
        )
        assert creds.is_valid is False


class TestValidateTokenFormat:
    """Test token format validation."""

    def test_valid_access_token(self):
        """Test validation passes for valid access token."""
        validate_token_format("sk-ant-oat01-abcdef123456", "access")

    def test_valid_refresh_token(self):
        """Test validation passes for valid refresh token."""
        validate_token_format("sk-ant-ort01-abcdef123456", "refresh")

    def test_empty_token(self):
        """Test validation fails for empty token."""
        with pytest.raises(TokenFormatError, match="access token is empty"):
            validate_token_format("", "access")

    def test_wrong_prefix_access(self):
        """Test validation fails for wrong access token prefix."""
        with pytest.raises(TokenFormatError, match="must start with 'sk-ant-oat01-'"):
            validate_token_format("sk-ant-api01-wrong", "access")

    def test_wrong_prefix_refresh(self):
        """Test validation fails for wrong refresh token prefix."""
        with pytest.raises(TokenFormatError, match="must start with 'sk-ant-ort01-'"):
            validate_token_format("sk-ant-oat01-wrong", "refresh")

    def test_invalid_characters(self):
        """Test validation fails for invalid characters."""
        with pytest.raises(TokenFormatError, match="invalid format"):
            validate_token_format("sk-ant-oat01-invalid chars!", "access")


class TestGetCredentialsPath:
    """Test credentials path resolution."""

    def test_credentials_path_structure(self):
        """Test credentials path has correct structure."""
        path = get_credentials_path()
        assert path.name == ".credentials.json"
        assert path.parent.name == ".claude"
        assert path.parent.parent == Path.home()


class TestReadCredentials:
    """Test reading credentials from file."""

    def create_temp_credentials_file(self, data: dict) -> Path:
        """Helper to create a temporary credentials file."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(data, temp_file)
        temp_file.close()
        return Path(temp_file.name)

    def test_read_valid_credentials(self):
        """Test reading valid credentials file."""
        future_time_ms = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp() * 1000)
        data = {
            "claudeAiOauth": {
                "accessToken": "sk-ant-oat01-test-access-token",
                "refreshToken": "sk-ant-ort01-test-refresh-token",
                "expiresAt": future_time_ms,
                "scopes": ["user:inference", "user:profile"],
                "subscription": "max"
            }
        }

        temp_path = self.create_temp_credentials_file(data)
        try:
            with patch('claude_agent_sdk._internal.oauth_credentials.get_credentials_path', return_value=temp_path):
                creds = read_credentials()

            assert creds.access_token == "sk-ant-oat01-test-access-token"
            assert creds.refresh_token == "sk-ant-ort01-test-refresh-token"
            assert creds.expires_at == future_time_ms
            assert creds.scopes == ["user:inference", "user:profile"]
            assert creds.subscription == "max"
            assert creds.is_valid is True
        finally:
            temp_path.unlink()

    def test_read_credentials_file_not_found(self):
        """Test reading credentials when file doesn't exist."""
        nonexistent_path = Path("/nonexistent/path/.credentials.json")
        with patch('claude_agent_sdk._internal.oauth_credentials.get_credentials_path', return_value=nonexistent_path):
            with pytest.raises(CredentialsNotFoundError, match="Credentials file not found"):
                read_credentials()

    def test_read_credentials_invalid_json(self):
        """Test reading credentials with invalid JSON."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_file.write("{ invalid json }")
        temp_file.close()
        temp_path = Path(temp_file.name)

        try:
            with patch('claude_agent_sdk._internal.oauth_credentials.get_credentials_path', return_value=temp_path):
                with pytest.raises(CredentialsInvalidError, match="not valid JSON"):
                    read_credentials()
        finally:
            temp_path.unlink()

    def test_read_credentials_missing_oauth_field(self):
        """Test reading credentials without claudeAiOauth field."""
        data = {"someOtherField": "value"}
        temp_path = self.create_temp_credentials_file(data)

        try:
            with patch('claude_agent_sdk._internal.oauth_credentials.get_credentials_path', return_value=temp_path):
                with pytest.raises(CredentialsInvalidError, match="missing 'claudeAiOauth' field"):
                    read_credentials()
        finally:
            temp_path.unlink()

    def test_read_credentials_missing_required_field(self):
        """Test reading credentials missing required field."""
        data = {
            "claudeAiOauth": {
                "accessToken": "sk-ant-oat01-test",
                # Missing refreshToken
                "expiresAt": 123456789
            }
        }
        temp_path = self.create_temp_credentials_file(data)

        try:
            with patch('claude_agent_sdk._internal.oauth_credentials.get_credentials_path', return_value=temp_path):
                with pytest.raises(CredentialsInvalidError, match="missing required field"):
                    read_credentials()
        finally:
            temp_path.unlink()

    def test_read_credentials_invalid_token_format(self):
        """Test reading credentials with invalid token format."""
        data = {
            "claudeAiOauth": {
                "accessToken": "invalid-token-format",
                "refreshToken": "sk-ant-ort01-test",
                "expiresAt": 123456789
            }
        }
        temp_path = self.create_temp_credentials_file(data)

        try:
            with patch('claude_agent_sdk._internal.oauth_credentials.get_credentials_path', return_value=temp_path):
                with pytest.raises(TokenFormatError, match="must start with 'sk-ant-oat01-'"):
                    read_credentials()
        finally:
            temp_path.unlink()


class TestCredentialsExist:
    """Test credentials existence check."""

    def test_credentials_exist_when_present(self):
        """Test credentials_exist returns True when file exists."""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        temp_path = Path(temp_file.name)

        try:
            with patch('claude_agent_sdk._internal.oauth_credentials.get_credentials_path', return_value=temp_path):
                assert credentials_exist() is True
        finally:
            temp_path.unlink()

    def test_credentials_exist_when_absent(self):
        """Test credentials_exist returns False when file doesn't exist."""
        nonexistent_path = Path("/nonexistent/path/.credentials.json")
        with patch('claude_agent_sdk._internal.oauth_credentials.get_credentials_path', return_value=nonexistent_path):
            assert credentials_exist() is False


class TestGetValidCredentials:
    """Test get_valid_credentials helper."""

    def test_get_valid_credentials_success(self):
        """Test get_valid_credentials returns credentials when valid."""
        future_time_ms = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp() * 1000)
        data = {
            "claudeAiOauth": {
                "accessToken": "sk-ant-oat01-test",
                "refreshToken": "sk-ant-ort01-test",
                "expiresAt": future_time_ms,
                "scopes": ["user:inference"],
                "subscription": "max"
            }
        }

        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(data, temp_file)
        temp_file.close()
        temp_path = Path(temp_file.name)

        try:
            with patch('claude_agent_sdk._internal.oauth_credentials.get_credentials_path', return_value=temp_path):
                creds = get_valid_credentials()
                assert creds is not None
                assert creds.is_valid is True
        finally:
            temp_path.unlink()

    def test_get_valid_credentials_when_expired(self):
        """Test get_valid_credentials returns None when expired."""
        past_time_ms = int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp() * 1000)
        data = {
            "claudeAiOauth": {
                "accessToken": "sk-ant-oat01-test",
                "refreshToken": "sk-ant-ort01-test",
                "expiresAt": past_time_ms,
                "scopes": ["user:inference"],
                "subscription": "max"
            }
        }

        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(data, temp_file)
        temp_file.close()
        temp_path = Path(temp_file.name)

        try:
            with patch('claude_agent_sdk._internal.oauth_credentials.get_credentials_path', return_value=temp_path):
                creds = get_valid_credentials()
                assert creds is None
        finally:
            temp_path.unlink()

    def test_get_valid_credentials_when_not_found(self):
        """Test get_valid_credentials returns None when file not found."""
        nonexistent_path = Path("/nonexistent/path/.credentials.json")
        with patch('claude_agent_sdk._internal.oauth_credentials.get_credentials_path', return_value=nonexistent_path):
            creds = get_valid_credentials()
            assert creds is None

    def test_get_valid_credentials_when_corrupted(self):
        """Test get_valid_credentials returns None when file corrupted."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_file.write("{ invalid json }")
        temp_file.close()
        temp_path = Path(temp_file.name)

        try:
            with patch('claude_agent_sdk._internal.oauth_credentials.get_credentials_path', return_value=temp_path):
                creds = get_valid_credentials()
                assert creds is None
        finally:
            temp_path.unlink()
