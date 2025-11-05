"""
Simple OAuth Demo - Minimal Example

This is the simplest possible example of using OAuth with the SDK.
If you already ran 'claude /login', this will just work!
"""

import asyncio
from claude_agent_sdk import query


async def main():
    print("Sending query using OAuth authentication...\n")

    # That's it! If you have OAuth credentials, SDK uses them automatically
    async for message in query(prompt="What is 2 + 2?"):
        print(message)


if __name__ == "__main__":
    asyncio.run(main())
