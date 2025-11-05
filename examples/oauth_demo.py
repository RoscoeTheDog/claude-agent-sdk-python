"""
OAuth Authentication Demo

This example demonstrates using the Python SDK with OAuth authentication.
If you already have valid OAuth credentials from running 'claude /login',
the SDK will automatically use them for subscription-based billing.

Prerequisites:
    1. Run 'claude /login' to set up OAuth credentials (one-time setup)
    2. Valid credentials stored in ~/.claude/.credentials.json

The SDK will:
    - Auto-detect your OAuth credentials
    - Use your Claude subscription instead of API credits
    - Auto-refresh tokens when they expire
"""

import asyncio

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage,
    SystemMessage,
)


async def basic_oauth_example():
    """Basic example - SDK auto-detects OAuth credentials."""
    print("=" * 60)
    print("Example 1: Basic OAuth (Auto-detect)")
    print("=" * 60)
    print("\nSending query to Claude using OAuth authentication...")
    print("(This will use your subscription, not API credits)\n")

    async for message in query(prompt="What is 2 + 2? Keep your answer brief."):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif isinstance(message, ResultMessage):
            print(f"\n✓ Query completed in {message.duration_ms}ms")
            print(f"  Cost: ${message.total_cost_usd:.6f}")
            print(f"  Tokens: {message.usage.get('output_tokens', 0)} output")
            print(f"  API Key Source: {message.usage.get('apiKeySource', 'N/A')}")

    print("\n" + "=" * 60 + "\n")


async def explicit_oauth_example():
    """Example with explicit OAuth mode configuration."""
    print("=" * 60)
    print("Example 2: Explicit OAuth Mode")
    print("=" * 60)
    print("\nForcing OAuth authentication (will fail if OAuth unavailable)...\n")

    # Force OAuth mode - fail if OAuth credentials not available
    options = ClaudeAgentOptions(
        auth_mode="oauth",
        auth_fallback=False,  # No fallback to API key
    )

    async for message in query(
        prompt="Tell me a fun fact about Python programming. Be brief.",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif isinstance(message, ResultMessage):
            print(f"\n✓ Query completed in {message.duration_ms}ms")
            print(f"  Cost: ${message.total_cost_usd:.6f}")
            print(f"  Tokens: {message.usage.get('output_tokens', 0)} output")

    print("\n" + "=" * 60 + "\n")


async def oauth_with_tools_example():
    """Example using OAuth with file operations."""
    print("=" * 60)
    print("Example 3: OAuth with Tools")
    print("=" * 60)
    print("\nUsing OAuth authentication with file operations...\n")

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write"],
        permission_mode="acceptEdits",  # Auto-accept file edits
        auth_mode="oauth",  # Use OAuth
    )

    async for message in query(
        prompt="Create a file called hello_oauth.txt with the message 'Hello from OAuth!'",
        options=options,
    ):
        if isinstance(message, SystemMessage):
            if message.subtype == "init":
                print(f"Session started: {message.data.get('session_id', 'N/A')[:8]}...")
                print(f"Model: {message.data.get('model', 'N/A')}")
                print(f"Permission mode: {message.data.get('permissionMode', 'N/A')}")
                print()
        elif isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"\n[Tool: {block.name}]")
                    print(f"  Input: {block.input}")
        elif isinstance(message, ResultMessage):
            print(f"\n✓ Task completed in {message.duration_ms}ms")
            print(f"  Turns: {message.num_turns}")
            print(f"  Cost: ${message.total_cost_usd:.6f}")
            print(f"  Total tokens: {message.usage.get('input_tokens', 0)} input + {message.usage.get('output_tokens', 0)} output")

    print("\n" + "=" * 60 + "\n")


async def check_auth_status():
    """Helper to check OAuth authentication status."""
    print("=" * 60)
    print("Checking OAuth Authentication Status")
    print("=" * 60)

    try:
        from claude_agent_sdk._internal.oauth_credentials import (
            read_credentials,
            CredentialsNotFoundError,
        )

        try:
            creds = read_credentials()
            print(f"\n✓ OAuth credentials found!")
            print(f"  - Subscription: {creds.subscription}")
            print(f"  - Scopes: {', '.join(creds.scopes)}")
            print(f"  - Expired: {'Yes' if creds.is_expired else 'No'}")
            print(f"  - Valid: {'Yes' if creds.is_valid else 'No'}")

            if creds.is_expired:
                print(
                    "\n  Note: Token is expired but SDK will auto-refresh it when needed."
                )
            else:
                print("\n  Your OAuth token is ready to use!")

        except CredentialsNotFoundError:
            print("\n✗ No OAuth credentials found.")
            print("\nTo set up OAuth authentication:")
            print("  1. Run: claude /login")
            print("  2. Complete browser login")
            print("  3. Run this script again")
            print(
                "\nAlternatively, set ANTHROPIC_API_KEY to use API key authentication."
            )

    except ImportError as e:
        print(f"\n✗ Error importing OAuth modules: {e}")

    print("\n" + "=" * 60 + "\n")


async def main():
    """Run all OAuth examples."""
    # Check OAuth status first
    await check_auth_status()

    try:
        # Run basic OAuth example
        await basic_oauth_example()

        # Run explicit OAuth example
        await explicit_oauth_example()

        # Run OAuth with tools example
        await oauth_with_tools_example()

        print("\n" + "=" * 60)
        print("All OAuth examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure you've run 'claude /login' first")
        print("  2. Check that ~/.claude/.credentials.json exists")
        print("  3. Try running 'claude /login' again to refresh credentials")


if __name__ == "__main__":
    asyncio.run(main())
