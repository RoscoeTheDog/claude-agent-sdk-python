"""Tests for RendererConfig theme support and file loading (Story 1.3.3)."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from claude_agent_sdk.rendering.config import (
    RendererConfig,
    RenderLevel,
    _detect_color_depth,
    _is_tty,
    _merge_configs,
)
from claude_agent_sdk.rendering.theme import ColorDepth, StyleRule, Theme


class TestRendererConfigThemeFields:
    """Test that theme-related fields are properly added to RendererConfig."""

    def test_default_theme_field(self):
        """Theme field should default to claude_code_default."""
        config = RendererConfig()
        assert isinstance(config.theme, Theme)
        # Should be claude_code_default theme
        assert config.theme == Theme.claude_code_default()

    def test_custom_theme_field(self):
        """Should accept custom theme."""
        custom_theme = Theme(
            user_message=StyleRule(fg_color="blue"),
            assistant_message=StyleRule(fg_color="green"),
        )
        config = RendererConfig(theme=custom_theme)
        assert config.theme == custom_theme

    def test_color_enabled_default(self):
        """color_enabled should default to True (when TTY)."""
        with patch("sys.stdout.isatty", return_value=True):
            config = RendererConfig()
            assert config.color_enabled is True

    def test_color_enabled_false(self):
        """Should accept color_enabled=False."""
        config = RendererConfig(color_enabled=False)
        assert config.color_enabled is False

    def test_color_depth_auto_detect(self):
        """color_depth should auto-detect if None."""
        with (
            patch(
                "claude_agent_sdk.rendering.config.detect_color_depth"
            ) as mock_detect,
            patch("sys.stdout.isatty", return_value=True),
        ):
            mock_detect.return_value = ColorDepth.TRUECOLOR
            config = RendererConfig()
            assert config.color_depth == ColorDepth.TRUECOLOR
            mock_detect.assert_called_once()

    def test_color_depth_explicit(self):
        """Should accept explicit color_depth."""
        with patch("sys.stdout.isatty", return_value=True):
            config = RendererConfig(color_depth=ColorDepth.EXTENDED_256)
            assert config.color_depth == ColorDepth.EXTENDED_256

    def test_screen_reader_mode_default(self):
        """screen_reader_mode should default to False."""
        config = RendererConfig()
        assert config.screen_reader_mode is False

    def test_screen_reader_mode_true(self):
        """Should accept screen_reader_mode=True."""
        config = RendererConfig(screen_reader_mode=True)
        assert config.screen_reader_mode is True


class TestRendererConfigTTYDetection:
    """Test TTY detection and auto-disabling colors."""

    def test_colors_disabled_when_not_tty(self):
        """Colors should be disabled if not a TTY."""
        with patch("sys.stdout.isatty", return_value=False):
            config = RendererConfig()
            assert config.color_enabled is False
            assert config.color_depth == ColorDepth.NONE

    def test_colors_enabled_when_tty(self):
        """Colors should remain enabled if TTY."""
        with (
            patch("sys.stdout.isatty", return_value=True),
            patch(
                "claude_agent_sdk.rendering.config.detect_color_depth"
            ) as mock_detect,
        ):
            mock_detect.return_value = ColorDepth.TRUECOLOR
            config = RendererConfig()
            assert config.color_enabled is True
            assert config.color_depth == ColorDepth.TRUECOLOR

    def test_explicit_color_enabled_false_not_overridden(self):
        """Explicitly setting color_enabled=False should not be overridden."""
        with patch("sys.stdout.isatty", return_value=True):
            config = RendererConfig(color_enabled=False)
            assert config.color_enabled is False


class TestRendererConfigFromFile:
    """Test loading config from JSON files."""

    def test_from_file_basic_config(self, tmp_path):
        """Should load basic config from file."""
        config_file = tmp_path / "config.json"
        config_data = {
            "render_level": "DETAILED",
            "show_cost": True,
            "color_enabled": True,
        }
        config_file.write_text(json.dumps(config_data))

        with patch("sys.stdout.isatty", return_value=True):
            config = RendererConfig.from_file(config_file)
            assert config.render_level == RenderLevel.DETAILED
            assert config.show_cost is True
            assert config.color_enabled is True

    def test_from_file_with_theme_preset(self, tmp_path):
        """Should load theme from preset name."""
        config_file = tmp_path / "config.json"
        config_data = {
            "theme": "claude_code",
            "color_enabled": True,
        }
        config_file.write_text(json.dumps(config_data))

        config = RendererConfig.from_file(config_file)
        assert config.theme == Theme.claude_code_default()

    def test_from_file_with_custom_theme(self, tmp_path):
        """Should load custom theme from dict."""
        config_file = tmp_path / "config.json"
        theme_dict = {
            "user_message": {"fg_color": "blue", "bold": True},
            "assistant_message": {"fg_color": "green"},
        }
        config_data = {
            "theme": theme_dict,
            "color_enabled": True,
        }
        config_file.write_text(json.dumps(config_data))

        config = RendererConfig.from_file(config_file)
        assert config.theme.user_message.fg_color == "blue"
        assert config.theme.user_message.bold is True
        assert config.theme.assistant_message.fg_color == "green"

    def test_from_file_with_color_depth(self, tmp_path):
        """Should deserialize color_depth from string."""
        config_file = tmp_path / "config.json"
        config_data = {
            "color_depth": "EXTENDED_256",
        }
        config_file.write_text(json.dumps(config_data))

        with patch("sys.stdout.isatty", return_value=True):
            config = RendererConfig.from_file(config_file)
            assert config.color_depth == ColorDepth.EXTENDED_256

    def test_from_file_not_found(self, tmp_path):
        """Should raise FileNotFoundError if file doesn't exist."""
        config_file = tmp_path / "nonexistent.json"
        with pytest.raises(FileNotFoundError):
            RendererConfig.from_file(config_file)

    def test_from_file_invalid_json(self, tmp_path):
        """Should raise JSONDecodeError if file is not valid JSON."""
        config_file = tmp_path / "config.json"
        config_file.write_text("not valid json {")

        with pytest.raises(json.JSONDecodeError):
            RendererConfig.from_file(config_file)


class TestRendererConfigToFile:
    """Test saving config to JSON files."""

    def test_to_file_basic_config(self, tmp_path):
        """Should save config to file."""
        config_file = tmp_path / "config.json"
        config = RendererConfig(
            render_level=RenderLevel.DETAILED,
            show_cost=True,
            color_enabled=False,
        )

        config.to_file(config_file)

        assert config_file.exists()
        data = json.loads(config_file.read_text())
        assert data["render_level"] == "DETAILED"
        assert data["show_cost"] is True
        assert data["color_enabled"] is False

    def test_to_file_with_theme(self, tmp_path):
        """Should serialize theme to dict."""
        config_file = tmp_path / "config.json"
        theme = Theme(
            user_message=StyleRule(fg_color="blue", bold=True),
            assistant_message=StyleRule(fg_color="green"),
        )
        config = RendererConfig(theme=theme)

        config.to_file(config_file)

        data = json.loads(config_file.read_text())
        assert "theme" in data
        assert data["theme"]["user_message"]["fg_color"] == "blue"
        assert data["theme"]["user_message"]["bold"] is True
        assert data["theme"]["assistant_message"]["fg_color"] == "green"

    def test_to_file_with_color_depth(self, tmp_path):
        """Should serialize color_depth to string."""
        config_file = tmp_path / "config.json"
        with patch("sys.stdout.isatty", return_value=True):
            config = RendererConfig(color_depth=ColorDepth.EXTENDED_256)

        config.to_file(config_file)

        data = json.loads(config_file.read_text())
        assert data["color_depth"] == "EXTENDED_256"

    def test_to_file_creates_parent_dirs(self, tmp_path):
        """Should create parent directories if they don't exist."""
        config_file = tmp_path / "subdir" / "nested" / "config.json"
        config = RendererConfig()

        config.to_file(config_file)

        assert config_file.exists()
        assert config_file.parent.exists()


class TestRendererConfigLoadDefaults:
    """Test cascading config loading from multiple sources."""

    def test_load_defaults_no_configs(self):
        """Should use built-in defaults if no config files exist."""
        with (
            patch("pathlib.Path.home") as mock_home,
            patch("pathlib.Path.cwd") as mock_cwd,
        ):
            # Mock paths that don't exist
            mock_home.return_value = Path("/nonexistent/home")
            mock_cwd.return_value = Path("/nonexistent/project")

            config = RendererConfig.load_defaults()
            assert config.render_level == RenderLevel.STANDARD
            assert config.show_cost is False

    def test_load_defaults_user_config_only(self, tmp_path):
        """Should load user-level config."""
        user_config = tmp_path / "user" / ".claude-sdk" / "config.json"
        user_config.parent.mkdir(parents=True)
        user_config.write_text(
            json.dumps({"show_cost": True, "render_level": "DETAILED"})
        )

        with (
            patch("pathlib.Path.home", return_value=tmp_path / "user"),
            patch("pathlib.Path.cwd", return_value=tmp_path / "project"),
        ):
            config = RendererConfig.load_defaults()
            assert config.show_cost is True
            assert config.render_level == RenderLevel.DETAILED

    def test_load_defaults_project_config_only(self, tmp_path):
        """Should load project-level config."""
        project_config = tmp_path / "project" / ".claude-sdk" / "config.json"
        project_config.parent.mkdir(parents=True)
        project_config.write_text(
            json.dumps({"show_cost": False, "color_enabled": False})
        )

        with (
            patch("pathlib.Path.home", return_value=tmp_path / "user"),
            patch("pathlib.Path.cwd", return_value=tmp_path / "project"),
        ):
            config = RendererConfig.load_defaults()
            assert config.show_cost is False
            assert config.color_enabled is False

    def test_load_defaults_cascading_priority(self, tmp_path):
        """Project config should override user config."""
        user_config = tmp_path / "user" / ".claude-sdk" / "config.json"
        user_config.parent.mkdir(parents=True)
        user_config.write_text(
            json.dumps(
                {"show_cost": True, "render_level": "DETAILED", "color_enabled": True}
            )
        )

        project_config = tmp_path / "project" / ".claude-sdk" / "config.json"
        project_config.parent.mkdir(parents=True)
        project_config.write_text(
            json.dumps({"show_cost": False, "color_enabled": False})
        )

        with (
            patch("pathlib.Path.home", return_value=tmp_path / "user"),
            patch("pathlib.Path.cwd", return_value=tmp_path / "project"),
        ):
            config = RendererConfig.load_defaults()
            # Project config overrides
            assert config.show_cost is False
            assert config.color_enabled is False
            # User config values not overridden
            assert config.render_level == RenderLevel.DETAILED


class TestMergeConfigs:
    """Test config merging logic."""

    def test_merge_empty_base(self):
        """Merging with empty base should return override."""
        base = {}
        override = {"show_cost": True, "color_enabled": False}
        result = _merge_configs(base, override)
        assert result == override

    def test_merge_empty_override(self):
        """Merging with empty override should return base."""
        base = {"show_cost": True, "color_enabled": False}
        override = {}
        result = _merge_configs(base, override)
        assert result == base

    def test_merge_override_takes_precedence(self):
        """Override values should take precedence."""
        base = {"show_cost": True, "color_enabled": True, "render_level": "STANDARD"}
        override = {"show_cost": False, "color_enabled": False}
        result = _merge_configs(base, override)
        assert result["show_cost"] is False
        assert result["color_enabled"] is False
        assert result["render_level"] == "STANDARD"  # Not overridden

    def test_merge_does_not_modify_original(self):
        """Merging should not modify original dicts."""
        base = {"show_cost": True}
        override = {"color_enabled": False}
        _merge_configs(base, override)
        assert "color_enabled" not in base
        assert "show_cost" not in override


class TestDetectColorDepth:
    """Test color depth detection wrapper."""

    def test_detect_color_depth(self):
        """Should call detect_color_depth from ansi module."""
        with patch(
            "claude_agent_sdk.rendering.config.detect_color_depth"
        ) as mock_detect:
            mock_detect.return_value = ColorDepth.TRUECOLOR
            result = _detect_color_depth()
            assert result == ColorDepth.TRUECOLOR
            mock_detect.assert_called_once()


class TestIsTTY:
    """Test TTY detection."""

    def test_is_tty_true(self):
        """Should return True when stdout is a TTY."""
        with patch("sys.stdout.isatty", return_value=True):
            assert _is_tty() is True

    def test_is_tty_false(self):
        """Should return False when stdout is not a TTY."""
        with patch("sys.stdout.isatty", return_value=False):
            assert _is_tty() is False


class TestRendererConfigDeserialization:
    """Test deserialization edge cases."""

    def test_deserialize_render_level_from_string(self):
        """Should deserialize RenderLevel from string name."""
        data = {"render_level": "DETAILED"}
        config = RendererConfig._from_dict(data)
        assert config.render_level == RenderLevel.DETAILED

    def test_deserialize_render_level_from_int(self):
        """Should deserialize RenderLevel from integer value."""
        data = {"render_level": 2}  # DETAILED
        config = RendererConfig._from_dict(data)
        assert config.render_level == RenderLevel.DETAILED

    def test_deserialize_color_depth_from_string(self):
        """Should deserialize ColorDepth from string name."""
        data = {"color_depth": "BASIC_16"}
        with patch("sys.stdout.isatty", return_value=True):
            config = RendererConfig._from_dict(data)
            assert config.color_depth == ColorDepth.BASIC_16

    def test_deserialize_color_depth_from_int(self):
        """Should deserialize ColorDepth from integer value."""
        data = {"color_depth": 16}  # BASIC_16
        with patch("sys.stdout.isatty", return_value=True):
            config = RendererConfig._from_dict(data)
            assert config.color_depth == ColorDepth.BASIC_16

    def test_deserialize_color_depth_null(self):
        """Should handle null color_depth (auto-detect)."""
        data = {"color_depth": None}
        with (
            patch(
                "claude_agent_sdk.rendering.config.detect_color_depth"
            ) as mock_detect,
            patch("sys.stdout.isatty", return_value=True),
        ):
            mock_detect.return_value = ColorDepth.TRUECOLOR
            config = RendererConfig._from_dict(data)
            # Should auto-detect in __post_init__
            assert config.color_depth == ColorDepth.TRUECOLOR


class TestRendererConfigSerialization:
    """Test serialization to dict."""

    def test_serialize_basic_config(self):
        """Should serialize basic config to dict."""
        config = RendererConfig(
            render_level=RenderLevel.DETAILED,
            show_cost=True,
        )
        data = config._to_dict()
        assert data["render_level"] == "DETAILED"
        assert data["show_cost"] is True

    def test_serialize_theme(self):
        """Should serialize theme to dict."""
        theme = Theme(user_message=StyleRule(fg_color="blue"))
        config = RendererConfig(theme=theme)
        data = config._to_dict()
        assert "theme" in data
        assert isinstance(data["theme"], dict)
        assert data["theme"]["user_message"]["fg_color"] == "blue"

    def test_serialize_color_depth(self):
        """Should serialize color_depth to string name."""
        with patch("sys.stdout.isatty", return_value=True):
            config = RendererConfig(color_depth=ColorDepth.EXTENDED_256)
        data = config._to_dict()
        assert data["color_depth"] == "EXTENDED_256"

    def test_serialize_color_depth_null(self):
        """Should serialize None color_depth as null."""
        config = RendererConfig(color_depth=None, color_enabled=False)
        data = config._to_dict()
        # Note: in __post_init__, None gets converted, but we're testing the serialization
        assert "color_depth" in data


class TestRendererConfigRoundTrip:
    """Test serialization -> deserialization round-trip."""

    def test_round_trip_basic_config(self, tmp_path):
        """Config should survive save -> load round-trip."""
        config_file = tmp_path / "config.json"
        original_config = RendererConfig(
            render_level=RenderLevel.DETAILED,
            show_cost=True,
            color_enabled=False,
        )

        original_config.to_file(config_file)
        loaded_config = RendererConfig.from_file(config_file)

        assert loaded_config.render_level == original_config.render_level
        assert loaded_config.show_cost == original_config.show_cost
        assert loaded_config.color_enabled == original_config.color_enabled

    def test_round_trip_with_theme(self, tmp_path):
        """Theme should survive save -> load round-trip."""
        config_file = tmp_path / "config.json"
        theme = Theme(
            user_message=StyleRule(fg_color="blue", bold=True),
            assistant_message=StyleRule(fg_color="green", italic=True),
        )
        original_config = RendererConfig(theme=theme)

        original_config.to_file(config_file)
        loaded_config = RendererConfig.from_file(config_file)

        assert loaded_config.theme.user_message.fg_color == "blue"
        assert loaded_config.theme.user_message.bold is True
        assert loaded_config.theme.assistant_message.fg_color == "green"
        assert loaded_config.theme.assistant_message.italic is True
