#!/usr/bin/env python3
"""Interactive demo of the Claude Agent SDK Pretty Printer.

This demo showcases all the rendering features added in Sprint 1:
- Simple display_message() usage
- Multiple handlers (console + file)
- Different render levels
- Custom configuration
- Real SDK integration with tool use

Run this script to see the pretty printer in action!
"""

from pathlib import Path
import sys

import anyio

from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.rendering import (
    MessageRenderer,
    ClaudeCodeFormatter,
    StreamHandler,
    FileHandler,
    RendererConfig,
    RenderLevel,
    display_message,
)


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


async def demo_1_simple_usage():
    """Demo 1: Simplest usage with display_message()."""
    print_section("DEMO 1: Simple Usage (display_message)")

    print("Using the convenience function - just one line of code!")
    print("Code: display_message(message)\n")

    async for message in query(prompt="Say hello in one sentence"):
        display_message(message)


async def demo_2_render_levels():
    """Demo 2: Different render levels."""
    print_section("DEMO 2: Render Levels (Controlling Verbosity)")

    levels = [
        (RenderLevel.MINIMAL, "MINIMAL - Only user/assistant text"),
        (RenderLevel.STANDARD, "STANDARD - + tool names/summaries (default)"),
        (RenderLevel.DETAILED, "DETAILED - + tool inputs/outputs"),
    ]

    for level, description in levels:
        print(f"\n--- {description} ---\n")

        renderer = MessageRenderer()
        config = RendererConfig(render_level=level)
        formatter = ClaudeCodeFormatter(config)
        handler = StreamHandler(formatter=formatter)
        renderer.add_handler(handler)

        # Query that requires tool use to show render level differences
        options = ClaudeAgentOptions(allowed_tools=["Read"])
        async for message in query(
            prompt="Read the first 5 lines of README.md and summarize the project in one sentence",
            options=options
        ):
            renderer.render(message)

        print()  # Extra spacing


async def demo_3_multi_handler():
    """Demo 3: Multiple handlers (console + file)."""
    print_section("DEMO 3: Multiple Destinations (Console + File)")

    # Create output file
    output_file = Path("demo_output.txt")
    print(f"Writing to both console AND file: {output_file.absolute()}\n")

    # Setup renderer with two handlers
    renderer = MessageRenderer()

    # Console: STANDARD level
    console_config = RendererConfig(render_level=RenderLevel.STANDARD)
    console_formatter = ClaudeCodeFormatter(console_config)
    console_handler = StreamHandler(formatter=console_formatter)
    renderer.add_handler(console_handler)

    # File: DETAILED level (more verbose in file)
    file_config = RendererConfig(render_level=RenderLevel.DETAILED)
    file_formatter = ClaudeCodeFormatter(file_config)
    file_handler = FileHandler(filepath=output_file, formatter=file_formatter)
    renderer.add_handler(file_handler)

    # Run query with tool use
    options = ClaudeAgentOptions(
        allowed_tools=["Read"],
        system_prompt="You are a helpful assistant.",
    )

    async for message in query(
        prompt="Read the README.md file and tell me what this project is about in one sentence.",
        options=options,
    ):
        renderer.render(message)

    print(f"\n✓ Detailed output saved to: {output_file.absolute()}")
    print(f"  Open it to see the DETAILED level with full tool inputs/outputs!")


async def demo_4_custom_config():
    """Demo 4: Custom configuration."""
    print_section("DEMO 4: Custom Configuration")

    print("Using custom settings:")
    print("  - Compact mode: True")
    print("  - Max text length: 300 characters")
    print("  - Custom UTF-8 bullet: ▸\n")

    config = RendererConfig(
        render_level=RenderLevel.STANDARD,
        compact_mode=True,
        max_text_length=300,
        bullet="▸",  # Custom bullet character
        show_metadata=False,
    )

    renderer = MessageRenderer()
    formatter = ClaudeCodeFormatter(config)
    handler = StreamHandler(formatter=formatter)
    renderer.add_handler(handler)

    async for message in query(
        prompt="Explain quantum computing in one paragraph."
    ):
        renderer.render(message)


async def demo_5_tool_use():
    """Demo 5: Tool use with pretty formatting."""
    print_section("DEMO 5: Tool Use with Pretty Formatting")

    print("Watch how tool calls and results are beautifully formatted!\n")
    print("Format:")
    print("  ● Tool(param: \"value\", number: 123)")
    print("    ⎿  Result line 1")
    print("       Result line 2\n")

    renderer = MessageRenderer()
    config = RendererConfig(render_level=RenderLevel.STANDARD)
    formatter = ClaudeCodeFormatter(config)
    handler = StreamHandler(formatter=formatter)
    renderer.add_handler(handler)

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"],
        system_prompt="You are a helpful assistant.",
    )

    async for message in query(
        prompt="List all Python files in the src/ directory and tell me how many there are.",
        options=options,
    ):
        renderer.render(message)


async def demo_6_utf8_characters():
    """Demo 6: UTF-8 character showcase."""
    print_section("DEMO 6: UTF-8 Character Showcase")

    print("The pretty printer uses Unicode characters for beautiful output:\n")
    print("  ● (U+25CF) - Bullet point for messages")
    print("  ⎿ (U+23BF) - Tree connector for indented content")
    print("  → (U+2192) - Arrow for navigation")
    print("  … (U+2026) - Ellipsis for truncation")
    print("  · (U+00B7) - Middle dot for list items\n")

    print("Let's see them in action:\n")

    renderer = MessageRenderer()
    formatter = ClaudeCodeFormatter()
    handler = StreamHandler(formatter=formatter)
    renderer.add_handler(handler)

    async for message in query(
        prompt="Say 'Hello from the pretty printer!' in one sentence."
    ):
        renderer.render(message)


async def demo_7_comparison():
    """Demo 7: Before vs After comparison."""
    print_section("DEMO 7: Before vs After")

    print("WITHOUT pretty printer (raw message):")
    print("-" * 70)

    # Collect all messages first
    messages = []
    async for message in query(prompt="What is Python? Answer in one sentence.", options=ClaudeAgentOptions(max_turns=1)):
        messages.append(message)

    # Show first message raw
    if messages:
        print(messages[0])
        print()

        print("-" * 70)
        print("\nWITH pretty printer (formatted):")
        print("-" * 70)
        display_message(messages[0])


async def main():
    """Run all demos."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║           Claude Agent SDK - Pretty Printer Demo                    ║
║                      Sprint 1 Features                              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

This demo showcases the new message rendering system that makes SDK
output beautiful and readable, matching the Claude Code CLI format.

Features demonstrated:
  1. Simple usage with display_message()
  2. Render levels (MINIMAL, STANDARD, DETAILED)
  3. Multiple handlers (console + file simultaneously)
  4. Custom configuration
  5. Tool use formatting
  6. UTF-8 character showcase
  7. Before/after comparison

Press Ctrl+C to skip any demo.
""")

    try:
        await demo_1_simple_usage()
        input("\nPress Enter to continue to Demo 2...")

        await demo_2_render_levels()
        input("\nPress Enter to continue to Demo 3...")

        await demo_3_multi_handler()
        input("\nPress Enter to continue to Demo 4...")

        await demo_4_custom_config()
        input("\nPress Enter to continue to Demo 5...")

        await demo_5_tool_use()
        input("\nPress Enter to continue to Demo 6...")

        await demo_6_utf8_characters()
        input("\nPress Enter to continue to Demo 7...")

        await demo_7_comparison()

        print_section("Demo Complete!")
        print("""
✓ All demos completed successfully!

Key Takeaways:
  1. Use display_message() for quick one-liners
  2. Use MessageRenderer + handlers for advanced control
  3. Configure RenderLevel to control verbosity
  4. Send output to multiple destinations (console, file, etc.)
  5. Customize UTF-8 characters and formatting options

Next Steps:
  - Check out examples/pretty_printer_basic.py for more examples
  - Read docs/rendering.md for complete documentation
  - Try creating your own custom formatters and handlers!

Thank you for trying the Claude Agent SDK Pretty Printer! 🎉
""")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    anyio.run(main)
