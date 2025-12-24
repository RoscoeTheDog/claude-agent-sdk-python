"""Tests for CLI detection module."""

import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from claude_agent_sdk._errors import ClaudeCodeNotFoundError, CLINotFoundError
from claude_agent_sdk._internal.cli_detection import (
    _attempt_auto_install,
    find_claude_cli,
    get_claude_cli_or_install,
)


class TestFindClaudeCLI:
    """Tests for find_claude_cli function."""

    def test_finds_cli_in_path(self):
        """Test finding Claude CLI via shutil.which (PATH)."""
        expected_path = "/usr/bin/claude"

        with patch(
            "claude_agent_sdk._internal.cli_detection.shutil.which",
            return_value=expected_path,
        ):
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
                patch(
                    "claude_agent_sdk._internal.cli_detection.shutil.which",
                    return_value=None,
                ),
                patch(
                    "claude_agent_sdk._internal.cli_detection.Path.home",
                    return_value=Path(tmpdir),
                ),
            ):
                result = find_claude_cli()

                assert ".npm-global" in result and "claude" in result

    def test_raises_cli_not_found_error_when_not_found(self):
        """Test that CLINotFoundError is raised when Claude CLI is not found."""
        with (
            patch(
                "claude_agent_sdk._internal.cli_detection.shutil.which",
                return_value=None,
            ),
            patch("claude_agent_sdk._internal.cli_detection.Path") as mock_path_class,
            pytest.raises(CLINotFoundError) as exc_info,
        ):
            # Mock all paths to not exist
            def create_mock_path(path_str):
                mock = MagicMock()
                mock.__truediv__ = lambda self, other: create_mock_path(
                    f"{path_str}/{other}"
                )
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

        with patch(
            "claude_agent_sdk._internal.cli_detection.shutil.which",
            return_value=expected_path,
        ):
            result = find_claude_cli()

        # shutil.which already returns absolute paths
        assert Path(result).is_absolute() or result.startswith("/")

    def test_windows_exe_extension(self):
        """Test finding Claude CLI with .exe extension on Windows."""
        home = Path.home()

        with (
            patch(
                "claude_agent_sdk._internal.cli_detection.shutil.which",
                return_value=None,
            ),
            patch(
                "claude_agent_sdk._internal.cli_detection.platform.system",
                return_value="Windows",
            ),
            patch("claude_agent_sdk._internal.cli_detection.Path") as mock_path_class,
            patch.dict(
                os.environ,
                {
                    "LOCALAPPDATA": str(home / "AppData/Local"),
                    "APPDATA": str(home / "AppData/Roaming"),
                },
            ),
        ):
            # Mock Path.home()
            mock_path_class.home.return_value = home

            # Create mock path instances
            def create_mock_path(path_str):
                mock = MagicMock()
                mock.__truediv__ = lambda self, other: create_mock_path(
                    f"{path_str}/{other}"
                    if not str(path_str).endswith("\\")
                    else f"{path_str}{other}"
                )
                mock.__str__ = lambda self: path_str
                mock.exists.return_value = "claude.exe" in str(
                    path_str
                ) and ".claude" in str(path_str)
                mock.is_file.return_value = "claude.exe" in str(
                    path_str
                ) and ".claude" in str(path_str)
                mock.absolute.return_value = path_str
                return mock

            mock_path_class.side_effect = lambda p: create_mock_path(str(p))
            mock_path_class.home.return_value = create_mock_path(str(home))

            result = find_claude_cli()

            assert "claude.exe" in result

    def test_windows_cmd_extension(self):
        """Test finding Claude CLI with .cmd extension on Windows (npm install)."""
        home = Path.home()
        appdata_local = home / "AppData/Local"

        with (
            patch(
                "claude_agent_sdk._internal.cli_detection.shutil.which",
                return_value=None,
            ),
            patch(
                "claude_agent_sdk._internal.cli_detection.platform.system",
                return_value="Windows",
            ),
            patch("claude_agent_sdk._internal.cli_detection.Path") as mock_path_class,
            patch.dict(
                os.environ,
                {
                    "LOCALAPPDATA": str(appdata_local),
                    "APPDATA": str(home / "AppData/Roaming"),
                },
            ),
        ):
            # Mock Path.home()
            mock_path_class.home.return_value = home

            # Create mock path instances
            def create_mock_path(path_str):
                mock = MagicMock()
                mock.__truediv__ = lambda self, other: create_mock_path(
                    f"{path_str}/{other}"
                    if not str(path_str).endswith("\\")
                    else f"{path_str}{other}"
                )
                mock.__str__ = lambda self: path_str
                # Match the npm .cmd path
                mock.exists.return_value = "claude.cmd" in str(
                    path_str
                ) and "npm" in str(path_str)
                mock.is_file.return_value = "claude.cmd" in str(
                    path_str
                ) and "npm" in str(path_str)
                mock.absolute.return_value = path_str
                return mock

            mock_path_class.side_effect = lambda p: create_mock_path(str(p))
            mock_path_class.home.return_value = create_mock_path(str(home))

            result = find_claude_cli()

            assert "claude.cmd" in result
            assert "npm" in result

    def test_macos_homebrew_paths(self):
        """Test finding Claude CLI in macOS Homebrew locations."""
        expected_path = "/opt/homebrew/bin/claude"

        with (
            patch(
                "claude_agent_sdk._internal.cli_detection.shutil.which",
                return_value=None,
            ),
            patch(
                "claude_agent_sdk._internal.cli_detection.platform.system",
                return_value="Darwin",
            ),
            patch("claude_agent_sdk._internal.cli_detection.Path") as mock_path_class,
        ):
            home = Path.home()
            mock_path_class.home.return_value = home

            # Create mock path instances
            def create_mock_path(path_str):
                mock = MagicMock()
                mock.__truediv__ = lambda self, other: create_mock_path(
                    f"{path_str}/{other}"
                )
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
            patch(
                "claude_agent_sdk._internal.cli_detection.shutil.which",
                return_value=None,
            ),
            patch(
                "claude_agent_sdk._internal.cli_detection.platform.system",
                return_value="Linux",
            ),
            patch("claude_agent_sdk._internal.cli_detection.Path") as mock_path_class,
        ):
            home = Path.home()
            mock_path_class.home.return_value = home

            # Create mock path instances
            def create_mock_path(path_str):
                mock = MagicMock()
                mock.__truediv__ = lambda self, other: create_mock_path(
                    f"{path_str}/{other}"
                )
                mock.__str__ = lambda self: path_str
                mock.exists.return_value = str(path_str) == expected_path
                mock.is_file.return_value = str(path_str) == expected_path
                mock.absolute.return_value = path_str
                return mock

            mock_path_class.side_effect = lambda p: create_mock_path(str(p))
            mock_path_class.home.return_value = create_mock_path(str(home))

            result = find_claude_cli()

            assert result == expected_path

    @pytest.mark.parametrize(
        "platform_name,path_to_find,expected_in_result",
        [
            # Cross-platform paths (work on all platforms)
            ("Linux", ".npm-global/bin/claude", ".npm-global"),
            ("Darwin", ".npm-global/bin/claude", ".npm-global"),
            ("Windows", ".npm-global/bin/claude", ".npm-global"),
            ("Linux", ".local/bin/claude", ".local"),
            ("Darwin", ".local/bin/claude", ".local"),
            ("Windows", ".local/bin/claude", ".local"),
            ("Linux", "node_modules/.bin/claude", "node_modules"),
            ("Darwin", "node_modules/.bin/claude", "node_modules"),
            ("Windows", "node_modules/.bin/claude", "node_modules"),
            ("Linux", ".yarn/bin/claude", ".yarn"),
            ("Darwin", ".yarn/bin/claude", ".yarn"),
            ("Windows", ".yarn/bin/claude", ".yarn"),
            ("Linux", ".claude/local/claude", ".claude/local"),
            ("Darwin", ".claude/local/claude", ".claude/local"),
            ("Windows", ".claude/local/claude", ".claude/local"),
            # macOS-specific paths
            ("Darwin", "/usr/local/bin/claude", "/usr/local/bin"),
            ("Darwin", "/opt/homebrew/bin/claude", "/opt/homebrew/bin"),
            # Linux-specific paths
            ("Linux", "/usr/local/bin/claude", "/usr/local/bin"),
            ("Linux", "/usr/bin/claude", "/usr/bin"),
            # Windows-specific paths
            ("Windows", "AppData/Local/npm/claude.cmd", "claude.cmd"),
            ("Windows", "AppData/Roaming/npm/claude.cmd", "claude.cmd"),
            ("Windows", ".claude/bin/claude.exe", "claude.exe"),
            ("Windows", ".claude/bin/claude.cmd", "claude.cmd"),
        ],
    )
    def test_exhaustive_fallback_path_coverage(
        self, platform_name, path_to_find, expected_in_result
    ):
        """Test that all documented fallback paths are properly searched (P0 AC).

        This test ensures complete coverage of all 11+ fallback locations across
        Windows, macOS, and Linux platforms as documented in cli_detection.py.
        """
        home = Path.home()

        with (
            patch(
                "claude_agent_sdk._internal.cli_detection.shutil.which",
                return_value=None,
            ),
            patch(
                "claude_agent_sdk._internal.cli_detection.platform.system",
                return_value=platform_name,
            ),
            patch("claude_agent_sdk._internal.cli_detection.Path") as mock_path_class,
            patch.dict(
                os.environ,
                {
                    "LOCALAPPDATA": str(home / "AppData/Local"),
                    "APPDATA": str(home / "AppData/Roaming"),
                },
            ),
        ):
            mock_path_class.home.return_value = home

            def create_mock_path(path_str):
                mock = MagicMock()
                mock.__truediv__ = lambda self, other: create_mock_path(
                    f"{path_str}/{other}"
                    if not str(path_str).endswith("\\")
                    else f"{path_str}{other}"
                )
                mock.__str__ = lambda self: path_str
                # Match the path we're looking for
                mock.exists.return_value = path_to_find in str(path_str).replace("\\", "/")
                mock.is_file.return_value = path_to_find in str(path_str).replace("\\", "/")
                mock.absolute.return_value = path_str
                return mock

            mock_path_class.side_effect = lambda p: create_mock_path(str(p))
            mock_path_class.home.return_value = create_mock_path(str(home))

            result = find_claude_cli()

            # Verify the expected path component is in result
            assert expected_in_result in result

    def test_path_priority_order(self):
        """Test that PATH detection takes priority over fallback locations (P1).

        When CLI is found both in PATH and fallback locations, PATH should win.
        """
        path_location = "/usr/bin/claude"

        with patch(
            "claude_agent_sdk._internal.cli_detection.shutil.which",
            return_value=path_location,
        ) as mock_which:
            # Even if fallbacks exist, should return PATH result
            result = find_claude_cli()

            assert result == path_location
            mock_which.assert_called_once_with("claude")

    def test_fallback_locations_checked_in_order(self):
        """Test that fallback locations are checked sequentially (P1).

        First matching location should be returned, not last.
        """
        home = Path.home()
        # Create scenario where .npm-global exists (first cross-platform location)

        with (
            patch(
                "claude_agent_sdk._internal.cli_detection.shutil.which",
                return_value=None,
            ),
            patch(
                "claude_agent_sdk._internal.cli_detection.platform.system",
                return_value="Linux",
            ),
            patch("claude_agent_sdk._internal.cli_detection.Path") as mock_path_class,
        ):
            mock_path_class.home.return_value = home

            def create_mock_path(path_str):
                mock = MagicMock()
                mock.__truediv__ = lambda self, other: create_mock_path(
                    f"{path_str}/{other}"
                )
                mock.__str__ = lambda self: path_str
                # Make .npm-global the first to exist
                mock.exists.return_value = ".npm-global" in str(path_str)
                mock.is_file.return_value = ".npm-global" in str(path_str)
                mock.absolute.return_value = path_str
                return mock

            mock_path_class.side_effect = lambda p: create_mock_path(str(p))
            mock_path_class.home.return_value = create_mock_path(str(home))

            result = find_claude_cli()

            # Should find .npm-global first (before .local, node_modules, etc.)
            assert ".npm-global" in result

    def test_windows_environment_variables_fallback(self):
        """Test Windows LOCALAPPDATA/APPDATA fallback when env vars missing (P1)."""
        home = Path("C:/Users/test")

        # Test without LOCALAPPDATA set
        with (
            patch(
                "claude_agent_sdk._internal.cli_detection.shutil.which",
                return_value=None,
            ),
            patch(
                "claude_agent_sdk._internal.cli_detection.platform.system",
                return_value="Windows",
            ),
            patch("claude_agent_sdk._internal.cli_detection.Path") as mock_path_class,
            patch.dict(os.environ, {}, clear=True),  # Clear env vars
        ):
            mock_path_class.home.return_value = home

            def create_mock_path(path_str):
                mock = MagicMock()
                mock.__truediv__ = lambda self, other: create_mock_path(
                    f"{path_str}/{other}"
                    if not str(path_str).endswith("\\")
                    else f"{path_str}{other}"
                )
                mock.__str__ = lambda self: path_str
                # Find in .claude/bin as fallback
                mock.exists.return_value = ".claude/bin/claude.exe" in str(path_str).replace("\\", "/")
                mock.is_file.return_value = ".claude/bin/claude.exe" in str(path_str).replace("\\", "/")
                mock.absolute.return_value = path_str
                return mock

            mock_path_class.side_effect = lambda p: create_mock_path(str(p))
            mock_path_class.home.return_value = create_mock_path(str(home))

            # Should still work even without LOCALAPPDATA/APPDATA
            result = find_claude_cli()
            assert "claude.exe" in result


class TestGetClaudeCliOrInstall:
    """Tests for get_claude_cli_or_install function."""

    def test_finds_existing_cli_without_auto_install(self):
        """Test that existing CLI is found without attempting auto-install."""
        expected_path = "/usr/bin/claude"

        with patch(
            "claude_agent_sdk._internal.cli_detection.find_claude_cli",
            return_value=expected_path,
        ) as mock_find, patch(
            "claude_agent_sdk._internal.cli_detection._attempt_auto_install"
        ) as mock_install:
            result = get_claude_cli_or_install()

        assert result == expected_path
        mock_find.assert_called_once()
        mock_install.assert_not_called()

    def test_falls_back_to_auto_install_when_not_found(self):
        """Test that auto-install is attempted when find_claude_cli fails."""
        expected_path = str(Path.home() / ".claude-sdk" / "bin" / "claude")

        with patch(
            "claude_agent_sdk._internal.cli_detection.find_claude_cli",
            side_effect=ClaudeCodeNotFoundError(),
        ), patch(
            "claude_agent_sdk._internal.cli_detection._attempt_auto_install",
            return_value=expected_path,
        ) as mock_install:
            result = get_claude_cli_or_install()

        assert result == expected_path
        mock_install.assert_called_once()


class TestAttemptAutoInstall:
    """Tests for _attempt_auto_install function."""

    def test_auto_install_success_unix(self):
        """Test successful auto-install on Unix-like systems."""
        # Mock the npm module
        mock_npm = Mock()
        mock_npm.run = Mock(return_value=Mock(returncode=0))

        # Create temporary directory simulation
        home = Path("/home/testuser")
        install_dir = home / ".claude-sdk"
        cli_path = install_dir / "bin" / "claude"

        with (
            patch.dict("sys.modules", {"nodejs": Mock(npm=mock_npm)}),
            patch("claude_agent_sdk._internal.cli_detection.platform.system", return_value="Linux"),
            patch("claude_agent_sdk._internal.cli_detection.Path.home", return_value=home),
        ):
            # Mock mkdir for the install directory
            with patch.object(Path, "mkdir") as mock_mkdir:
                # Mock exists and is_file for the CLI path
                with (
                    patch.object(Path, "exists") as mock_exists,
                    patch.object(Path, "is_file") as mock_is_file,
                ):
                    # Setup: first two calls for candidates check (fail for bin/claude), third succeeds
                    mock_exists.side_effect = [True]  # CLI exists
                    mock_is_file.side_effect = [True]  # CLI is a file

                    result = _attempt_auto_install()

                    # Verify result is a string path
                    assert "claude" in result
                    assert ".claude-sdk" in result

                    # Verify npm.run was called
                    mock_npm.run.assert_called_once()

                    # Verify npm install arguments
                    call_args = mock_npm.run.call_args
                    assert "install" in call_args[0][0]
                    assert "-g" in call_args[0][0]
                    assert "@anthropic-ai/claude-code" in call_args[0][0]
                    assert "--prefix" in call_args[0][0]

    def test_auto_install_success_windows(self):
        """Test successful auto-install on Windows."""
        # Mock the npm module
        mock_npm = Mock()
        mock_npm.run = Mock(return_value=Mock(returncode=0))

        home = Path("C:/Users/testuser")

        with (
            patch.dict("sys.modules", {"nodejs": Mock(npm=mock_npm)}),
            patch("claude_agent_sdk._internal.cli_detection.platform.system", return_value="Windows"),
            patch("claude_agent_sdk._internal.cli_detection.Path.home", return_value=home),
        ):
            with patch.object(Path, "mkdir"):
                with (
                    patch.object(Path, "exists") as mock_exists,
                    patch.object(Path, "is_file") as mock_is_file,
                ):
                    # Windows checks .cmd first, then .exe - make .cmd succeed
                    mock_exists.side_effect = [True, False]  # .cmd exists, .exe doesn't
                    mock_is_file.side_effect = [True, False]  # .cmd is file, .exe isn't

                    result = _attempt_auto_install()

                    assert "claude" in result
                    assert ".claude-sdk" in result
                    mock_npm.run.assert_called_once()

    def test_auto_install_nodejs_bin_not_installed(self):
        """Test graceful handling when nodejs-bin is not installed."""
        # Mock import to raise ImportError for nodejs module
        import builtins

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "nodejs":
                raise ImportError("No module named 'nodejs'")
            return original_import(name, *args, **kwargs)

        with patch.object(builtins, "__import__", side_effect=mock_import):
            with pytest.raises(ClaudeCodeNotFoundError) as exc_info:
                _attempt_auto_install()

        error_msg = str(exc_info.value)
        assert "Claude Code CLI not found" in error_msg
        assert "auto-oauth" in error_msg

    def test_auto_install_npm_install_fails(self):
        """Test handling of npm install failure."""
        mock_npm = Mock()
        mock_npm.run = Mock(
            side_effect=subprocess.CalledProcessError(
                returncode=1, cmd="npm install", stderr="Network error"
            )
        )

        home = Path("/home/testuser")

        with (
            patch.dict("sys.modules", {"nodejs": Mock(npm=mock_npm)}),
            patch("claude_agent_sdk._internal.cli_detection.Path.home", return_value=home),
        ):
            with patch.object(Path, "mkdir"):
                with pytest.raises(ClaudeCodeNotFoundError) as exc_info:
                    _attempt_auto_install()

        error_msg = str(exc_info.value)
        assert "Auto-install failed" in error_msg
        assert "exit code 1" in error_msg
        assert "Network error" in error_msg

    def test_auto_install_timeout(self):
        """Test handling of npm install timeout."""
        mock_npm = Mock()
        mock_npm.run = Mock(
            side_effect=subprocess.TimeoutExpired(cmd="npm install", timeout=300)
        )

        home = Path("/home/testuser")

        with (
            patch.dict("sys.modules", {"nodejs": Mock(npm=mock_npm)}),
            patch("claude_agent_sdk._internal.cli_detection.Path.home", return_value=home),
        ):
            with patch.object(Path, "mkdir"):
                with pytest.raises(ClaudeCodeNotFoundError) as exc_info:
                    _attempt_auto_install()

        error_msg = str(exc_info.value)
        assert "Auto-install timed out" in error_msg
        assert "manual installation" in error_msg

    def test_auto_install_cli_not_found_after_install(self):
        """Test handling when npm install succeeds but CLI not found at expected location."""
        mock_npm = Mock()
        mock_npm.run = Mock(return_value=Mock(returncode=0))

        home = Path("/home/testuser")

        with (
            patch.dict("sys.modules", {"nodejs": Mock(npm=mock_npm)}),
            patch("claude_agent_sdk._internal.cli_detection.platform.system", return_value="Linux"),
            patch("claude_agent_sdk._internal.cli_detection.Path.home", return_value=home),
        ):
            with patch.object(Path, "mkdir"):
                with (
                    patch.object(Path, "exists", return_value=False),
                    patch.object(Path, "is_file", return_value=False),
                ):
                    with pytest.raises(ClaudeCodeNotFoundError) as exc_info:
                        _attempt_auto_install()

        error_msg = str(exc_info.value)
        assert "Auto-install completed but CLI not found" in error_msg
        assert ".claude-sdk/bin/" in error_msg

    def test_auto_install_creates_directory(self):
        """Test that auto-install creates .claude-sdk directory."""
        mock_npm = Mock()
        mock_npm.run = Mock(return_value=Mock(returncode=0))

        home = Path("/home/testuser")

        with (
            patch.dict("sys.modules", {"nodejs": Mock(npm=mock_npm)}),
            patch("claude_agent_sdk._internal.cli_detection.platform.system", return_value="Linux"),
            patch("claude_agent_sdk._internal.cli_detection.Path.home", return_value=home),
        ):
            with patch.object(Path, "mkdir") as mock_mkdir:
                with (
                    patch.object(Path, "exists", return_value=True),
                    patch.object(Path, "is_file", return_value=True),
                ):
                    _attempt_auto_install()

                    # Verify mkdir was called
                    assert mock_mkdir.called

    def test_auto_install_generic_exception(self):
        """Test handling of unexpected exceptions during auto-install."""
        mock_npm = Mock()
        mock_npm.run = Mock(side_effect=RuntimeError("Unexpected error"))

        home = Path("/home/testuser")

        with (
            patch.dict("sys.modules", {"nodejs": Mock(npm=mock_npm)}),
            patch("claude_agent_sdk._internal.cli_detection.Path.home", return_value=home),
        ):
            with patch.object(Path, "mkdir"):
                with pytest.raises(ClaudeCodeNotFoundError) as exc_info:
                    _attempt_auto_install()

        error_msg = str(exc_info.value)
        assert "Auto-install failed" in error_msg
        assert "Unexpected error" in error_msg
