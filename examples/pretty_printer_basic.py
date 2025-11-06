#!/usr/bin/env python3
"""Pretty printer basic example for Claude Code SDK.

This example demonstrates how to use the rendering module to display
SDK messages in various formats (console and file output).
"""

from pathlib import Path

import anyio

from claude_agent_sdk import ClaudeAgentOptions, query
from claude_agent_sdk.rendering import (
    ClaudeCodeFormatter,
    FileHandler,
    MessageRenderer,
    RendererConfig,
    RenderLevel,
    StreamHandler,
    display_message,
)


async def simple_example():
    """Simple example using display_message() convenience function."""
    print("=== Simple Example (display_message) ===\n")

    async for message in query(prompt="What is 2 + 2?"):
        # Use convenience function for quick rendering
        display_message(message)


async def multi_handler_example():
    """Example with multiple handlers (console + file)."""
    print("\n=== Multi-Handler Example (Console + File) ===\n")

    # Create output file in current directory
    output_file = Path("pretty_printer_output.txt")

    # Setup renderer with multiple handlers
    renderer = MessageRenderer()

    # Console handler with STANDARD level (shows tool names, summaries)
    console_config = RendererConfig(render_level=RenderLevel.STANDARD)
    console_formatter = ClaudeCodeFormatter(console_config)
    console_handler = StreamHandler(formatter=console_formatter)
    renderer.add_handler(console_handler)

    # File handler with DETAILED level (shows tool inputs/outputs)
    file_config = RendererConfig(render_level=RenderLevel.DETAILED)
    file_formatter = ClaudeCodeFormatter(file_config)
    file_handler = FileHandler(filepath=output_file, formatter=file_formatter)
    renderer.add_handler(file_handler)

    # Run query
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"],
        system_prompt="You are a helpful assistant.",
    )

    async for message in query(
        prompt="List all Python files in the src/ directory",
        options=options,
    ):
        # Render to both console and file
        renderer.render(message)

    print(f"\n\nDetailed output saved to: {output_file.absolute()}")


async def custom_config_example():
    """Example with custom rendering configuration."""
    print("\n=== Custom Config Example ===\n")

    # Create custom config with different settings
    config = RendererConfig(
        render_level=RenderLevel.MINIMAL,  # Only user/assistant text
        compact_mode=True,  # More compact output
        max_text_length=200,  # Truncate long text
        show_metadata=False,  # Hide timestamps/metadata
    )

    # Create renderer
    renderer = MessageRenderer()
    formatter = ClaudeCodeFormatter(config)
    handler = StreamHandler(formatter=formatter)
    renderer.add_handler(handler)

    # Run query
    async for message in query(prompt="Explain what Python is in one sentence."):
        renderer.render(message)


async def main():
    """Run all examples."""
    await simple_example()
    await multi_handler_example()
    await custom_config_example()

    print("\n=== Examples Complete ===")
    print("\nKey takeaways:")
    print("1. Use display_message() for quick one-liners")
    print("2. Use MessageRenderer + handlers for more control")
    print("3. Configure RenderLevel to control verbosity")
    print("4. Use multiple handlers to output to console + file simultaneously")


if __name__ == "__main__":
    anyio.run(main)
