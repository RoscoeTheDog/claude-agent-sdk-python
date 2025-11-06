#!/usr/bin/env python3
"""Quick 30-second demo of the pretty printer.

This is a minimal demo that shows the core functionality quickly.
For a full feature showcase, run: python demo_pretty_printer.py
"""

import anyio
from claude_agent_sdk import query
from claude_agent_sdk.rendering import display_message, RenderLevel

print("""
╔══════════════════════════════════════════════════════════════╗
║  Claude Agent SDK - Pretty Printer Quick Demo (30 seconds)  ║
╚══════════════════════════════════════════════════════════════╝

This is the simplest way to use the pretty printer - just one line!

Code:
    from claude_agent_sdk.rendering import display_message

    async for message in query(prompt="Hello"):
        display_message(message)

Output:
""")


async def main():
    # Simple usage - just works!
    async for message in query(prompt="What is 2 + 2? Answer in one sentence."):
        display_message(message)

    print("\n" + "="*60)
    print("\n✓ That's it! One line of code for beautiful output.")
    print("\nFor more features, run: python demo_pretty_printer.py")
    print("\nFeatures:")
    print("  • Multiple output destinations (console, file, custom)")
    print("  • Configurable verbosity levels (MINIMAL → DETAILED)")
    print("  • UTF-8 formatting matching Claude Code CLI")
    print("  • Tool use/result formatting")
    print("  • Customizable configuration\n")


if __name__ == "__main__":
    anyio.run(main)
