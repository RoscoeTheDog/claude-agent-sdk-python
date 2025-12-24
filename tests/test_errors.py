"""Tests for Claude SDK error handling."""

import platform
from unittest.mock import patch

from claude_agent_sdk import (
    ClaudeCodeNotFoundError,
    ClaudeSDKError,
    CLIConnectionError,
    CLIJSONDecodeError,
    CLINotFoundError,
    ProcessError,
)


class TestErrorTypes:
    """Test error types and their properties."""

    def test_base_error(self):
        """Test base ClaudeSDKError."""
        error = ClaudeSDKError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert isinstance(error, Exception)

    def test_cli_not_found_error(self):
        """Test CLINotFoundError."""
        error = CLINotFoundError("Claude Code not found")
        assert isinstance(error, ClaudeSDKError)
        assert "Claude Code not found" in str(error)

    def test_connection_error(self):
        """Test CLIConnectionError."""
        error = CLIConnectionError("Failed to connect to CLI")
        assert isinstance(error, ClaudeSDKError)
        assert "Failed to connect to CLI" in str(error)

    def test_process_error(self):
        """Test ProcessError with exit code and stderr."""
        error = ProcessError("Process failed", exit_code=1, stderr="Command not found")
        assert error.exit_code == 1
        assert error.stderr == "Command not found"
        assert "Process failed" in str(error)
        assert "exit code: 1" in str(error)
        assert "Command not found" in str(error)

    def test_json_decode_error(self):
        """Test CLIJSONDecodeError."""
        import json

        try:
            json.loads("{invalid json}")
        except json.JSONDecodeError as e:
            error = CLIJSONDecodeError("{invalid json}", e)
            assert error.line == "{invalid json}"
            assert error.original_error == e
            assert "Failed to decode JSON" in str(error)


class TestClaudeCodeNotFoundError:
    """Test ClaudeCodeNotFoundError comprehensive installation instructions."""

    def test_default_message_includes_installation_instructions(self):
        """Test that default error message includes comprehensive installation instructions."""
        error = ClaudeCodeNotFoundError()
        error_msg = str(error)

        # Check main error message
        assert "Claude Code CLI not found" in error_msg

        # Check installation options section
        assert "Installation options:" in error_msg

    def test_npm_install_command_included(self):
        """Test that npm install command is included in error message (AC-2.2)."""
        error = ClaudeCodeNotFoundError()
        error_msg = str(error)

        # Check npm command is present
        assert "npm install -g @anthropic-ai/claude-code" in error_msg
        assert "npm (recommended - works on all platforms)" in error_msg

    def test_pip_auto_oauth_extra_included(self):
        """Test that pip install with auto-oauth extra is included (AC-2.4)."""
        error = ClaudeCodeNotFoundError()
        error_msg = str(error)

        # Check pip with auto-oauth extra
        assert "pip install 'claude-agent-sdk[auto-oauth]'" in error_msg
        assert "pip with auto-oauth extra" in error_msg

    def test_anthropic_docs_link_included(self):
        """Test that Anthropic documentation link is included (AC-2.5)."""
        error = ClaudeCodeNotFoundError()
        error_msg = str(error)

        # Check documentation link
        assert (
            "https://docs.anthropic.com/en/docs/claude-code/installation" in error_msg
        )
        assert "For more information, visit:" in error_msg

    def test_homebrew_install_on_macos(self):
        """Test that Homebrew installation is included on macOS (AC-2.3)."""
        with patch.object(platform, "system", return_value="Darwin"):
            error = ClaudeCodeNotFoundError()
            error_msg = str(error)

            # Check Homebrew instructions present on macOS
            assert "brew install claude-code" in error_msg
            assert "Homebrew (macOS only)" in error_msg

    def test_no_homebrew_on_non_macos(self):
        """Test that Homebrew installation is not included on non-macOS platforms."""
        with patch.object(platform, "system", return_value="Linux"):
            error = ClaudeCodeNotFoundError()
            error_msg = str(error)

            # Check Homebrew instructions not present on Linux
            assert "brew install" not in error_msg
            assert "Homebrew" not in error_msg

        with patch.object(platform, "system", return_value="Windows"):
            error = ClaudeCodeNotFoundError()
            error_msg = str(error)

            # Check Homebrew instructions not present on Windows
            assert "brew install" not in error_msg
            assert "Homebrew" not in error_msg

    def test_custom_cli_path_parameter(self):
        """Test that cli_path parameter is included in error message."""
        error = ClaudeCodeNotFoundError(cli_path="/usr/local/bin/claude")
        error_msg = str(error)

        # Check cli_path is appended
        assert "Searched path: /usr/local/bin/claude" in error_msg

    def test_custom_message_parameter(self):
        """Test that custom message parameter overrides default message."""
        custom_msg = "Custom error message"
        error = ClaudeCodeNotFoundError(message=custom_msg)
        error_msg = str(error)

        # Custom message should be used instead of default
        assert custom_msg in error_msg
        # Default installation instructions should not be present
        assert "Installation options:" not in error_msg

    def test_custom_message_with_cli_path(self):
        """Test that cli_path is appended even with custom message."""
        custom_msg = "Custom error"
        error = ClaudeCodeNotFoundError(message=custom_msg, cli_path="/opt/claude")
        error_msg = str(error)

        assert custom_msg in error_msg
        assert "Searched path: /opt/claude" in error_msg

    def test_backwards_compatibility_alias(self):
        """Test that CLINotFoundError is an alias for ClaudeCodeNotFoundError."""
        # CLINotFoundError should be the same class
        assert CLINotFoundError is ClaudeCodeNotFoundError

        # Creating CLINotFoundError should work the same way
        error = CLINotFoundError()
        assert isinstance(error, ClaudeCodeNotFoundError)
        assert isinstance(error, CLIConnectionError)
        assert "Claude Code CLI not found" in str(error)

    def test_inheritance_hierarchy(self):
        """Test that ClaudeCodeNotFoundError inherits from CLIConnectionError."""
        error = ClaudeCodeNotFoundError()

        # Check inheritance chain
        assert isinstance(error, ClaudeCodeNotFoundError)
        assert isinstance(error, CLIConnectionError)
        assert isinstance(error, ClaudeSDKError)
        assert isinstance(error, Exception)

    def test_custom_installation_option_included(self):
        """Test that custom installation option with ClaudeAgentOptions is mentioned."""
        error = ClaudeCodeNotFoundError()
        error_msg = str(error)

        # Check developer option for custom paths
        assert "For custom installations, use ClaudeAgentOptions:" in error_msg
        assert "ClaudeAgentOptions(cli_path='/path/to/claude')" in error_msg

    def test_platform_specific_numbering(self):
        """Test that installation option numbering adjusts based on platform."""
        # On macOS: npm=1, Homebrew=2, pip=3
        with patch.object(platform, "system", return_value="Darwin"):
            error = ClaudeCodeNotFoundError()
            error_msg = str(error)
            assert "1. npm" in error_msg
            assert "2. Homebrew" in error_msg
            assert "3. pip" in error_msg

        # On non-macOS: npm=1, pip=2 (no Homebrew)
        with patch.object(platform, "system", return_value="Linux"):
            error = ClaudeCodeNotFoundError()
            error_msg = str(error)
            assert "1. npm" in error_msg
            assert "2. pip" in error_msg
            assert "3. pip" not in error_msg

    def test_error_message_contains_installation_commands(self):
        """Test that error message contains complete installation commands (P1 AC)."""
        error = ClaudeCodeNotFoundError()
        error_msg = str(error)

        # Verify npm command with exact package name
        assert "npm install -g @anthropic-ai/claude-code" in error_msg

        # Verify pip command with auto-oauth extra
        assert "pip install 'claude-agent-sdk[auto-oauth]'" in error_msg

        # On macOS, verify Homebrew command
        with patch.object(platform, "system", return_value="Darwin"):
            error = ClaudeCodeNotFoundError()
            error_msg = str(error)
            assert "brew install claude-code" in error_msg

    def test_error_message_contains_docs_link(self):
        """Test that error message contains Anthropic documentation link (P1 AC)."""
        error = ClaudeCodeNotFoundError()
        error_msg = str(error)

        # Verify full documentation URL
        assert "https://docs.anthropic.com/en/docs/claude-code/installation" in error_msg
        assert "For more information, visit:" in error_msg

    def test_error_message_contains_custom_path_option(self):
        """Test that error message mentions ClaudeAgentOptions for custom paths (P1 AC)."""
        error = ClaudeCodeNotFoundError()
        error_msg = str(error)

        # Verify developer option is mentioned
        assert "For custom installations, use ClaudeAgentOptions:" in error_msg
        assert "ClaudeAgentOptions(cli_path='/path/to/claude')" in error_msg

    def test_searched_path_appended_to_message(self):
        """Test that specific searched path is appended when cli_path provided (P1 AC)."""
        custom_path = "/opt/custom/bin/claude"
        error = ClaudeCodeNotFoundError(cli_path=custom_path)
        error_msg = str(error)

        # Verify the searched path is mentioned
        assert f"Searched path: {custom_path}" in error_msg

    def test_custom_message_overrides_default(self):
        """Test that custom message parameter overrides all default content (P1 AC)."""
        custom_msg = "Custom installation message"
        error = ClaudeCodeNotFoundError(message=custom_msg)
        error_msg = str(error)

        # Should have custom message
        assert custom_msg in error_msg

        # Should NOT have default installation instructions
        assert "Installation options:" not in error_msg
        assert "npm install" not in error_msg

    def test_custom_message_preserves_cli_path(self):
        """Test that cli_path is appended even with custom message (P1 AC)."""
        custom_msg = "Custom message"
        custom_path = "/usr/local/bin/claude"
        error = ClaudeCodeNotFoundError(message=custom_msg, cli_path=custom_path)
        error_msg = str(error)

        # Should have both custom message and cli_path
        assert custom_msg in error_msg
        assert f"Searched path: {custom_path}" in error_msg

    def test_error_message_platform_specific_content_windows(self):
        """Test Windows-specific error message content (P1 AC)."""
        with patch.object(platform, "system", return_value="Windows"):
            error = ClaudeCodeNotFoundError()
            error_msg = str(error)

            # Should have npm (cross-platform)
            assert "npm install -g @anthropic-ai/claude-code" in error_msg

            # Should have pip
            assert "pip install 'claude-agent-sdk[auto-oauth]'" in error_msg

            # Should NOT have Homebrew
            assert "brew install" not in error_msg
            assert "Homebrew" not in error_msg

    def test_error_message_platform_specific_content_macos(self):
        """Test macOS-specific error message content (P1 AC)."""
        with patch.object(platform, "system", return_value="Darwin"):
            error = ClaudeCodeNotFoundError()
            error_msg = str(error)

            # Should have all three options on macOS
            assert "npm install -g @anthropic-ai/claude-code" in error_msg
            assert "brew install claude-code" in error_msg
            assert "pip install 'claude-agent-sdk[auto-oauth]'" in error_msg

    def test_error_message_platform_specific_content_linux(self):
        """Test Linux-specific error message content (P1 AC)."""
        with patch.object(platform, "system", return_value="Linux"):
            error = ClaudeCodeNotFoundError()
            error_msg = str(error)

            # Should have npm and pip
            assert "npm install -g @anthropic-ai/claude-code" in error_msg
            assert "pip install 'claude-agent-sdk[auto-oauth]'" in error_msg

            # Should NOT have Homebrew
            assert "brew install" not in error_msg
            assert "Homebrew" not in error_msg

    def test_error_message_structure_completeness(self):
        """Test that error message has all required structural elements (P1 AC)."""
        error = ClaudeCodeNotFoundError()
        error_msg = str(error)

        # Main error statement
        assert "Claude Code CLI not found" in error_msg

        # Installation options header
        assert "Installation options:" in error_msg

        # At least 2 installation methods (npm + pip minimum)
        assert "1." in error_msg
        assert "2." in error_msg

        # Documentation reference
        assert "For more information, visit:" in error_msg

        # Developer option
        assert "For custom installations, use ClaudeAgentOptions:" in error_msg
