"""Tests for message parser error handling."""

import pytest

from claude_agent_sdk._errors import MessageParseError
from claude_agent_sdk._internal.message_parser import parse_message
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


class TestMessageParser:
    """Test message parsing with the new exception behavior."""

    def test_parse_valid_user_message(self):
        """Test parsing a valid user message."""
        data = {
            "type": "user",
            "message": {"content": [{"type": "text", "text": "Hello"}]},
        }
        message = parse_message(data)
        assert isinstance(message, UserMessage)
        assert len(message.content) == 1
        assert isinstance(message.content[0], TextBlock)
        assert message.content[0].text == "Hello"

    def test_parse_user_message_with_tool_use(self):
        """Test parsing a user message with tool_use block."""
        data = {
            "type": "user",
            "message": {
                "content": [
                    {"type": "text", "text": "Let me read this file"},
                    {
                        "type": "tool_use",
                        "id": "tool_456",
                        "name": "Read",
                        "input": {"file_path": "/example.txt"},
                    },
                ]
            },
        }
        message = parse_message(data)
        assert isinstance(message, UserMessage)
        assert len(message.content) == 2
        assert isinstance(message.content[0], TextBlock)
        assert isinstance(message.content[1], ToolUseBlock)
        assert message.content[1].id == "tool_456"
        assert message.content[1].name == "Read"
        assert message.content[1].input == {"file_path": "/example.txt"}

    def test_parse_user_message_with_tool_result(self):
        """Test parsing a user message with tool_result block."""
        data = {
            "type": "user",
            "message": {
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "tool_789",
                        "content": "File contents here",
                    }
                ]
            },
        }
        message = parse_message(data)
        assert isinstance(message, UserMessage)
        assert len(message.content) == 1
        assert isinstance(message.content[0], ToolResultBlock)
        assert message.content[0].tool_use_id == "tool_789"
        assert message.content[0].content == "File contents here"

    def test_parse_user_message_with_tool_result_error(self):
        """Test parsing a user message with error tool_result block."""
        data = {
            "type": "user",
            "message": {
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "tool_error",
                        "content": "File not found",
                        "is_error": True,
                    }
                ]
            },
        }
        message = parse_message(data)
        assert isinstance(message, UserMessage)
        assert len(message.content) == 1
        assert isinstance(message.content[0], ToolResultBlock)
        assert message.content[0].tool_use_id == "tool_error"
        assert message.content[0].content == "File not found"
        assert message.content[0].is_error is True

    def test_parse_user_message_with_mixed_content(self):
        """Test parsing a user message with mixed content blocks."""
        data = {
            "type": "user",
            "message": {
                "content": [
                    {"type": "text", "text": "Here's what I found:"},
                    {
                        "type": "tool_use",
                        "id": "use_1",
                        "name": "Search",
                        "input": {"query": "test"},
                    },
                    {
                        "type": "tool_result",
                        "tool_use_id": "use_1",
                        "content": "Search results",
                    },
                    {"type": "text", "text": "What do you think?"},
                ]
            },
        }
        message = parse_message(data)
        assert isinstance(message, UserMessage)
        assert len(message.content) == 4
        assert isinstance(message.content[0], TextBlock)
        assert isinstance(message.content[1], ToolUseBlock)
        assert isinstance(message.content[2], ToolResultBlock)
        assert isinstance(message.content[3], TextBlock)

    def test_parse_user_message_inside_subagent(self):
        """Test parsing a valid user message."""
        data = {
            "type": "user",
            "message": {"content": [{"type": "text", "text": "Hello"}]},
            "parent_tool_use_id": "toolu_01Xrwd5Y13sEHtzScxR77So8",
        }
        message = parse_message(data)
        assert isinstance(message, UserMessage)
        assert message.parent_tool_use_id == "toolu_01Xrwd5Y13sEHtzScxR77So8"

    def test_parse_valid_assistant_message(self):
        """Test parsing a valid assistant message."""
        data = {
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "text", "text": "Hello"},
                    {
                        "type": "tool_use",
                        "id": "tool_123",
                        "name": "Read",
                        "input": {"file_path": "/test.txt"},
                    },
                ],
                "model": "claude-opus-4-1-20250805",
            },
        }
        message = parse_message(data)
        assert isinstance(message, AssistantMessage)
        assert len(message.content) == 2
        assert isinstance(message.content[0], TextBlock)
        assert isinstance(message.content[1], ToolUseBlock)

    def test_parse_assistant_message_with_thinking(self):
        """Test parsing an assistant message with thinking block."""
        data = {
            "type": "assistant",
            "message": {
                "content": [
                    {
                        "type": "thinking",
                        "thinking": "I'm thinking about the answer...",
                        "signature": "sig-123",
                    },
                    {"type": "text", "text": "Here's my response"},
                ],
                "model": "claude-opus-4-1-20250805",
            },
        }
        message = parse_message(data)
        assert isinstance(message, AssistantMessage)
        assert len(message.content) == 2
        assert isinstance(message.content[0], ThinkingBlock)
        assert message.content[0].thinking == "I'm thinking about the answer..."
        assert message.content[0].signature == "sig-123"
        assert isinstance(message.content[1], TextBlock)
        assert message.content[1].text == "Here's my response"

    def test_parse_valid_system_message(self):
        """Test parsing a valid system message."""
        data = {"type": "system", "subtype": "start"}
        message = parse_message(data)
        assert isinstance(message, SystemMessage)
        assert message.subtype == "start"

    def test_parse_assistant_message_inside_subagent(self):
        """Test parsing a valid assistant message."""
        data = {
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "text", "text": "Hello"},
                    {
                        "type": "tool_use",
                        "id": "tool_123",
                        "name": "Read",
                        "input": {"file_path": "/test.txt"},
                    },
                ],
                "model": "claude-opus-4-1-20250805",
            },
            "parent_tool_use_id": "toolu_01Xrwd5Y13sEHtzScxR77So8",
        }
        message = parse_message(data)
        assert isinstance(message, AssistantMessage)
        assert message.parent_tool_use_id == "toolu_01Xrwd5Y13sEHtzScxR77So8"

    def test_parse_valid_result_message(self):
        """Test parsing a valid result message."""
        data = {
            "type": "result",
            "subtype": "success",
            "duration_ms": 1000,
            "duration_api_ms": 500,
            "is_error": False,
            "num_turns": 2,
            "session_id": "session_123",
        }
        message = parse_message(data)
        assert isinstance(message, ResultMessage)
        assert message.subtype == "success"

    def test_parse_invalid_data_type(self):
        """Test that non-dict data raises MessageParseError."""
        with pytest.raises(MessageParseError) as exc_info:
            parse_message("not a dict")  # type: ignore
        assert "Invalid message data type" in str(exc_info.value)
        assert "expected dict, got str" in str(exc_info.value)

    def test_parse_missing_type_field(self):
        """Test that missing 'type' field raises MessageParseError."""
        with pytest.raises(MessageParseError) as exc_info:
            parse_message({"message": {"content": []}})
        assert "Message missing 'type' field" in str(exc_info.value)

    def test_parse_unknown_message_type(self):
        """Test that unknown message type raises MessageParseError."""
        with pytest.raises(MessageParseError) as exc_info:
            parse_message({"type": "unknown_type"})
        assert "Unknown message type: unknown_type" in str(exc_info.value)

    def test_parse_user_message_missing_fields(self):
        """Test that user message with missing fields raises MessageParseError."""
        with pytest.raises(MessageParseError) as exc_info:
            parse_message({"type": "user"})
        assert "Missing required field in user message" in str(exc_info.value)

    def test_parse_assistant_message_missing_fields(self):
        """Test that assistant message with missing fields raises MessageParseError."""
        with pytest.raises(MessageParseError) as exc_info:
            parse_message({"type": "assistant"})
        assert "Missing required field in assistant message" in str(exc_info.value)

    def test_parse_system_message_missing_fields(self):
        """Test that system message with missing fields raises MessageParseError."""
        with pytest.raises(MessageParseError) as exc_info:
            parse_message({"type": "system"})
        assert "Missing required field in system message" in str(exc_info.value)

    def test_parse_result_message_missing_fields(self):
        """Test that result message with missing fields raises MessageParseError."""
        with pytest.raises(MessageParseError) as exc_info:
            parse_message({"type": "result", "subtype": "success"})
        assert "Missing required field in result message" in str(exc_info.value)

    def test_message_parse_error_contains_data(self):
        """Test that MessageParseError contains the original data."""
        data = {"type": "unknown", "some": "data"}
        with pytest.raises(MessageParseError) as exc_info:
            parse_message(data)
        assert exc_info.value.data == data

    def test_strip_system_reminders_from_user_tool_result(self):
        """Test that system reminders are removed from user message tool results."""
        data = {
            "type": "user",
            "message": {
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "test_id",
                        "content": "Line 1\n\n<system-reminder>\nThis is a system reminder that should be removed.\n</system-reminder>\n\nLine 2",
                        "is_error": False,
                    }
                ]
            },
        }
        message = parse_message(data)
        assert isinstance(message, UserMessage)
        assert len(message.content) == 1
        assert isinstance(message.content[0], ToolResultBlock)
        # System reminder should be stripped
        assert "<system-reminder>" not in message.content[0].content
        assert "</system-reminder>" not in message.content[0].content
        # Original content should remain
        assert "Line 1" in message.content[0].content
        assert "Line 2" in message.content[0].content

    def test_strip_system_reminders_from_assistant_tool_result(self):
        """Test that system reminders are removed from assistant message tool results."""
        data = {
            "type": "assistant",
            "message": {
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "test_id",
                        "content": "Result text\n\n<system-reminder>\nInternal reminder\n</system-reminder>\n\nMore text",
                        "is_error": False,
                    }
                ],
                "model": "claude-3-5-sonnet-20241022",
            },
        }
        message = parse_message(data)
        assert isinstance(message, AssistantMessage)
        assert len(message.content) == 1
        assert isinstance(message.content[0], ToolResultBlock)
        # System reminder should be stripped
        assert "<system-reminder>" not in message.content[0].content
        assert "</system-reminder>" not in message.content[0].content
        # Original content should remain
        assert "Result text" in message.content[0].content
        assert "More text" in message.content[0].content

    def test_strip_multiple_system_reminders(self):
        """Test that multiple system reminders are all removed."""
        data = {
            "type": "user",
            "message": {
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "test_id",
                        "content": "<system-reminder>First</system-reminder>\nContent\n<system-reminder>Second</system-reminder>",
                        "is_error": False,
                    }
                ]
            },
        }
        message = parse_message(data)
        assert isinstance(message, UserMessage)
        assert isinstance(message.content[0], ToolResultBlock)
        # Both system reminders should be stripped
        assert "<system-reminder>" not in message.content[0].content
        assert "First" not in message.content[0].content
        assert "Second" not in message.content[0].content
        # Original content should remain
        assert "Content" in message.content[0].content

    def test_strip_system_reminders_with_multiline_content(self):
        """Test that system reminders with multiline content are removed."""
        data = {
            "type": "user",
            "message": {
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "test_id",
                        "content": "Before\n\n<system-reminder>\nLine 1 of reminder\nLine 2 of reminder\nLine 3 of reminder\n</system-reminder>\n\nAfter",
                        "is_error": False,
                    }
                ]
            },
        }
        message = parse_message(data)
        assert isinstance(message, UserMessage)
        assert isinstance(message.content[0], ToolResultBlock)
        # System reminder should be completely removed
        assert "<system-reminder>" not in message.content[0].content
        assert "Line 1 of reminder" not in message.content[0].content
        assert "Line 2 of reminder" not in message.content[0].content
        # Original content should remain
        assert "Before" in message.content[0].content
        assert "After" in message.content[0].content

    def test_strip_system_reminders_handles_none_content(self):
        """Test that None content is handled gracefully."""
        data = {
            "type": "user",
            "message": {
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "test_id",
                        "content": None,
                        "is_error": False,
                    }
                ]
            },
        }
        message = parse_message(data)
        assert isinstance(message, UserMessage)
        assert isinstance(message.content[0], ToolResultBlock)
        # Should handle None gracefully
        assert message.content[0].content is None

    def test_strip_system_reminders_preserves_content_without_reminders(self):
        """Test that content without system reminders is unchanged."""
        original_content = "This is normal content\nWith multiple lines\nNo reminders here"
        data = {
            "type": "user",
            "message": {
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "test_id",
                        "content": original_content,
                        "is_error": False,
                    }
                ]
            },
        }
        message = parse_message(data)
        assert isinstance(message, UserMessage)
        assert isinstance(message.content[0], ToolResultBlock)
        # Content should be exactly the same
        assert message.content[0].content == original_content
