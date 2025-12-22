"""Tests for CLI detection module."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from claude_agent_sdk._errors import CLINotFoundError
from claude_agent_sdk._internal.cli_detection import find_claude_cli


class TestFindClaudeCLI:
    """Tests for find_claude_cli function."""

    def test_finds_cli_in_path(self):
        """Test finding Claude CLI via shutil.which (PATH)."""
        expected_path = "/usr/bin/claude"

        with patch("claude_agent_sdk._internal.cli_detection.shutil.which", return_value=expected_path):
            result = find_claude_cli()

        assert result == expected_path

    def test_finds_cli_in_fallback_locations(self):
        """Test finding Claude CLI in fallback locations."""
        # Test by actually creating a temporary file that will be found
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a fake claude CLI
            cli_path = Path(tmpdir) / ".npm-global" / "bin" / "claude"
            cli_path.parent.mkdir(parents=True)
            cli_path.touch()

            # Mock Path.home() to return our temp directory
            with (
                patch("claude_agent_sdk._internal.cli_detection.shutil.which", return_value=None),
                patch("claude_agent_sdk._internal.cli_detection.Path.home", return_value=Path(tmpdir)),
            ):
                result = find_claude_cli()

                assert ".npm-global" in result and "claude" in result

    def test_raises_cli_not_found_error_when_not_found(self):
        """Test that CLINotFoundError is raised when Claude CLI is not found."""
        with (
            patch("claude_agent_sdk._internal.cli_detection.shutil.which", return_value=None),
            patch("claude_agent_sdk._internal.cli_detection.Path") as mock_path_class,
            pytest.raises(CLINotFoundError) as exc_info,
        ):
            # Mock all paths to not exist
            def create_mock_path(path_str):
                mock = MagicMock()
                mock.__truediv__ = lambda self, other: create_mock_path(f"{path_str}/{other}")
                mock.__str__ = lambda self: path_str
                mock.exists.return_value = False
                mock.is_file.return_value = False
                return mock

            mock_path_class.side_effect = lambda p: create_mock_path(str(p))
            mock_path_class.home.return_value = create_mock_path(str(Path.home()))

            find_claude_cli()

        error_msg = str(exc_info.value)
        assert "Claude Code CLI not found" in error_msg
        assert "npm install" in error_msg

    def test_returns_absolute_path_from_which(self):
        """Test that the function returns an absolute path when found via which."""
        expected_path = "/usr/bin/claude"

        with patch("claude_agent_sdk._internal.cli_detection.shutil.which", return_value=expected_path):
            result = find_claude_cli()

        # shutil.which already returns absolute paths
        assert Path(result).is_absolute() or result.startswith("/")

    def test_windows_exe_extension(self):
        """Test finding Claude CLI with .exe extension on Windows."""
        home = Path.home()
        expected_path = home / ".claude/bin/claude.exe"

        with (
            patch("claude_agent_sdk._internal.cli_detection.shutil.which", return_value=None),
            patch("claude_agent_sdk._internal.cli_detection.platform.system", return_value="Windows"),
            patch("claude_agent_sdk._internal.cli_detection.Path") as mock_path_class,
            patch.dict(os.environ, {"LOCALAPPDATA": str(home / "AppData/Local"), "APPDATA": str(home / "AppData/Roaming")}),
        ):
            # Mock Path.home()
            mock_path_class.home.return_value = home

            # Create mock path instances
            def create_mock_path(path_str):
                mock = MagicMock()
                mock.__truediv__ = lambda self, other: create_mock_path(f"{path_str}/{other}" if not str(path_str).endswith("\\") else f"{path_str}{other}")
                mock.__str__ = lambda self: path_str
                mock.exists.return_value = "claude.exe" in str(path_str) and ".claude" in str(path_str)
                mock.is_file.return_value = "claude.exe" in str(path_str) and ".claude" in str(path_str)
                mock.absolute.return_value = path_str
                return mock

            mock_path_class.side_effect = lambda p: create_mock_path(str(p))
            mock_path_class.home.return_value = create_mock_path(str(home))

            result = find_claude_cli()

            assert "claude.exe" in result

    def test_macos_homebrew_paths(self):
        """Test finding Claude CLI in macOS Homebrew locations."""
        expected_path = "/opt/homebrew/bin/claude"

        with (
            patch("claude_agent_sdk._internal.cli_detection.shutil.which", return_value=None),
            patch("claude_agent_sdk._internal.cli_detection.platform.system", return_value="Darwin"),
            patch("claude_agent_sdk._internal.cli_detection.Path") as mock_path_class,
        ):
            home = Path.home()
            mock_path_class.home.return_value = home

            # Create mock path instances
            def create_mock_path(path_str):
                mock = MagicMock()
                mock.__truediv__ = lambda self, other: create_mock_path(f"{path_str}/{other}")
                mock.__str__ = lambda self: path_str
                mock.exists.return_value = str(path_str) == expected_path
                mock.is_file.return_value = str(path_str) == expected_path
                mock.absolute.return_value = path_str
                return mock

            mock_path_class.side_effect = lambda p: create_mock_path(str(p))
            mock_path_class.home.return_value = create_mock_path(str(home))

            result = find_claude_cli()

            assert result == expected_path

    def test_linux_paths(self):
        """Test finding Claude CLI in Linux locations."""
        expected_path = "/usr/local/bin/claude"

        with (
            patch("claude_agent_sdk._internal.cli_detection.shutil.which", return_value=None),
            patch("claude_agent_sdk._internal.cli_detection.platform.system", return_value="Linux"),
            patch("claude_agent_sdk._internal.cli_detection.Path") as mock_path_class,
        ):
            home = Path.home()
            mock_path_class.home.return_value = home

            # Create mock path instances
            def create_mock_path(path_str):
                mock = MagicMock()
                mock.__truediv__ = lambda self, other: create_mock_path(f"{path_str}/{other}")
                mock.__str__ = lambda self: path_str
                mock.exists.return_value = str(path_str) == expected_path
                mock.is_file.return_value = str(path_str) == expected_path
                mock.absolute.return_value = path_str
                return mock

            mock_path_class.side_effect = lambda p: create_mock_path(str(p))
            mock_path_class.home.return_value = create_mock_path(str(home))

            result = find_claude_cli()

            assert result == expected_path
