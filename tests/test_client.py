"""Tests for Claude SDK client functionality."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import anyio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    query,
)
from claude_agent_sdk.rendering.config import RendererConfig
from claude_agent_sdk.rendering.theme import Theme
from claude_agent_sdk.types import TextBlock


class TestQueryFunction:
    """Test the main query function."""

    def test_query_single_prompt(self):
        """Test query with a single prompt."""

        async def _test():
            with patch(
                "claude_agent_sdk._internal.client.InternalClient.process_query"
            ) as mock_process:
                # Mock the async generator
                async def mock_generator():
                    yield AssistantMessage(
                        content=[TextBlock(text="4")], model="claude-opus-4-1-20250805"
                    )

                mock_process.return_value = mock_generator()

                messages = []
                async for msg in query(prompt="What is 2+2?"):
                    messages.append(msg)

                assert len(messages) == 1
                assert isinstance(messages[0], AssistantMessage)
                assert messages[0].content[0].text == "4"

        anyio.run(_test)

    def test_query_with_options(self):
        """Test query with various options."""

        async def _test():
            with patch(
                "claude_agent_sdk._internal.client.InternalClient.process_query"
            ) as mock_process:

                async def mock_generator():
                    yield AssistantMessage(
                        content=[TextBlock(text="Hello!")],
                        model="claude-opus-4-1-20250805",
                    )

                mock_process.return_value = mock_generator()

                options = ClaudeAgentOptions(
                    allowed_tools=["Read", "Write"],
                    system_prompt="You are helpful",
                    permission_mode="acceptEdits",
                    max_turns=5,
                )

                messages = []
                async for msg in query(prompt="Hi", options=options):
                    messages.append(msg)

                # Verify process_query was called with correct prompt and options
                mock_process.assert_called_once()
                call_args = mock_process.call_args
                assert call_args[1]["prompt"] == "Hi"
                assert call_args[1]["options"] == options

        anyio.run(_test)

    def test_query_with_cwd(self):
        """Test query with custom working directory."""

        async def _test():
            with patch(
                "claude_agent_sdk._internal.client.SubprocessCLITransport"
            ) as mock_transport_class:
                mock_transport = AsyncMock()
                mock_transport_class.return_value = mock_transport

                # Mock the message stream
                async def mock_receive():
                    yield {
                        "type": "assistant",
                        "message": {
                            "role": "assistant",
                            "content": [{"type": "text", "text": "Done"}],
                            "model": "claude-opus-4-1-20250805",
                        },
                    }
                    yield {
                        "type": "result",
                        "subtype": "success",
                        "duration_ms": 1000,
                        "duration_api_ms": 800,
                        "is_error": False,
                        "num_turns": 1,
                        "session_id": "test-session",
                        "total_cost_usd": 0.001,
                    }

                mock_transport.read_messages = mock_receive
                mock_transport.connect = AsyncMock()
                mock_transport.close = AsyncMock()
                mock_transport.end_input = AsyncMock()
                mock_transport.write = AsyncMock()
                mock_transport.is_ready = Mock(return_value=True)

                options = ClaudeAgentOptions(cwd="/custom/path")
                messages = []
                async for msg in query(prompt="test", options=options):
                    messages.append(msg)

                # Verify transport was created with correct parameters
                mock_transport_class.assert_called_once()
                call_kwargs = mock_transport_class.call_args.kwargs
                assert call_kwargs["prompt"] == "test"
                assert call_kwargs["options"].cwd == "/custom/path"

        anyio.run(_test)


class TestClaudeSDKClientThemeIntegration:
    """Test ClaudeSDKClient integration with theme system."""

    def test_client_with_default_config(self):
        """Test that client uses default config when none provided."""

        async def _test():
            client = ClaudeSDKClient()

            # Should have loaded default config
            assert client.renderer_config is not None
            assert isinstance(client.renderer_config, RendererConfig)

            # Default config should have claude_code theme
            assert client.renderer_config.theme is not None
            assert isinstance(client.renderer_config.theme, Theme)

        anyio.run(_test)

    def test_client_with_custom_theme(self):
        """Test that client accepts custom theme via renderer_config."""

        async def _test():
            # Create custom config with gruvbox theme
            custom_config = RendererConfig(theme=Theme.gruvbox())
            client = ClaudeSDKClient(renderer_config=custom_config)

            # Should use provided config
            assert client.renderer_config is custom_config
            assert client.renderer_config.theme == Theme.gruvbox()

        anyio.run(_test)

    def test_client_with_colors_disabled(self):
        """Test that client respects color_enabled=False."""

        async def _test():
            # Create config with colors disabled
            custom_config = RendererConfig(color_enabled=False)
            client = ClaudeSDKClient(renderer_config=custom_config)

            # Should have colors disabled
            assert client.renderer_config.color_enabled is False

        anyio.run(_test)

    def test_client_config_file_loading(self):
        """Test that client loads config from file when available."""

        async def _test():
            # Create temporary config file
            with tempfile.TemporaryDirectory() as tmpdir:
                config_dir = Path(tmpdir) / ".claude-sdk"
                config_dir.mkdir(parents=True, exist_ok=True)
                config_file = config_dir / "config.json"

                # Write config with solarized_dark theme
                config_file.write_text(
                    '{"theme": "solarized_dark", "color_enabled": true, "show_cost": true}'
                )

                # Mock the config file path to use our temp directory
                with patch("claude_agent_sdk.rendering.config.Path.home") as mock_home:
                    mock_home.return_value = Path(tmpdir)

                    # Load defaults should pick up the config
                    config = RendererConfig.load_defaults()

                    # Should have loaded solarized_dark theme
                    assert config.theme == Theme.solarized_dark()
                    assert config.show_cost is True

        anyio.run(_test)

    def test_client_with_all_theme_presets(self):
        """Test that client works with all built-in theme presets."""

        async def _test():
            themes = [
                ("claude_code", Theme.claude_code_default()),
                ("solarized_dark", Theme.solarized_dark()),
                ("solarized_light", Theme.solarized_light()),
                ("gruvbox", Theme.gruvbox()),
                ("nord", Theme.nord()),
                ("monochrome", Theme.monochrome()),
                ("high_contrast", Theme.high_contrast()),
            ]

            for theme_name, theme_obj in themes:
                config = RendererConfig(theme=theme_obj)
                client = ClaudeSDKClient(renderer_config=config)

                # Should use the specified theme
                assert client.renderer_config.theme == theme_obj, f"Theme {theme_name} not properly set"

        anyio.run(_test)
