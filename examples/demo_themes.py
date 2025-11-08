#!/usr/bin/env python3
"""Demo showcasing all built-in theme presets.

This script demonstrates the visual appearance of all available themes
by rendering sample messages with each theme.

Usage:
    python examples/demo_themes.py [--theme THEME_NAME]

Examples:
    python examples/demo_themes.py                     # Show all themes
    python examples/demo_themes.py --theme gruvbox     # Show only Gruvbox
"""

import argparse
from claude_agent_sdk.rendering.theme import Theme
from claude_agent_sdk.rendering.ansi import AnsiEncoder
from claude_agent_sdk.rendering.config import RendererConfig


def demo_theme(theme_name: str, theme: Theme) -> None:
    """Display a themed demo of various message types."""
    encoder = AnsiEncoder()

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

    # Tool result
    tool_result_rule = theme.tool_result
    result_text = "  Result: Paris is the capital and largest city of France..."
    print(encoder.encode(result_text, tool_result_rule))

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
    args = parser.parse_args()

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

        demo_theme(theme_name, themes[theme_name])
    else:
        # Show all themes
        print("\n" + "=" * 70)
        print("  CLAUDE AGENT SDK - THEME SHOWCASE")
        print("=" * 70)

        for theme_name, theme in themes.items():
            demo_theme(theme_name, theme)

    return 0


if __name__ == "__main__":
    exit(main())
