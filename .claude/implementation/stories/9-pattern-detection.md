# Story 9: Pattern Detection Infrastructure

**Status**: unassigned
**Assignee**: unassigned
**Estimated Time**: 2.5 hours
**Actual Time**: TBD
**Priority**: HIGH

---

## Dependencies

- Story 1 (COMPLETED) - Identifies technical reference patterns
- Story 2 (unassigned) - Theme foundation with `info` category
- Reference: `.claude/implementation/stories/1-color-analysis.md` - Section: "Technical References & Links"

---

## Description

Implement pattern detection infrastructure to automatically identify and highlight technical references (issue numbers, hex color codes, environment variables, repository paths) in assistant messages and tool results.

**Critical Finding**: From Story 1 analysis, Claude CLI uses **renderer-side pattern detection** (not LLM-generated markup) to identify and color technical elements cyan. This is a key differentiator in visual presentation.

**Goal**: Achieve feature parity with Claude CLI's automatic technical reference highlighting.

---

## Acceptance Criteria

### Core Infrastructure
- [ ] Create `src/claude_agent_sdk/rendering/pattern_detector.py` module
- [ ] Implement `PatternDetector` class with configurable regex patterns
- [ ] Integrate with renderer pipeline (after markdown parsing, before theme application)
- [ ] Support pattern categories: issue_number, hex_color, env_var, repo_path

### Pattern Detection Rules
- [ ] Issue numbers: `#\d+` → cyan (e.g., `#9812`, `#1234`)
- [ ] Hex color codes: `#[0-9A-Fa-f]{6}` → cyan (e.g., `#13A10E`, `#FF5733`)
- [ ] Environment variables: `[A-Z_][A-Z0-9_]+` → cyan (e.g., `COLORTERM`, `PATH`)
- [ ] Repository paths: `[\w-]+/[\w-]+` → cyan (e.g., `sharkdp/bat`, `anthropics/claude-code`)

### Configuration & Customization
- [ ] Add `PatternConfig` dataclass with enable/disable flags per pattern type
- [ ] Add `enable_pattern_detection: bool = True` to `RendererConfig`
- [ ] Allow custom regex patterns via configuration
- [ ] Pattern priority ordering (apply most specific first)

### Renderer Integration
- [ ] Apply pattern detection to assistant messages
- [ ] Apply pattern detection to tool results
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

## Testing Strategy

### Unit Tests

```python
def test_issue_number_detection():
    """Test issue number pattern detection."""
    detector = create_detector()

    text = "See issue #9812 and #6635 for details"
    result = detector.detect_and_style(text)

    # Verify issue numbers are cyan
    assert_contains_ansi_color(result, "#9812", BRIGHT_CYAN)
    assert_contains_ansi_color(result, "#6635", BRIGHT_CYAN)


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

**Document Version**: 1.0
**Created**: 2025-11-08 23:15
**Author**: Claude Agent SDK Team
**Priority**: HIGH - Critical for CLI feature parity
