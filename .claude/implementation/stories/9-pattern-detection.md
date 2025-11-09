# Story 9: Pattern Detection & Semantic Role Mapping (Enhanced)

**Status**: unassigned
**Assignee**: unassigned
**Estimated Time**: 3.5 hours (2.5h original + 1.0h enhancement)
**Actual Time**: TBD
**Priority**: HIGH
**Version**: 2.0 (Enhanced with Stories 4.5 + 4.6 integration)

---

## Dependencies

- Story 1 (COMPLETED) - Identifies technical reference patterns
- Story 2 (unassigned) - Theme foundation with `info` category
- **Story 4.5 (unassigned) - REQUIRED** - Provides SemanticRole taxonomy and PatternBasedDetector
- **Story 4.6 (unassigned) - REQUIRED** - Provides ANSIFormatter and theme integration
- Reference: `.claude/implementation/stories/1-color-analysis.md` - Section: "Technical References & Links"
- Reference: `.claude/research/semantic-ui-coloring/final-recommendations.md`

---

## Description

Implement comprehensive pattern detection infrastructure with two layers:
1. **Technical Reference Detection** (original) - Issue numbers, hex codes, env vars, repo paths
2. **Semantic Role Mapping** (enhancement) - Tool calls, status indicators, large response warnings, metadata hints

**Architecture Philosophy**: Extends PatternBasedDetector from Story 4.5 with additional tool-specific patterns. Integrates with ANSIFormatter from Story 4.6 for semantic role-based coloring.

**Critical Finding**: From Story 1 analysis, Claude CLI uses **renderer-side pattern detection** (not LLM-generated markup) to identify and color technical elements. Research validation adds tool call patterns, status indicators, and large response handling.

**Goal**:
- Original: Feature parity with Claude CLI's technical reference highlighting
- Enhancement: Intelligent tool call detection, status indicator rendering, large response warnings

---

## Acceptance Criteria

### Core Infrastructure (Original)
- [ ] Create `src/claude_agent_sdk/rendering/pattern_detector.py` module
- [ ] Implement `PatternDetector` class with configurable regex patterns
- [ ] Integrate with renderer pipeline (after markdown parsing, before theme application)
- [ ] Support pattern categories: issue_number, hex_color, env_var, repo_path

### Technical Reference Detection (Original)
- [ ] Issue numbers: `#\d+` → cyan (e.g., `#9812`, `#1234`)
- [ ] Hex color codes: `#[0-9A-Fa-f]{6}` → cyan (e.g., `#13A10E`, `#FF5733`)
- [ ] Environment variables: `[A-Z_][A-Z0-9_]+` → cyan (e.g., `COLORTERM`, `PATH`)
- [ ] Repository paths: `[\w-]+/[\w-]+` → cyan (e.g., `sharkdp/bat`, `anthropics/claude-code`)

### Semantic Role Mapping (Enhancement - Stories 4.5 + 4.6)
- [ ] Extend `PatternBasedDetector` from Story 4.5 with tool-specific patterns
- [ ] Tool call detection (`tool_use` message type → TOOL role)
- [ ] Tool result detection (`tool_result` message type → TOOL role)
- [ ] Status indicator detection (✓, ✗, ⚠️, ⟳, ⊙) with appropriate roles
- [ ] Large response detection (~11.5k tokens) → WARNING role
- [ ] Support for `message.metadata.ui.role` explicit hints

### Status Indicator Rendering (Enhancement)
- [ ] Success indicator: `^✓` → SUCCESS role (green)
- [ ] Error indicator: `^✗` → ERROR role (red)
- [ ] Warning indicator: `^⚠️` → WARNING role (yellow)
- [ ] Running indicator: `⟳` → TOOL role (magenta)
- [ ] Pending indicator: `⊙` → INFO role (cyan)

### Large Response Handling (Enhancement)
- [ ] Token counting for message content
- [ ] Warning threshold detection (~11.5k tokens)
- [ ] Large response warning message formatting
- [ ] Integration with ANSIFormatter for warning display

### Configuration & Customization
- [ ] Add `PatternConfig` dataclass with enable/disable flags per pattern type
- [ ] Add `enable_pattern_detection: bool = True` to `RendererConfig`
- [ ] Add `enable_semantic_roles: bool = True` flag (enhancement)
- [ ] Allow custom regex patterns via configuration
- [ ] Pattern priority ordering (metadata > type > content > technical refs)

### Renderer Integration
- [ ] Apply technical reference detection to assistant messages
- [ ] Apply technical reference detection to tool results
- [ ] Apply semantic role detection to all message types
- [ ] Integrate with ANSIFormatter from Story 4.6
- [ ] Preserve code block content (no pattern detection within code)
- [ ] Handle overlapping patterns correctly (longest match wins)

---

## Technical Implementation

### Affected Files

**New Files**:
- `src/claude_agent_sdk/rendering/pattern_detector.py` - Pattern detection module

**Modified Files**:
- `src/claude_agent_sdk/rendering/config.py` - Add `PatternConfig`, `enable_pattern_detection`
- `src/claude_agent_sdk/rendering/formatters.py` - Integrate pattern detection
- `src/claude_agent_sdk/rendering/base.py` - Update rendering pipeline

### Pattern Detector Implementation

```python
from dataclasses import dataclass
from typing import Optional, Pattern
import re

@dataclass
class PatternConfig:
    """Configuration for pattern detection.

    Controls which patterns are detected and highlighted.
    """
    enable_issue_numbers: bool = True
    enable_hex_colors: bool = True
    enable_env_vars: bool = True
    enable_repo_paths: bool = True

    # Custom patterns (name → regex)
    custom_patterns: dict[str, str] = None

    def __post_init__(self):
        if self.custom_patterns is None:
            self.custom_patterns = {}


class PatternDetector:
    """Detects and highlights technical references in text.

    Implements renderer-side pattern detection matching Claude CLI behavior.
    Identified patterns are styled with the theme's 'info' category (cyan).

    Pattern Priority:
    1. Code blocks (skip pattern detection)
    2. Existing inline code (skip pattern detection)
    3. Custom patterns (user-defined)
    4. Built-in patterns (issue #s, hex codes, env vars, repos)
    """

    # Built-in pattern definitions
    ISSUE_NUMBER_PATTERN = r'(?<![a-zA-Z0-9])#(\d+)(?![a-zA-Z0-9])'
    HEX_COLOR_PATTERN = r'(?<![a-zA-Z0-9])#([0-9A-Fa-f]{6})(?![a-zA-Z0-9])'
    ENV_VAR_PATTERN = r'\b([A-Z_][A-Z0-9_]{2,})\b'  # Min 3 chars to avoid false positives
    REPO_PATH_PATTERN = r'(?<![a-zA-Z0-9/])([\w-]+)/([\w.-]+)(?![a-zA-Z0-9/])'

    def __init__(self, config: PatternConfig, theme: 'Theme'):
        """Initialize pattern detector.

        Args:
            config: Pattern detection configuration
            theme: Theme for styling matched patterns
        """
        self.config = config
        self.theme = theme
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile all enabled patterns into regex objects."""
        self.patterns: list[tuple[str, Pattern, str]] = []

        # Add built-in patterns if enabled
        if self.config.enable_issue_numbers:
            self.patterns.append((
                "issue_number",
                re.compile(self.ISSUE_NUMBER_PATTERN),
                "info"  # Theme category
            ))

        if self.config.enable_hex_colors:
            self.patterns.append((
                "hex_color",
                re.compile(self.HEX_COLOR_PATTERN),
                "info"
            ))

        if self.config.enable_env_vars:
            self.patterns.append((
                "env_var",
                re.compile(self.ENV_VAR_PATTERN),
                "info"
            ))

        if self.config.enable_repo_paths:
            self.patterns.append((
                "repo_path",
                re.compile(self.REPO_PATH_PATTERN),
                "info"
            ))

        # Add custom patterns
        for name, regex in self.config.custom_patterns.items():
            self.patterns.append((
                f"custom_{name}",
                re.compile(regex),
                "info"
            ))

    def detect_and_style(self, text: str, preserve_ranges: list[tuple[int, int]] = None) -> str:
        """Detect patterns in text and apply styling.

        Args:
            text: Text to process
            preserve_ranges: List of (start, end) ranges to skip (e.g., code blocks)

        Returns:
            Text with ANSI styling applied to detected patterns
        """
        if preserve_ranges is None:
            preserve_ranges = []

        # Track all matches with their positions
        matches = []

        for pattern_name, pattern, theme_category in self.patterns:
            for match in pattern.finditer(text):
                start, end = match.span()

                # Skip if in preserved range
                if any(p_start <= start < p_end or p_start < end <= p_end
                       for p_start, p_end in preserve_ranges):
                    continue

                matches.append((start, end, match.group(0), theme_category))

        # Sort by start position
        matches.sort(key=lambda m: m[0])

        # Remove overlapping matches (keep longest)
        filtered_matches = []
        last_end = 0
        for start, end, matched_text, category in matches:
            if start >= last_end:
                filtered_matches.append((start, end, matched_text, category))
                last_end = end

        # Apply styling in reverse order to preserve positions
        result = text
        for start, end, matched_text, category in reversed(filtered_matches):
            style_rule = getattr(self.theme, category)
            styled = self._apply_ansi_style(matched_text, style_rule)
            result = result[:start] + styled + result[end:]

        return result

    def _apply_ansi_style(self, text: str, style_rule: 'StyleRule') -> str:
        """Apply ANSI styling to text."""
        from claude_agent_sdk.rendering.ansi import ANSIEncoder
        encoder = ANSIEncoder()
        return encoder.encode(text, style_rule)

    def extract_code_ranges(self, text: str) -> list[tuple[int, int]]:
        """Extract ranges of code blocks and inline code to preserve.

        Args:
            text: Text to analyze

        Returns:
            List of (start, end) ranges to skip during pattern detection
        """
        ranges = []

        # Triple-backtick code blocks
        code_block_pattern = re.compile(r'```[^\n]*\n(.*?)```', re.DOTALL)
        for match in code_block_pattern.finditer(text):
            ranges.append(match.span())

        # Inline code
        inline_code_pattern = re.compile(r'`([^`]+)`')
        for match in inline_code_pattern.finditer(text):
            ranges.append(match.span())

        return ranges
```

### Integration with Formatters

```python
# In formatters.py
class MessageFormatter:
    def __init__(self, config: RendererConfig):
        self.config = config
        self.theme = config.theme

        # Initialize pattern detector
        if config.enable_pattern_detection:
            pattern_config = config.pattern_config or PatternConfig()
            self.pattern_detector = PatternDetector(pattern_config, self.theme)
        else:
            self.pattern_detector = None

    def format_assistant_message(self, message: AssistantMessage) -> str:
        """Format assistant message with pattern detection."""
        formatted_blocks = []

        for block in message.content:
            if isinstance(block, TextBlock):
                # Extract code ranges to preserve
                code_ranges = self.pattern_detector.extract_code_ranges(block.text) if self.pattern_detector else []

                # Apply pattern detection
                if self.pattern_detector:
                    processed_text = self.pattern_detector.detect_and_style(
                        block.text,
                        preserve_ranges=code_ranges
                    )
                else:
                    processed_text = block.text

                formatted_blocks.append(processed_text)
            # ... handle other block types

        return '\n'.join(formatted_blocks)
```

---

## Enhancement: Semantic Role Integration (Stories 4.5 + 4.6)

### Extended Pattern Detector with Semantic Roles

**File**: `src/claude_agent_sdk/rendering/pattern_detector.py` (Enhanced)

```python
from claude_agent_sdk.rendering.semantic import (
    SemanticRole,
    PatternBasedDetector,
    ANSIFormatter,
)

class EnhancedPatternDetector(PatternDetector):
    """Enhanced pattern detector with semantic role mapping.

    Extends original PatternDetector with:
    - Tool call pattern detection
    - Status indicator patterns
    - Large response warnings
    - Integration with Story 4.5 PatternBasedDetector
    - Integration with Story 4.6 ANSIFormatter
    """

    def __init__(self, config: PatternConfig, theme: 'Theme'):
        """Initialize enhanced detector.

        Args:
            config: Pattern detection configuration
            theme: Theme for styling
        """
        super().__init__(config, theme)

        # Initialize semantic role detector from Story 4.5
        from claude_agent_sdk.rendering.semantic import (
            PatternBasedDetector,
            RoleDetectionConfig,
        )
        role_config = RoleDetectionConfig()
        self.role_detector = PatternBasedDetector(role_config)

        # Initialize ANSI formatter from Story 4.6
        from claude_agent_sdk.rendering.semantic import (
            ANSIFormatter,
            FormatterConfig,
        )
        formatter_config = FormatterConfig(theme=theme)
        self.formatter = ANSIFormatter(formatter_config)

        # Add status indicator patterns
        self._compile_status_patterns()

    def _compile_status_patterns(self) -> None:
        """Compile status indicator patterns.

        Patterns from research (query4-tool-rendering.md):
        - ✓ Complete → SUCCESS role (green)
        - ✗ Failed → ERROR role (red)
        - ⚠️ Warning → WARNING role (yellow)
        - ⟳ Running → TOOL role (magenta)
        - ⊙ Pending → INFO role (cyan)
        """
        self.status_patterns = [
            (re.compile(r'^✓'), SemanticRole.SUCCESS),
            (re.compile(r'^✗'), SemanticRole.ERROR),
            (re.compile(r'^⚠️'), SemanticRole.WARNING),
            (re.compile(r'⟳'), SemanticRole.TOOL),
            (re.compile(r'⊙'), SemanticRole.INFO),
        ]

    def detect_and_style_with_roles(
        self,
        text: str,
        message: Any,
        preserve_ranges: list[tuple[int, int]] = None
    ) -> str:
        """Detect patterns AND semantic roles, applying appropriate styling.

        Two-phase processing:
        1. Detect semantic role (Story 4.5) → base message styling
        2. Detect technical references (original) → fine-grained highlighting

        Args:
            text: Text to process
            message: Message object for role detection
            preserve_ranges: Code ranges to skip

        Returns:
            Styled text with both role-based and pattern-based coloring
        """
        # Phase 1: Detect semantic role
        role = self.role_detector.detect(message)

        # Phase 2: Check for large response warning
        if self._is_large_response(text):
            warning_msg = self._format_large_response_warning(len(text))
            text = f"{warning_msg}\n\n{text}"
            role = SemanticRole.WARNING

        # Phase 3: Apply technical reference detection (original behavior)
        text_with_refs = super().detect_and_style(text, preserve_ranges)

        # Phase 4: Apply semantic role formatting (Story 4.6)
        # Only if message doesn't have fine-grained formatting already
        if role in (SemanticRole.ERROR, SemanticRole.WARNING, SemanticRole.SUCCESS):
            # Apply role-based coloring to entire message
            formatted = self.formatter.format_with_icon(text_with_refs, role)
        else:
            # Just use technical reference highlighting
            formatted = text_with_refs

        return formatted

    def _is_large_response(self, text: str, threshold: int = 11500) -> bool:
        """Check if response exceeds token threshold.

        Args:
            text: Text to check
            threshold: Token threshold (default: ~11.5k from research)

        Returns:
            bool: True if response is large
        """
        # Rough approximation: 1 token ≈ 4 characters
        estimated_tokens = len(text) / 4
        return estimated_tokens > threshold

    def _format_large_response_warning(self, char_count: int) -> str:
        """Format large response warning message.

        Pattern from research (query4-tool-rendering.md):
        ⚠️ Large response (12,543 tokens)
           Response truncated at 10,000 characters

        Args:
            char_count: Character count of response

        Returns:
            Formatted warning string
        """
        token_estimate = char_count // 4
        warning = f"⚠️ Large response ({token_estimate:,} tokens)"

        # Truncation levels from research: 4k, 6k, 8k, 10k, 12k, 16k
        truncation_levels = [4000, 6000, 8000, 10000, 12000, 16000]
        truncate_at = next(
            (level for level in truncation_levels if char_count > level),
            None
        )

        if truncate_at:
            warning += f"\n   Response may be truncated at {truncate_at:,} characters"

        return warning
```

### Integration with Renderer Pipeline

**File**: `src/claude_agent_sdk/rendering/formatters.py` (Enhanced)

```python
class MessageFormatter:
    """Enhanced message formatter with semantic role support."""

    def __init__(self, config: RendererConfig):
        self.config = config
        self.theme = config.theme

        # Initialize enhanced pattern detector
        if config.enable_pattern_detection:
            pattern_config = config.pattern_config or PatternConfig()
            self.pattern_detector = EnhancedPatternDetector(
                pattern_config,
                self.theme
            )
        else:
            self.pattern_detector = None

    def format_message(self, message: Message) -> str:
        """Format message with semantic role detection and styling.

        Integration with Stories 4.5 + 4.6:
        1. Detect semantic role (PatternBasedDetector)
        2. Apply role-based formatting (ANSIFormatter)
        3. Apply technical reference highlighting (original)

        Args:
            message: Message to format

        Returns:
            Formatted message with ANSI styling
        """
        # Extract code ranges to preserve
        code_ranges = []
        if self.pattern_detector:
            code_ranges = self.pattern_detector.extract_code_ranges(
                message.content
            )

        # Apply enhanced detection (both roles and patterns)
        if self.pattern_detector and hasattr(self.pattern_detector, 'detect_and_style_with_roles'):
            formatted = self.pattern_detector.detect_and_style_with_roles(
                message.content,
                message,
                preserve_ranges=code_ranges
            )
        elif self.pattern_detector:
            # Fallback to original pattern detection
            formatted = self.pattern_detector.detect_and_style(
                message.content,
                preserve_ranges=code_ranges
            )
        else:
            formatted = message.content

        return formatted
```

---

## Testing Strategy (Enhanced)

### Unit Tests (Original + Enhancement)

```python
# Original tests (technical references)
def test_issue_number_detection(): ...
def test_hex_color_detection(): ...
def test_env_var_detection(): ...
def test_repo_path_detection(): ...
def test_code_preservation(): ...
def test_overlapping_patterns(): ...

# Enhancement tests (semantic roles)
def test_tool_call_role_detection():
    """Test tool call message type detection."""
    from claude_agent_sdk.rendering.semantic import SemanticRole

    detector = create_enhanced_detector()

    class Message:
        def __init__(self):
            self.type = "tool_use"
            self.content = "Calling tool: Read"

    role = detector.role_detector.detect(Message())
    assert role == SemanticRole.TOOL


def test_status_indicator_success():
    """Test success indicator pattern."""
    detector = create_enhanced_detector()

    class Message:
        def __init__(self):
            self.type = "assistant"
            self.content = "✓ Task completed successfully"

    formatted = detector.detect_and_style_with_roles(
        "✓ Task completed successfully",
        Message()
    )

    # Should be green (SUCCESS role)
    assert "\033[32;1m" in formatted  # Bright green
    assert "✓" in formatted


def test_status_indicator_error():
    """Test error indicator pattern."""
    detector = create_enhanced_detector()

    class Message:
        def __init__(self):
            self.type = "assistant"
            self.content = "✗ Task failed"

    formatted = detector.detect_and_style_with_roles(
        "✗ Task failed",
        Message()
    )

    # Should be red (ERROR role)
    assert "\033[31;1m" in formatted  # Bright red
    assert "✗" in formatted


def test_large_response_warning():
    """Test large response detection and warning."""
    detector = create_enhanced_detector()

    # Create large text (>11.5k tokens ≈ >46k chars)
    large_text = "a" * 50000

    class Message:
        def __init__(self):
            self.type = "assistant"
            self.content = large_text

    assert detector._is_large_response(large_text) == True

    formatted = detector.detect_and_style_with_roles(
        large_text,
        Message()
    )

    # Should include warning
    assert "⚠️ Large response" in formatted
    assert "tokens" in formatted


def test_metadata_role_hint():
    """Test metadata.ui.role explicit hint."""
    from claude_agent_sdk.rendering.semantic import SemanticRole

    detector = create_enhanced_detector()

    class UIMetadata:
        role = "success"

    class Metadata:
        ui = UIMetadata()

    class Message:
        def __init__(self):
            self.type = "assistant"
            self.content = "Operation succeeded"
            self.metadata = Metadata()

    role = detector.role_detector.detect(Message())
    assert role == SemanticRole.SUCCESS


def test_combined_technical_and_semantic():
    """Test both technical reference and semantic role detection."""
    detector = create_enhanced_detector()

    class Message:
        def __init__(self):
            self.type = "assistant"
            self.content = "See issue #9812 for COLORTERM details"

    formatted = detector.detect_and_style_with_roles(
        "See issue #9812 for COLORTERM details",
        Message()
    )

    # Should have both technical reference highlighting
    assert "#9812" in formatted  # Issue number
    assert "COLORTERM" in formatted  # Env var
    # And appropriate ANSI codes
    assert "\033[" in formatted


def test_hex_color_detection():
    """Test hex color code detection."""
    detector = create_detector()

    text = "Use colors #13A10E and #FF5733"
    result = detector.detect_and_style(text)

    assert_contains_ansi_color(result, "#13A10E", BRIGHT_CYAN)
    assert_contains_ansi_color(result, "#FF5733", BRIGHT_CYAN)


def test_env_var_detection():
    """Test environment variable detection."""
    detector = create_detector()

    text = "Check COLORTERM and PATH variables"
    result = detector.detect_and_style(text)

    assert_contains_ansi_color(result, "COLORTERM", BRIGHT_CYAN)
    assert_contains_ansi_color(result, "PATH", BRIGHT_CYAN)


def test_repo_path_detection():
    """Test repository path detection."""
    detector = create_detector()

    text = "See sharkdp/bat and anthropics/claude-code"
    result = detector.detect_and_style(text)

    assert_contains_ansi_color(result, "sharkdp/bat", BRIGHT_CYAN)
    assert_contains_ansi_color(result, "anthropics/claude-code", BRIGHT_CYAN)


def test_code_preservation():
    """Test that code blocks are preserved."""
    detector = create_detector()

    text = """Check #9812. Here's code:
```python
# This #1234 should not be highlighted
ENV_VAR = "test"
```
But #5678 outside code should be."""

    code_ranges = detector.extract_code_ranges(text)
    result = detector.detect_and_style(text, preserve_ranges=code_ranges)

    # Outside code: highlighted
    assert_contains_ansi_color(result, "#9812", BRIGHT_CYAN)
    assert_contains_ansi_color(result, "#5678", BRIGHT_CYAN)

    # Inside code: not highlighted
    assert_not_highlighted(result, "#1234")
    assert_not_highlighted(result, "ENV_VAR")  # In code context


def test_overlapping_patterns():
    """Test handling of overlapping patterns."""
    detector = create_detector()

    # Hex color that starts with #
    text = "#13A10E is a color, not issue #13"
    result = detector.detect_and_style(text)

    # Should match hex color (longer match)
    assert_contains_ansi_color(result, "#13A10E", BRIGHT_CYAN)
```

---

## Implementation Guidance

### Architecture Reference

- See: `stories/renderer-architecture.md` - Section: "Pattern Detector"
- Pattern detection occurs in rendering pipeline after markdown parsing
- Applied before final theme styling
- Preserves code block integrity

### Performance Optimization

```python
# Cache compiled patterns
# Limit regex complexity (avoid catastrophic backtracking)
# Process in chunks for very long text
```

### False Positive Handling

```python
# Environment variables: Minimum 3 characters to avoid false positives
# Repository paths: Validate format (no spaces, valid characters)
# Issue numbers: Word boundary checks to avoid matching in URLs
```

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| False positives | Medium | Medium | Strict regex patterns, minimum length requirements |
| Performance on large text | Low | Low | Chunk processing, pattern caching |
| Overlapping patterns | Medium | Low | Longest match priority, conflict resolution |
| Code block interference | High | Low | Explicit code range preservation |

---

## Future Enhancements

- URL detection and highlighting
- File path detection
- Semantic version detection (v1.2.3)
- UUID detection
- IP address detection
- Custom pattern plugins

---

## Completion Checklist

- [ ] PatternDetector class implemented
- [ ] All built-in patterns working (issue #s, hex, env vars, repos)
- [ ] Code range preservation functional
- [ ] Integration with formatters complete
- [ ] Configuration options working
- [ ] Unit tests passing (90%+ coverage)
- [ ] Integration tests validating full pipeline
- [ ] Manual validation against Claude CLI
- [ ] Performance acceptable (< 10ms for typical message)
- [ ] Documentation updated
- [ ] Code reviewed
- [ ] Story marked complete in index.md

---

## Time Breakdown (Enhanced)

### Original Scope (2.5h)
- **Core Infrastructure**: 30 min
- **Technical Reference Patterns**: 45 min
- **Configuration**: 15 min
- **Renderer Integration**: 30 min
- **Testing**: 30 min
- **Documentation**: 10 min

### Enhancement (Stories 4.5 + 4.6 Integration) (+1.0h)
- **Semantic Role Integration**: 20 min
- **Status Indicator Patterns**: 15 min
- **Large Response Handling**: 15 min
- **Enhanced Testing**: 10 min

**Total**: 3.5 hours

---

## Success Criteria (Enhanced)

✅ **Original: All technical reference patterns working**
- Issue numbers, hex codes, env vars, repo paths detected
- Cyan highlighting applied correctly
- Code blocks preserved

✅ **Enhancement: Semantic role detection integrated**
- Tool calls detected and styled (TOOL role → magenta)
- Status indicators rendered with correct colors
- Large response warnings triggered at ~11.5k tokens
- Metadata.ui.role hints respected

✅ **Integration with Stories 4.5 + 4.6 complete**
- PatternBasedDetector extended
- ANSIFormatter integrated
- Combined technical + semantic detection working

---

## References (Enhanced)

- Original: `.claude/implementation/stories/1-color-analysis.md`
- Enhancement: `.claude/research/semantic-ui-coloring/final-recommendations.md`
- Enhancement: `.claude/research/semantic-ui-coloring/phase2-deep-research/query4-tool-rendering.md`
- Story 4.5: Semantic Role Taxonomy & Detection (dependency)
- Story 4.6: UI Element Formatter (dependency)
- Architecture: `.claude/implementation/SPRINT-1.5-ARCHITECTURE-REDESIGN-SUMMARY.md`

---

**Document Version**: 2.0 (Enhanced with Stories 4.5 + 4.6)
**Created**: 2025-11-08 23:15
**Updated**: 2025-11-09 (Semantic role integration)
**Author**: Claude Agent SDK Team
**Priority**: HIGH - Critical for CLI feature parity + semantic coloring
