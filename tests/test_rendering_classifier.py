"""Tests for the semantic block classifier.

This module tests the BlockClassifier which maps content blocks to semantic
categories for theme-based styling.
"""

from claude_agent_sdk.rendering.classifier import BlockClassifier
from claude_agent_sdk.types import (
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
)


class TestBlockClassifierInit:
    """Tests for BlockClassifier initialization."""

    def test_classifier_initializes_without_error(self):
        """Test that classifier can be initialized."""
        classifier = BlockClassifier()
        assert classifier is not None

    def test_classifier_compiles_regex_patterns(self):
        """Test that regex patterns are compiled during init."""
        classifier = BlockClassifier()
        assert hasattr(classifier, "_error_regex")
        assert hasattr(classifier, "_warning_regex")
        assert hasattr(classifier, "_success_regex")
        assert hasattr(classifier, "_info_regex")


class TestTypeBasedClassification:
    """Tests for Tier 1: Type-based classification."""

    def test_tool_result_block_error(self):
        """Test that ToolResultBlock with is_error=True returns 'tool_error'."""
        classifier = BlockClassifier()
        block = ToolResultBlock(tool_use_id="123", is_error=True)
        assert classifier.classify(block) == "tool_error"

    def test_tool_result_block_error_with_content(self):
        """Test that ToolResultBlock with is_error=True and content returns 'tool_error'."""
        classifier = BlockClassifier()
        block = ToolResultBlock(
            tool_use_id="123",
            content="Error: File not found",
            is_error=True,
        )
        assert classifier.classify(block) == "tool_error"

    def test_tool_result_block_success(self):
        """Test that ToolResultBlock with is_error=False returns 'tool_result'."""
        classifier = BlockClassifier()
        block = ToolResultBlock(tool_use_id="123", is_error=False)
        assert classifier.classify(block) == "tool_result"

    def test_tool_result_block_success_with_content(self):
        """Test that ToolResultBlock with is_error=False and content returns 'tool_result'."""
        classifier = BlockClassifier()
        block = ToolResultBlock(
            tool_use_id="123",
            content="Success: File created",
            is_error=False,
        )
        assert classifier.classify(block) == "tool_result"

    def test_tool_result_block_no_error_flag(self):
        """Test that ToolResultBlock with is_error=None returns 'tool_result'."""
        classifier = BlockClassifier()
        block = ToolResultBlock(tool_use_id="123", is_error=None)
        assert classifier.classify(block) == "tool_result"

    def test_tool_use_block_read(self):
        """Test that ToolUseBlock for Read tool returns 'tool_use'."""
        classifier = BlockClassifier()
        block = ToolUseBlock(id="123", name="Read", input={"file_path": "test.py"})
        assert classifier.classify(block) == "tool_use"

    def test_tool_use_block_write(self):
        """Test that ToolUseBlock for Write tool returns 'tool_use'."""
        classifier = BlockClassifier()
        block = ToolUseBlock(id="123", name="Write", input={"file_path": "test.py"})
        assert classifier.classify(block) == "tool_use"

    def test_tool_use_block_bash(self):
        """Test that ToolUseBlock for Bash tool returns 'tool_use'."""
        classifier = BlockClassifier()
        block = ToolUseBlock(id="123", name="Bash", input={"command": "ls"})
        assert classifier.classify(block) == "tool_use"

    def test_tool_use_block_grep(self):
        """Test that ToolUseBlock for Grep tool returns 'tool_use'."""
        classifier = BlockClassifier()
        block = ToolUseBlock(id="123", name="Grep", input={"pattern": "test"})
        assert classifier.classify(block) == "tool_use"

    def test_tool_use_block_unknown_tool(self):
        """Test that ToolUseBlock for unknown tool returns 'tool_use'."""
        classifier = BlockClassifier()
        block = ToolUseBlock(id="123", name="UnknownTool", input={})
        assert classifier.classify(block) == "tool_use"

    def test_thinking_block(self):
        """Test that ThinkingBlock returns 'thinking'."""
        classifier = BlockClassifier()
        block = ThinkingBlock(
            thinking="Let me think about this...",
            signature="signature123",
        )
        assert classifier.classify(block) == "thinking"


class TestContentHeuristics:
    """Tests for Tier 3: Content heuristic classification."""

    def test_text_block_error_lowercase(self):
        """Test that TextBlock with 'error:' prefix returns 'error'."""
        classifier = BlockClassifier()
        block = TextBlock(text="error: Something went wrong")
        assert classifier.classify(block) == "error"

    def test_text_block_error_uppercase(self):
        """Test that TextBlock with 'ERROR' prefix returns 'error'."""
        classifier = BlockClassifier()
        block = TextBlock(text="ERROR: File not found")
        assert classifier.classify(block) == "error"

    def test_text_block_error_emoji(self):
        """Test that TextBlock with ❌ emoji returns 'error'."""
        classifier = BlockClassifier()
        block = TextBlock(text="❌ Operation failed")
        assert classifier.classify(block) == "error"

    def test_text_block_error_failed(self):
        """Test that TextBlock with 'failed' returns 'error'."""
        classifier = BlockClassifier()
        block = TextBlock(text="failed to connect to server")
        assert classifier.classify(block) == "error"

    def test_text_block_error_exception(self):
        """Test that TextBlock with 'Exception:' returns 'error'."""
        classifier = BlockClassifier()
        block = TextBlock(text="ValueError: Invalid input")
        assert classifier.classify(block) == "error"

    def test_text_block_error_traceback(self):
        """Test that TextBlock with 'Traceback' returns 'error'."""
        classifier = BlockClassifier()
        block = TextBlock(text="Traceback (most recent call last):")
        assert classifier.classify(block) == "error"

    def test_text_block_error_not_found(self):
        """Test that TextBlock with 'not found' returns 'error'."""
        classifier = BlockClassifier()
        block = TextBlock(text="File not found: test.py")
        assert classifier.classify(block) == "error"

    def test_text_block_warning_lowercase(self):
        """Test that TextBlock with 'warning:' prefix returns 'warning'."""
        classifier = BlockClassifier()
        block = TextBlock(text="warning: This is deprecated")
        assert classifier.classify(block) == "warning"

    def test_text_block_warning_uppercase(self):
        """Test that TextBlock with 'WARNING' prefix returns 'warning'."""
        classifier = BlockClassifier()
        block = TextBlock(text="WARNING: API will change")
        assert classifier.classify(block) == "warning"

    def test_text_block_warning_emoji(self):
        """Test that TextBlock with ⚠️ emoji returns 'warning'."""
        classifier = BlockClassifier()
        block = TextBlock(text="⚠️ Please review carefully")
        assert classifier.classify(block) == "warning"

    def test_text_block_warning_deprecated(self):
        """Test that TextBlock with 'deprecated' returns 'warning'."""
        classifier = BlockClassifier()
        block = TextBlock(text="This method is deprecated")
        assert classifier.classify(block) == "warning"

    def test_text_block_success_lowercase(self):
        """Test that TextBlock with 'success:' prefix returns 'success'."""
        classifier = BlockClassifier()
        block = TextBlock(text="success: Operation completed")
        assert classifier.classify(block) == "success"

    def test_text_block_success_uppercase(self):
        """Test that TextBlock with 'SUCCESS' prefix returns 'success'."""
        classifier = BlockClassifier()
        block = TextBlock(text="SUCCESS: All tests passed")
        assert classifier.classify(block) == "success"

    def test_text_block_success_emoji(self):
        """Test that TextBlock with ✅ emoji returns 'success'."""
        classifier = BlockClassifier()
        block = TextBlock(text="✅ Build completed")
        assert classifier.classify(block) == "success"

    def test_text_block_success_completed(self):
        """Test that TextBlock with 'completed' returns 'success'."""
        classifier = BlockClassifier()
        block = TextBlock(text="completed successfully")
        assert classifier.classify(block) == "success"

    def test_text_block_success_passed(self):
        """Test that TextBlock with 'passed' returns 'success'."""
        classifier = BlockClassifier()
        block = TextBlock(text="All tests passed")
        assert classifier.classify(block) == "success"

    def test_text_block_info_lowercase(self):
        """Test that TextBlock with 'info:' prefix returns 'info'."""
        classifier = BlockClassifier()
        block = TextBlock(text="info: Server started on port 8080")
        assert classifier.classify(block) == "info"

    def test_text_block_info_uppercase(self):
        """Test that TextBlock with 'INFO' prefix returns 'info'."""
        classifier = BlockClassifier()
        block = TextBlock(text="INFO: Loading configuration")
        assert classifier.classify(block) == "info"

    def test_text_block_info_emoji(self):
        """Test that TextBlock with ℹ️ emoji returns 'info'."""
        classifier = BlockClassifier()
        block = TextBlock(text="ℹ️ Configuration loaded from file")
        assert classifier.classify(block) == "info"

    def test_text_block_info_note(self):
        """Test that TextBlock with 'note:' prefix returns 'info'."""
        classifier = BlockClassifier()
        block = TextBlock(text="note: Remember to save your work")
        assert classifier.classify(block) == "info"

    def test_text_block_plain_text(self):
        """Test that TextBlock with plain text returns 'text'."""
        classifier = BlockClassifier()
        block = TextBlock(text="This is just regular text")
        assert classifier.classify(block) == "text"

    def test_text_block_empty(self):
        """Test that TextBlock with empty text returns 'text'."""
        classifier = BlockClassifier()
        block = TextBlock(text="")
        assert classifier.classify(block) == "text"

    def test_text_block_whitespace_only(self):
        """Test that TextBlock with only whitespace returns 'text'."""
        classifier = BlockClassifier()
        block = TextBlock(text="   \n\t  ")
        assert classifier.classify(block) == "text"


class TestEdgeCases:
    """Tests for edge cases and complex scenarios."""

    def test_multiline_error(self):
        """Test that multiline error text is classified correctly."""
        classifier = BlockClassifier()
        block = TextBlock(
            text="Some context\nerror: Something went wrong\nMore details"
        )
        assert classifier.classify(block) == "error"

    def test_error_not_at_start(self):
        """Test that error pattern not at start still matches."""
        classifier = BlockClassifier()
        block = TextBlock(text="Operation failed: ValueError: Invalid input")
        # 'failed' should match
        assert classifier.classify(block) == "error"

    def test_case_insensitivity(self):
        """Test that pattern matching is case-insensitive."""
        classifier = BlockClassifier()
        assert classifier.classify(TextBlock(text="Error: test")) == "error"
        assert classifier.classify(TextBlock(text="ERROR: test")) == "error"
        assert classifier.classify(TextBlock(text="error: test")) == "error"

    def test_priority_order_error_over_success(self):
        """Test that error patterns take priority when multiple patterns match."""
        classifier = BlockClassifier()
        # Text with both error and success patterns - error should win
        block = TextBlock(text="error: Operation completed successfully")
        assert classifier.classify(block) == "error"

    def test_priority_order_error_over_warning(self):
        """Test that error patterns take priority over warning."""
        classifier = BlockClassifier()
        block = TextBlock(text="error: warning about something")
        assert classifier.classify(block) == "error"

    def test_priority_order_warning_over_success(self):
        """Test that warning patterns take priority over success."""
        classifier = BlockClassifier()
        block = TextBlock(text="warning: completed successfully")
        assert classifier.classify(block) == "warning"

    def test_priority_order_success_over_info(self):
        """Test that success patterns take priority over info."""
        classifier = BlockClassifier()
        block = TextBlock(text="success: info about completion")
        assert classifier.classify(block) == "success"

    def test_unknown_block_type(self):
        """Test that unknown block types return 'text' as fallback."""
        classifier = BlockClassifier()

        # Use a simple dict to simulate an unknown block type
        class UnknownBlock:
            pass

        block = UnknownBlock()
        assert classifier.classify(block) == "text"

    def test_none_block(self):
        """Test that None block returns 'text' as fallback."""
        classifier = BlockClassifier()
        assert classifier.classify(None) == "text"


class TestHelperMethods:
    """Tests for private helper methods."""

    def test_matches_error_helper(self):
        """Test the _matches_error helper method."""
        classifier = BlockClassifier()
        assert classifier._matches_error("error: test") is True
        assert classifier._matches_error("ERROR: test") is True
        assert classifier._matches_error("failed to connect") is True
        assert classifier._matches_error("success: test") is False
        assert classifier._matches_error("plain text") is False

    def test_matches_warning_helper(self):
        """Test the _matches_warning helper method."""
        classifier = BlockClassifier()
        assert classifier._matches_warning("warning: test") is True
        assert classifier._matches_warning("WARNING: test") is True
        assert classifier._matches_warning("deprecated method") is True
        assert classifier._matches_warning("error: test") is False
        assert classifier._matches_warning("plain text") is False

    def test_matches_success_helper(self):
        """Test the _matches_success helper method."""
        classifier = BlockClassifier()
        assert classifier._matches_success("success: test") is True
        assert classifier._matches_success("SUCCESS: test") is True
        assert classifier._matches_success("completed successfully") is True
        assert classifier._matches_success("All tests passed") is True
        assert classifier._matches_success("error: test") is False
        assert classifier._matches_success("plain text") is False

    def test_matches_info_helper(self):
        """Test the _matches_info helper method."""
        classifier = BlockClassifier()
        assert classifier._matches_info("info: test") is True
        assert classifier._matches_info("INFO: test") is True
        assert classifier._matches_info("note: test") is True
        assert classifier._matches_info("error: test") is False
        assert classifier._matches_info("plain text") is False

    def test_helper_with_whitespace(self):
        """Test that helpers handle leading/trailing whitespace."""
        classifier = BlockClassifier()
        assert classifier._matches_error("  error: test  ") is True
        assert classifier._matches_warning("  warning: test  ") is True
        assert classifier._matches_success("  success: test  ") is True
        assert classifier._matches_info("  info: test  ") is True


class TestRealWorldExamples:
    """Tests using real-world message examples."""

    def test_bash_error_output(self):
        """Test classification of typical bash error output."""
        classifier = BlockClassifier()
        block = TextBlock(text="bash: command not found: nonexistent")
        assert classifier.classify(block) == "error"

    def test_python_traceback(self):
        """Test classification of Python traceback."""
        classifier = BlockClassifier()
        block = TextBlock(
            text="Traceback (most recent call last):\n  File 'test.py', line 1"
        )
        assert classifier.classify(block) == "error"

    def test_pytest_output_success(self):
        """Test classification of pytest success output."""
        classifier = BlockClassifier()
        block = TextBlock(text="===== 100 passed in 1.23s =====")
        assert classifier.classify(block) == "success"

    def test_pytest_output_failure(self):
        """Test classification of pytest failure output."""
        classifier = BlockClassifier()
        block = TextBlock(text="FAILED tests/test_example.py::test_function")
        assert classifier.classify(block) == "error"

    def test_deprecation_warning(self):
        """Test classification of deprecation warning."""
        classifier = BlockClassifier()
        block = TextBlock(
            text="DeprecationWarning: This function is deprecated, use new_function instead"
        )
        assert classifier.classify(block) == "warning"

    def test_git_output(self):
        """Test classification of git command output."""
        classifier = BlockClassifier()
        block = TextBlock(text="On branch main\nYour branch is up to date")
        assert classifier.classify(block) == "text"

    def test_file_not_found_error(self):
        """Test classification of file not found error."""
        classifier = BlockClassifier()
        block = TextBlock(text="Error: File not found: config.json")
        assert classifier.classify(block) == "error"

    def test_build_success_message(self):
        """Test classification of build success message."""
        classifier = BlockClassifier()
        block = TextBlock(text="Build completed successfully in 2.5s")
        assert classifier.classify(block) == "success"
