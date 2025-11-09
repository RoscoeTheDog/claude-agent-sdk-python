"""Pattern detection for technical references and semantic role mapping.

This module implements Claude CLI's pattern detection behavior for highlighting
technical references (issue #s, hex colors, env vars, repo paths) and mapping
messages to semantic roles for appropriate styling.
"""

import re
from re import Pattern
from typing import Any

from .config import PatternConfig
from .theme import StyleRule, Theme


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

    def __init__(self, config: PatternConfig, theme: Theme):
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
        self.patterns: list[tuple[str, Pattern[str], str]] = []

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

    def detect_and_style(
        self,
        text: str,
        preserve_ranges: list[tuple[int, int]] | None = None
    ) -> str:
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

    def _apply_ansi_style(self, text: str, style_rule: StyleRule) -> str:
        """Apply ANSI styling to text.

        Args:
            text: Text to style
            style_rule: Style rule to apply

        Returns:
            Text with ANSI codes applied
        """
        from .ansi import AnsiEncoder
        encoder = AnsiEncoder()
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


class EnhancedPatternDetector(PatternDetector):
    """Enhanced pattern detector with semantic role mapping.

    Extends original PatternDetector with:
    - Tool call pattern detection
    - Status indicator patterns
    - Large response warnings
    - Integration with Story 4.5 PatternBasedDetector
    - Integration with Story 4.6 ANSIFormatter
    """

    def __init__(self, config: PatternConfig, theme: Theme):
        """Initialize enhanced detector.

        Args:
            config: Pattern detection configuration
            theme: Theme for styling
        """
        super().__init__(config, theme)

        # Initialize semantic role detector from Story 4.5
        if config.enable_semantic_roles:
            from .semantic import PatternBasedDetector, RoleDetectionConfig

            role_config = RoleDetectionConfig()
            self.role_detector = PatternBasedDetector(role_config)
        else:
            self.role_detector = None

        # Initialize ANSI formatter from Story 4.6
        if config.enable_semantic_roles:
            from .semantic import ANSIFormatter, FormatterConfig, default_theme

            # Use semantic module's default theme (FormatterConfig expects ColorTheme)
            formatter_config = FormatterConfig(theme=default_theme())
            self.formatter = ANSIFormatter(formatter_config)
        else:
            self.formatter = None

        # Add status indicator patterns if enabled
        if config.enable_status_indicators:
            self._compile_status_patterns()
        else:
            self.status_patterns = []

    def _compile_status_patterns(self) -> None:
        """Compile status indicator patterns.

        Patterns from research (query4-tool-rendering.md):
        - ✓ Complete → SUCCESS role (green)
        - ✗ Failed → ERROR role (red)
        - ⚠️ Warning → WARNING role (yellow)
        - ⟳ Running → TOOL role (magenta)
        - ⊙ Pending → INFO role (cyan)
        """
        from .semantic import SemanticRole

        self.status_patterns: list[tuple[Pattern[str], SemanticRole]] = [
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
        preserve_ranges: list[tuple[int, int]] | None = None
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
        # Phase 1: Detect semantic role (if enabled)
        role = None
        if self.role_detector and self.config.enable_semantic_roles:
            role = self.role_detector.detect(message)

        # Phase 2: Check for large response warning (if enabled)
        if self.config.enable_large_response_warnings and self._is_large_response(text):
            from .semantic import SemanticRole
            warning_msg = self._format_large_response_warning(len(text))
            text = f"{warning_msg}\n\n{text}"
            role = SemanticRole.WARNING

        # Phase 3: Apply technical reference detection (original behavior)
        text_with_refs = super().detect_and_style(text, preserve_ranges)

        # Phase 4: Apply semantic role formatting (Story 4.6) if enabled and role detected
        if (self.formatter and self.config.enable_semantic_roles and
                role is not None):
            from .semantic import SemanticRole
            # Only apply role-based coloring for special roles
            if role in (SemanticRole.ERROR, SemanticRole.WARNING, SemanticRole.SUCCESS):
                formatted = self.formatter.format_with_icon(text_with_refs, role)
            else:
                # Just use technical reference highlighting
                formatted = text_with_refs
        else:
            # No semantic role formatting, just technical references
            formatted = text_with_refs

        return formatted

    def _is_large_response(self, text: str, threshold: int | None = None) -> bool:
        """Check if response exceeds token threshold.

        Args:
            text: Text to check
            threshold: Token threshold (defaults to config value)

        Returns:
            bool: True if response is large
        """
        if threshold is None:
            threshold = self.config.large_response_threshold

        # Rough approximation: 1 token ≈ 4 characters
        estimated_tokens = len(text) / 4
        return estimated_tokens > (threshold / 4)

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
