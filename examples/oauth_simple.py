"""
Simple OAuth Demo - Minimal Example

This is the simplest possible example of using OAuth with the SDK.
If you already ran 'claude /login', this will just work!
"""

import asyncio
from claude_agent_sdk import query, AssistantMessage, TextBlock, ResultMessage


async def main():
    print("Sending query using OAuth authentication...\n")

    # That's it! If you have OAuth credentials, SDK uses them automatically
    async for message in query(prompt="What is 2 + 2?"):
        # Extract and print just the text response
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif isinstance(message, ResultMessage):
            print(f"\n✓ Completed in {message.duration_ms}ms")
            print(f"  Cost: ${message.total_cost_usd:.6f} (using subscription)")


if __name__ == "__main__":
    asyncio.run(main())
