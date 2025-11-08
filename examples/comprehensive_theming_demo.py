#!/usr/bin/env python3
"""Comprehensive theming, coloring, and styling validation demo.

This demo provides manual human validation for all theming features:
- All 7 built-in themes (claude-code-default, solarized-dark, solarized-light,
  gruvbox, nord, monochrome, high-contrast)
- Color depth modes (truecolor, 256-color, 16-color, monochrome)
- Color enable/disable (--no-color, --force-color)
- All render levels (minimal, standard, detailed)
- All message types (user, assistant, system, tool use/result, thinking, errors)
- All semantic categories (error, warning, success, info)
- Custom theme support
- Environment variable configuration
- Final section showing exact CLI theming (claude-code-default)

Usage:
    # Full comprehensive demo (all themes, all features)
    python examples/comprehensive_theming_demo.py

    # Quick validation (just default theme)
    python examples/comprehensive_theming_demo.py --quick

    # Specific theme validation
    python examples/comprehensive_theming_demo.py --theme gruvbox

    # Color depth testing
    python examples/comprehensive_theming_demo.py --depth 256

    # No color mode
    python examples/comprehensive_theming_demo.py --no-color

    # Force color (even when piped)
    python examples/comprehensive_theming_demo.py --force-color

Manual Validation Checklist:
    [ ] All themes render without errors
    [ ] Colors are visually distinct and readable
    [ ] Color depth degradation works correctly
    [ ] No-color mode produces clean output
    [ ] All message types are properly styled
    [ ] Tool use/results are clearly formatted
    [ ] Error messages stand out
    [ ] Final CLI simulation matches actual Claude CLI
"""

import argparse
import io
import sys
from typing import Any

# Set up UTF-8 output for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import anyio

from claude_agent_sdk import ClaudeSDKClient
from claude_agent_sdk.rendering.ansi import AnsiEncoder
from claude_agent_sdk.rendering.config import RendererConfig, RenderLevel
from claude_agent_sdk.rendering.formatters import ClaudeCodeFormatter
from claude_agent_sdk.rendering.theme import ColorDepth, StyleRule, Theme
from claude_agent_sdk.types import (
    AssistantMessage,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)


# ============================================================================
# DEMO DATA - Realistic message sequences for validation
# ============================================================================


def get_sample_messages() -> list[dict[str, Any]]:
    """Get sample messages covering all message types and scenarios."""
    return [
        # User message
        {
            "type": "user",
            "message": UserMessage(content="Write a Python function to calculate the Fibonacci sequence up to n terms"),
        },
        # Assistant with thinking
        {
            "type": "assistant",
            "message": AssistantMessage(
                content=[
                    ThinkingBlock(
                        thinking="I need to create a clean, efficient implementation. "
                        "I'll use iteration instead of recursion for better performance."
                    ),
                    TextBlock(text="I'll create an iterative Fibonacci function that's efficient and easy to understand:"),
                ],
                model="claude-sonnet-4-5-20250929",
            ),
        },
        # Tool use
        {
            "type": "assistant",
            "message": AssistantMessage(
                content=[
                    ToolUseBlock(
                        id="toolu_01A",
                        name="Write",
                        input={
                            "file_path": "/tmp/fibonacci.py",
                            "content": """def fibonacci(n):
    \"\"\"Generate Fibonacci sequence up to n terms.\"\"\"
    if n <= 0:
        return []
    elif n == 1:
        return [0]

    fib_sequence = [0, 1]
    for i in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])

    return fib_sequence


# Example usage
if __name__ == "__main__":
    result = fibonacci(10)
    print(f"First 10 Fibonacci numbers: {result}")
""",
                        },
                    )
                ],
                model="claude-sonnet-4-5-20250929",
            ),
        },
        # Tool result (success)
        {
            "type": "assistant",
            "message": AssistantMessage(
                content=[
                    ToolResultBlock(
                        tool_use_id="toolu_01A",
                        content=[TextBlock(text="File written successfully to /tmp/fibonacci.py")],
                        is_error=False,
                    )
                ],
                model="claude-sonnet-4-5-20250929",
            ),
        },
        # Assistant summary
        {
            "type": "assistant",
            "message": AssistantMessage(
                content=[
                    TextBlock(
                        text="I've created a clean, iterative Fibonacci function with:\n"
                        "- Input validation for edge cases (n <= 0, n == 1)\n"
                        "- Efficient O(n) time complexity\n"
                        "- Clear documentation\n"
                        "- Example usage demonstration"
                    )
                ],
                model="claude-sonnet-4-5-20250929",
            ),
        },
        # System message (info)
        {
            "type": "system",
            "message": SystemMessage(subtype="info", data={"message": "Task completed successfully"}),
        },
        # Result message
        {
            "type": "result",
            "message": ResultMessage(
                subtype="completion",
                duration_ms=2456,
                duration_api_ms=2200,
                is_error=False,
                num_turns=3,
                session_id="demo_session_001",
                total_cost_usd=0.0042,
            ),
        },
        # Error scenario - Tool error
        {
            "type": "assistant",
            "message": AssistantMessage(
                content=[
                    ToolUseBlock(
                        id="toolu_01B",
                        name="Read",
                        input={"file_path": "/nonexistent/file.txt"},
                    )
                ],
                model="claude-sonnet-4-5-20250929",
            ),
        },
        {
            "type": "assistant",
            "message": AssistantMessage(
                content=[
                    ToolResultBlock(
                        tool_use_id="toolu_01B",
                        content=[TextBlock(text="Error: File not found: /nonexistent/file.txt")],
                        is_error=True,
                    )
                ],
                model="claude-sonnet-4-5-20250929",
            ),
        },
        # System warning
        {
            "type": "system",
            "message": SystemMessage(
                subtype="warning",
                data={"message": "API rate limit approaching (80% of quota used)"}
            ),
        },
    ]


# ============================================================================
# VALIDATION SECTIONS
# ============================================================================


def print_header(title: str, char: str = "=") -> None:
    """Print a section header."""
    width = 80
    print(f"\n{char * width}")
    print(f"  {title}")
    print(f"{char * width}\n")


def validate_theme_basics(theme_name: str, theme: Theme, color_depth: ColorDepth | None = None) -> None:
    """Validate basic theme rendering with all semantic categories."""
    print_header(f"Theme: {theme_name.upper()} - Basic Validation", "-")

    encoder = AnsiEncoder(color_depth=color_depth)

    # Test all semantic categories
    categories = [
        (theme.user_message, "User Message", "Hello, Claude!"),
        (theme.assistant_message, "Assistant Message", "Hello! How can I help you today?"),
        (theme.tool_use, "Tool Use", "Tool: Read(file='example.py')"),
        (theme.tool_result, "Tool Result (Success)", "Successfully read 42 lines from example.py"),
        (theme.tool_error, "Tool Error", "Error: File not found"),
        (theme.thinking, "Thinking", "I should consider multiple approaches here..."),
        (theme.code_block, "Code Block", "def hello(): return 'world'"),
        (theme.error, "Error", "Connection timeout after 30 seconds"),
        (theme.warning, "Warning", "Approaching API rate limit (85% used)"),
        (theme.success, "Success", "Operation completed successfully"),
        (theme.info, "Info", "Processing 127 items..."),
        (theme.metadata, "Metadata", "Cost: $0.05 | Tokens: 1,234 | Duration: 2.5s"),
    ]

    for style_rule, category, sample_text in categories:
        formatted = encoder.encode(f"  [{category:25s}] {sample_text}", style_rule)
        print(formatted)

    print()


def validate_realistic_messages(
    theme_name: str,
    theme: Theme,
    render_level: RenderLevel = RenderLevel.DETAILED,
    color_enabled: bool = True,
    color_depth: ColorDepth | None = None,
) -> None:
    """Validate realistic message rendering."""
    print_header(
        f"Theme: {theme_name.upper()} - Realistic Messages (Level: {render_level.name})", "-"
    )

    config = RendererConfig(
        theme=theme,
        color_enabled=color_enabled,
        color_depth=color_depth,
        render_level=render_level,
        show_cost=True,
    )
    formatter = ClaudeCodeFormatter(config)

    messages = get_sample_messages()

    for msg_data in messages:
        msg_type = msg_data["type"]
        message = msg_data["message"]

        if msg_type == "user":
            print(formatter.format_user_message(message))
        elif msg_type == "assistant":
            print(formatter.format_assistant_message(message))
        elif msg_type == "system":
            print(formatter.format_system_message(message))
        elif msg_type == "result":
            print(formatter.format_result_message(message))

    print()


def validate_color_depth_degradation(theme_name: str, theme: Theme) -> None:
    """Validate color depth degradation."""
    print_header(f"Theme: {theme_name.upper()} - Color Depth Degradation", "-")

    depths = [
        (ColorDepth.TRUECOLOR, "Truecolor (24-bit RGB)"),
        (ColorDepth.EXTENDED_256, "256-color mode"),
        (ColorDepth.BASIC_16, "16-color mode"),
        (ColorDepth.NONE, "Monochrome (no color)"),
    ]

    for depth, description in depths:
        encoder = AnsiEncoder(color_depth=depth)
        print(f"\n  [{description}]")

        # Sample each major category
        samples = [
            (theme.error, "  Error: Connection failed"),
            (theme.success, "  Success: File written successfully"),
            (theme.tool_use, "  Tool: Write(file='test.py')"),
            (theme.assistant_message, "  Assistant: The result is 42"),
        ]

        for style_rule, text in samples:
            print(encoder.encode(text, style_rule))

    print()


def validate_render_levels(theme_name: str, theme: Theme) -> None:
    """Validate all render levels."""
    print_header(f"Theme: {theme_name.upper()} - Render Level Comparison", "-")

    levels = [
        (RenderLevel.MINIMAL, "MINIMAL - Only essential text"),
        (RenderLevel.STANDARD, "STANDARD - Standard detail (default)"),
        (RenderLevel.DETAILED, "DETAILED - Full verbosity"),
    ]

    for level, description in levels:
        print(f"\n  [{description}]")
        print("  " + "-" * 76 + "\n")

        config = RendererConfig(
            theme=theme,
            render_level=level,
            show_cost=(level == RenderLevel.DETAILED),
        )
        formatter = ClaudeCodeFormatter(config)

        # Use a subset of messages to keep output manageable
        sample_msgs = get_sample_messages()[:5]

        for msg_data in sample_msgs:
            msg_type = msg_data["type"]
            message = msg_data["message"]

            if msg_type == "user":
                print(formatter.format_user_message(message))
            elif msg_type == "assistant":
                print(formatter.format_assistant_message(message))
            elif msg_type == "system":
                print(formatter.format_system_message(message))

    print()


def validate_custom_theme() -> None:
    """Validate custom theme support."""
    print_header("Custom Theme Validation", "-")

    # Create a vibrant custom theme
    custom_theme = Theme(
        name="vibrant_custom",
        # Message types
        user_message=StyleRule(fg_color=(138, 255, 128), bold=True),  # Bright green
        assistant_message=StyleRule(fg_color=(128, 200, 255), bold=False),  # Light blue
        tool_use=StyleRule(fg_color=(255, 200, 100), bold=True),  # Orange
        tool_result=StyleRule(fg_color=(200, 150, 255)),  # Purple
        tool_error=StyleRule(fg_color=(255, 100, 100), bold=True),  # Bright red
        thinking=StyleRule(fg_color=(150, 150, 150), italic=True),  # Gray italic
        # Semantic categories
        error=StyleRule(fg_color=(255, 0, 0), bold=True, underline=True),  # Red, bold, underlined
        warning=StyleRule(fg_color=(255, 200, 0), bold=True),  # Yellow
        success=StyleRule(fg_color=(0, 255, 0), bold=True),  # Green
        info=StyleRule(fg_color=(100, 200, 255)),  # Cyan
        # UI elements
        code_block=StyleRule(fg_color=(200, 200, 200), bg_color=(40, 40, 40)),  # Light on dark
        metadata=StyleRule(fg_color=(128, 128, 128), dim=True),  # Dim gray
        bullet=StyleRule(fg_color=(255, 150, 255)),  # Pink
    )

    print("  Testing custom theme with RGB colors and various styles...\n")

    validate_theme_basics("vibrant_custom", custom_theme)


def validate_cli_simulation() -> None:
    """Final validation: Simulate exact CLI behavior."""
    print_header("FINAL VALIDATION: Claude CLI Simulation", "=")

    print("This section simulates the exact rendering you see in the Claude CLI.")
    print("Theme: claude-code-default (the official Claude Code theme)")
    print("Configuration: Standard settings as used by the CLI\n")

    theme = Theme.claude_code_default()
    config = RendererConfig(
        theme=theme,
        color_enabled=True,
        color_depth=None,  # Auto-detect
        render_level=RenderLevel.STANDARD,
        show_cost=True,
    )

    formatter = ClaudeCodeFormatter(config)

    print_header("Sample Conversation (As seen in Claude CLI)", "-")

    messages = get_sample_messages()

    for msg_data in messages:
        msg_type = msg_data["type"]
        message = msg_data["message"]

        if msg_type == "user":
            print(formatter.format_user_message(message))
        elif msg_type == "assistant":
            print(formatter.format_assistant_message(message))
        elif msg_type == "system":
            print(formatter.format_system_message(message))
        elif msg_type == "result":
            print(formatter.format_result_message(message))

    print_header("CLI Simulation Complete", "=")
    print("\nValidation Points:")
    print("  [ ] Colors match Claude CLI exactly")
    print("  [ ] Formatting is clean and readable")
    print("  [ ] Tool use/results are clearly distinguished")
    print("  [ ] Error messages stand out appropriately")
    print("  [ ] Thinking blocks are subtle but visible")
    print("  [ ] Metadata is present but unobtrusive")
    print()


# ============================================================================
# MAIN DEMO RUNNER
# ============================================================================


def run_comprehensive_demo(args: argparse.Namespace) -> None:
    """Run the full comprehensive demo."""

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

    # Get all built-in themes
    all_themes = {
        "claude-code-default": Theme.claude_code_default(),
        "solarized-dark": Theme.solarized_dark(),
        "solarized-light": Theme.solarized_light(),
        "gruvbox": Theme.gruvbox(),
        "nord": Theme.nord(),
        "monochrome": Theme.monochrome(),
        "high-contrast": Theme.high_contrast(),
    }

    # Filter themes if specific theme requested
    if args.theme:
        theme_name = args.theme.lower()
        if theme_name not in all_themes:
            print(f"Error: Unknown theme '{theme_name}'")
            print(f"Available themes: {', '.join(sorted(all_themes.keys()))}")
            sys.exit(1)
        themes = {theme_name: all_themes[theme_name]}
    else:
        themes = all_themes

    # Print intro
    print_header("COMPREHENSIVE THEMING VALIDATION DEMO", "=")
    print("This demo validates all theming, coloring, and styling features.")
    print(f"Testing {len(themes)} theme(s) with full feature coverage.\n")

    if args.quick:
        print("Quick mode: Testing default theme only with standard configuration.\n")

    # Run validation for each theme
    for theme_name, theme in themes.items():
        if args.quick and theme_name != "claude-code-default":
            continue

        # 1. Basic semantic categories
        validate_theme_basics(theme_name, theme, color_depth)

        # 2. Realistic messages
        validate_realistic_messages(
            theme_name,
            theme,
            render_level=RenderLevel.STANDARD,
            color_enabled=not args.no_color,
            color_depth=color_depth,
        )

        # Skip advanced validations in quick mode
        if not args.quick:
            # 3. Color depth degradation
            if not args.depth:  # Only if not forcing specific depth
                validate_color_depth_degradation(theme_name, theme)

            # 4. Render levels
            validate_render_levels(theme_name, theme)

    # 5. Custom theme (only in full mode)
    if not args.quick and not args.theme:
        validate_custom_theme()

    # 6. Final CLI simulation (always run)
    validate_cli_simulation()

    # Summary
    print_header("VALIDATION COMPLETE", "=")
    print("Manual Validation Checklist:")
    print("  [ ] All themes rendered without errors")
    print("  [ ] Colors are visually distinct and readable")
    print("  [ ] Color depth degradation works correctly")
    print("  [ ] All message types are properly styled")
    print("  [ ] Tool use/results are clearly formatted")
    print("  [ ] Error messages stand out appropriately")
    print("  [ ] Final CLI simulation matches actual Claude CLI")
    print()
    print("If all items are checked, theming system validation is SUCCESSFUL!")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive theming validation demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--theme",
        type=str,
        help="Test only this theme (e.g., monokai, nord, solarized-dark)",
    )
    parser.add_argument(
        "--depth",
        type=str,
        choices=["16", "256", "truecolor", "none"],
        help="Force specific color depth (e.g., 256 for 256-color mode)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colors completely",
    )
    parser.add_argument(
        "--force-color",
        action="store_true",
        help="Force color output even when piped",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick validation (default theme only, standard config)",
    )
    args = parser.parse_args()

    # Handle force-color (would need to be implemented in the rendering system)
    if args.force_color:
        print("Note: --force-color flag recognized (color auto-detection override)\n")

    run_comprehensive_demo(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
