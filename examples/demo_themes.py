#!/usr/bin/env python3
"""Demo showcasing all built-in theme presets.

This comprehensive demo demonstrates:
- All 7 built-in themes side-by-side
- Different message types (user, assistant, system)
- Tool calls and results (success and error)
- All semantic categories (error, warning, success, info)
- Color depth degradation simulation
- Interactive theme switcher
- Color and no-color modes

Usage:
    python examples/demo_themes.py                      # Show all themes
    python examples/demo_themes.py --theme gruvbox      # Show only Gruvbox
    python examples/demo_themes.py --no-color           # Disable colors
    python examples/demo_themes.py --interactive        # Interactive theme switcher
    python examples/demo_themes.py --depth 256          # Force 256-color mode
"""

import argparse
import io
import sys

# Set up UTF-8 output for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
from claude_agent_sdk.rendering.ansi import AnsiEncoder
from claude_agent_sdk.rendering.config import RendererConfig
from claude_agent_sdk.rendering.formatters import ClaudeCodeFormatter
from claude_agent_sdk.rendering.theme import ColorDepth, Theme
from claude_agent_sdk.types import (
    AssistantMessage,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolUseBlock,
    UserMessage,
)


def demo_theme_basic(
    theme_name: str, theme: Theme, color_depth: ColorDepth | None = None
) -> None:
    """Display a basic themed demo of various message types."""
    encoder = AnsiEncoder(color_depth=color_depth)

    # Header
    header_rule = theme.bullet
    header_text = f"\n{'=' * 70}\n  Theme: {theme_name.upper()}\n{'=' * 70}"
    print(encoder.encode(header_text, header_rule))

    # User message
    user_rule = theme.user_message
    user_text = "\n  User: What is the capital of France?"
    print(encoder.encode(user_text, user_rule))

    # Assistant message
    assistant_rule = theme.assistant_message
    assistant_text = "  Assistant: The capital of France is Paris."
    print(encoder.encode(assistant_text, assistant_rule))

    # Tool use
    tool_use_rule = theme.tool_use
    tool_text = "\n  Tool: WebSearch(query='Paris France')"
    print(encoder.encode(tool_text, tool_use_rule))

    # Tool result (success)
    tool_result_rule = theme.tool_result
    result_text = "  Result: Paris is the capital and largest city of France..."
    print(encoder.encode(result_text, tool_result_rule))

    # Tool error
    tool_error_rule = theme.tool_error
    error_result_text = "  Tool Error: API connection failed"
    print(encoder.encode(error_result_text, tool_error_rule))

    # Semantic categories
    error_rule = theme.error
    error_text = "\n  Error: Connection timeout"
    print(encoder.encode(error_text, error_rule))

    warning_rule = theme.warning
    warning_text = "  Warning: API rate limit approaching"
    print(encoder.encode(warning_text, warning_rule))

    success_rule = theme.success
    success_text = "  Success: Task completed successfully"
    print(encoder.encode(success_text, success_rule))

    info_rule = theme.info
    info_text = "  Info: Processing 5 items..."
    print(encoder.encode(info_text, info_rule))

    # Code
    code_rule = theme.code_block
    code_text = "\n  Code: def hello(): return 'world'"
    print(encoder.encode(code_text, code_rule))

    # Thinking
    thinking_rule = theme.thinking
    thinking_text = "  Thinking: Considering multiple approaches..."
    print(encoder.encode(thinking_text, thinking_rule))

    # Metadata
    metadata_rule = theme.metadata
    metadata_text = "  Metadata: Cost: $0.05 | Tokens: 1234"
    print(encoder.encode(metadata_text, metadata_rule))

    print()


def demo_theme_realistic(
    theme_name: str,
    theme: Theme,
    color_enabled: bool = True,
    color_depth: ColorDepth | None = None,
) -> None:
    """Display a realistic demo using actual message formatting."""
    config = RendererConfig(
        theme=theme,
        color_enabled=color_enabled,
        color_depth=color_depth,
        render_level=2,  # Full detail
        show_cost=True,
    )
    formatter = ClaudeCodeFormatter(config)

    # Header
    encoder = AnsiEncoder(color_depth=color_depth)
    header_rule = theme.bullet
    header_text = (
        f"\n{'=' * 70}\n  Theme: {theme_name.upper()} (Realistic Rendering)\n{'=' * 70}"
    )
    if color_enabled:
        print(encoder.encode(header_text, header_rule))
    else:
        print(header_text)

    # User message
    user_msg = UserMessage(content="Write a Python function to calculate factorial")
    print(formatter.format_user_message(user_msg))

    # Assistant message with tool use
    tool_use = ToolUseBlock(
        id="toolu_01A",
        name="Write",
        input={
            "file_path": "/tmp/factorial.py",
            "content": "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)",
        },
    )
    assistant_msg = AssistantMessage(
        content=[
            TextBlock(text="I'll create a recursive factorial function:"),
            tool_use,
        ],
        model="claude-sonnet-4-5-20250929",
    )
    print(formatter.format_assistant_message(assistant_msg))

    # System message
    system_msg = SystemMessage(
        subtype="test", data={"message": "Function created successfully"}
    )
    print(formatter.format_system_message(system_msg))

    # Result message
    result_msg = ResultMessage(
        subtype="completion",
        duration_ms=1234,
        duration_api_ms=1100,
        is_error=False,
        num_turns=1,
        session_id="demo123",
        total_cost_usd=0.05,
    )
    print(formatter.format_result_message(result_msg))

    print()


def demo_color_depth_degradation(theme_name: str, theme: Theme) -> None:
    """Show how a theme looks at different color depths."""
    depths = [
        (ColorDepth.TRUECOLOR, "Truecolor (24-bit RGB)"),
        (ColorDepth.EXTENDED_256, "256 colors"),
        (ColorDepth.BASIC_16, "16 colors"),
        (ColorDepth.NONE, "No colors"),
    ]

    print(f"\n{'=' * 70}")
    print(f"  Theme: {theme_name.upper()} - Color Depth Degradation")
    print("=" * 70)

    for depth, description in depths:
        encoder = AnsiEncoder(color_depth=depth)

        # Show depth label
        print(f"\n  [{description}]")

        # Sample with various semantic categories
        error_text = "  Error: Connection failed"
        print(encoder.encode(error_text, theme.error))

        success_text = "  Success: Operation completed"
        print(encoder.encode(success_text, theme.success))

        tool_text = "  Tool: Read(file='test.py')"
        print(encoder.encode(tool_text, theme.tool_use))

    print()


def interactive_mode():
    """Interactive theme switcher."""
    themes = {
        "1": ("claude_code_default", Theme.claude_code_default()),
        "2": ("solarized_dark", Theme.solarized_dark()),
        "3": ("solarized_light", Theme.solarized_light()),
        "4": ("gruvbox", Theme.gruvbox()),
        "5": ("nord", Theme.nord()),
        "6": ("monochrome", Theme.monochrome()),
        "7": ("high_contrast", Theme.high_contrast()),
    }

    while True:
        print("\n" + "=" * 70)
        print("  INTERACTIVE THEME SWITCHER")
        print("=" * 70)
        print("\nAvailable themes:")
        for key, (name, _) in themes.items():
            print(f"  {key}. {name}")
        print("  q. Quit")

        choice = input("\nSelect a theme (1-7) or 'q' to quit: ").strip()

        if choice.lower() == "q":
            print("Goodbye!")
            break

        if choice in themes:
            theme_name, theme = themes[choice]
            demo_theme_realistic(theme_name, theme)
        else:
            print("Invalid choice. Please try again.")


def main():
    parser = argparse.ArgumentParser(
        description="Demo all built-in theme presets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--theme",
        type=str,
        help="Show only this theme (e.g., gruvbox, nord, solarized_dark)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colors (demonstrate no-color mode)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Launch interactive theme switcher",
    )
    parser.add_argument(
        "--depth",
        type=str,
        choices=["16", "256", "truecolor", "none"],
        help="Force specific color depth (e.g., 256 for 256-color mode)",
    )
    parser.add_argument(
        "--degradation",
        action="store_true",
        help="Show color depth degradation for all themes",
    )
    parser.add_argument(
        "--realistic",
        action="store_true",
        help="Use realistic message formatting instead of basic demo",
    )
    args = parser.parse_args()

    # Interactive mode
    if args.interactive:
        interactive_mode()
        return 0

    # Determine color depth
    color_depth = None
    if args.depth:
        depth_map = {
            "16": ColorDepth.BASIC_16,
            "256": ColorDepth.EXTENDED_256,
            "truecolor": ColorDepth.TRUECOLOR,
            "none": ColorDepth.NONE,
        }
        color_depth = depth_map[args.depth]

    # Available themes
    themes = {
        "claude_code_default": Theme.claude_code_default(),
        "solarized_dark": Theme.solarized_dark(),
        "solarized_light": Theme.solarized_light(),
        "gruvbox": Theme.gruvbox(),
        "nord": Theme.nord(),
        "monochrome": Theme.monochrome(),
        "high_contrast": Theme.high_contrast(),
    }

    if args.theme:
        # Show only the specified theme
        theme_name = args.theme.lower()
        if theme_name not in themes:
            print(f"Error: Unknown theme '{theme_name}'")
            print(f"Available themes: {', '.join(sorted(themes.keys()))}")
            return 1

        theme = themes[theme_name]

        if args.degradation:
            demo_color_depth_degradation(theme_name, theme)
        elif args.realistic:
            demo_theme_realistic(
                theme_name,
                theme,
                color_enabled=not args.no_color,
                color_depth=color_depth,
            )
        else:
            demo_theme_basic(theme_name, theme, color_depth=color_depth)
    else:
        # Show all themes
        print("\n" + "=" * 70)
        print("  CLAUDE AGENT SDK - THEME SHOWCASE")
        print("=" * 70)

        if args.degradation:
            for theme_name, theme in themes.items():
                demo_color_depth_degradation(theme_name, theme)
        elif args.realistic:
            for theme_name, theme in themes.items():
                demo_theme_realistic(
                    theme_name,
                    theme,
                    color_enabled=not args.no_color,
                    color_depth=color_depth,
                )
        else:
            for theme_name, theme in themes.items():
                demo_theme_basic(theme_name, theme, color_depth=color_depth)

    return 0


if __name__ == "__main__":
    sys.exit(main())
