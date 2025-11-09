"""Language registry for syntax highlighting.

This module maintains the catalog of supported programming languages
and their metadata. New languages can be added by simply adding entries
to the LANGUAGES dict - no code changes required.

Usage:
    >>> lang = LanguageRegistry.detect(hint="python")
    >>> lang.name
    'Python'
    >>> lang.pygments_lexer
    'python'
"""

from dataclasses import dataclass


@dataclass
class LanguageSpec:
    """Specification for a programming language.

    Attributes:
        name: Human-readable name (e.g., "Python", "JavaScript")
        aliases: List of fence hint aliases (e.g., ["py", "python", "python3"])
        pygments_lexer: Lexer name for Pygments.get_lexer_by_name()
        category: Language category for grouping/filtering
        semantic_formatter: Optional override to use StructuredDataFormatter
                           instead of Pygments (e.g., "json", "yaml")

    Example:
        >>> python_spec = LanguageSpec(
        ...     name="Python",
        ...     aliases=["py", "python", "python3"],
        ...     pygments_lexer="python",
        ...     category="general_purpose"
        ... )
    """

    name: str
    aliases: list[str]
    pygments_lexer: str
    category: str  # general_purpose, data_format, markup, shell, database
    semantic_formatter: str | None = None  # "json", "yaml", or None


class LanguageRegistry:
    """Central registry of supported programming languages.

    This class maintains a catalog of language specifications and provides
    language detection from fence hints (e.g., ```python) or content analysis.

    To add a new language, simply add an entry to the LANGUAGES dict.
    No code changes required.

    Usage:
        >>> # Detect from fence hint
        >>> lang = LanguageRegistry.detect(hint="python")
        >>>
        >>> # Check if uses semantic formatter
        >>> if lang.semantic_formatter:
        ...     # Use StructuredDataFormatter
        ... else:
        ...     # Use Pygments
    """

    # Language catalog - add new languages here
    LANGUAGES: dict[str, LanguageSpec] = {
        # General Purpose Languages
        "python": LanguageSpec(
            name="Python",
            aliases=["py", "python", "python3"],
            pygments_lexer="python",
            category="general_purpose"
        ),
        "javascript": LanguageSpec(
            name="JavaScript",
            aliases=["js", "javascript"],
            pygments_lexer="javascript",
            category="general_purpose"
        ),
        "typescript": LanguageSpec(
            name="TypeScript",
            aliases=["ts", "typescript"],
            pygments_lexer="typescript",
            category="general_purpose"
        ),
        "java": LanguageSpec(
            name="Java",
            aliases=["java"],
            pygments_lexer="java",
            category="general_purpose"
        ),
        "csharp": LanguageSpec(
            name="C#",
            aliases=["csharp", "cs", "c#"],
            pygments_lexer="csharp",
            category="general_purpose"
        ),
        "ruby": LanguageSpec(
            name="Ruby",
            aliases=["ruby", "rb"],
            pygments_lexer="ruby",
            category="general_purpose"
        ),
        "php": LanguageSpec(
            name="PHP",
            aliases=["php"],
            pygments_lexer="php",
            category="general_purpose"
        ),
        "swift": LanguageSpec(
            name="Swift",
            aliases=["swift"],
            pygments_lexer="swift",
            category="general_purpose"
        ),
        "kotlin": LanguageSpec(
            name="Kotlin",
            aliases=["kotlin", "kt"],
            pygments_lexer="kotlin",
            category="general_purpose"
        ),

        # Systems Programming
        "rust": LanguageSpec(
            name="Rust",
            aliases=["rust", "rs"],
            pygments_lexer="rust",
            category="general_purpose"
        ),
        "go": LanguageSpec(
            name="Go",
            aliases=["go", "golang"],
            pygments_lexer="go",
            category="general_purpose"
        ),
        "c": LanguageSpec(
            name="C",
            aliases=["c"],
            pygments_lexer="c",
            category="general_purpose"
        ),
        "cpp": LanguageSpec(
            name="C++",
            aliases=["cpp", "c++", "cxx"],
            pygments_lexer="cpp",
            category="general_purpose"
        ),

        # Data Formats (use semantic formatters)
        "json": LanguageSpec(
            name="JSON",
            aliases=["json"],
            pygments_lexer="json",
            category="data_format",
            semantic_formatter="json"  # Use StructuredDataFormatter
        ),
        "yaml": LanguageSpec(
            name="YAML",
            aliases=["yaml", "yml"],
            pygments_lexer="yaml",
            category="data_format",
            semantic_formatter="yaml"  # Use StructuredDataFormatter
        ),
        "xml": LanguageSpec(
            name="XML",
            aliases=["xml"],
            pygments_lexer="xml",
            category="data_format"
        ),
        "toml": LanguageSpec(
            name="TOML",
            aliases=["toml"],
            pygments_lexer="toml",
            category="data_format"
        ),

        # Markup Languages
        "html": LanguageSpec(
            name="HTML",
            aliases=["html", "htm"],
            pygments_lexer="html",
            category="markup"
        ),
        "css": LanguageSpec(
            name="CSS",
            aliases=["css"],
            pygments_lexer="css",
            category="markup"
        ),
        "scss": LanguageSpec(
            name="SCSS",
            aliases=["scss", "sass"],
            pygments_lexer="scss",
            category="markup"
        ),
        "markdown": LanguageSpec(
            name="Markdown",
            aliases=["markdown", "md"],
            pygments_lexer="markdown",
            category="markup"
        ),

        # Shell/Scripting
        "bash": LanguageSpec(
            name="Bash",
            aliases=["bash", "sh", "shell"],
            pygments_lexer="bash",
            category="shell"
        ),
        "powershell": LanguageSpec(
            name="PowerShell",
            aliases=["powershell", "ps1"],
            pygments_lexer="powershell",
            category="shell"
        ),

        # Database
        "sql": LanguageSpec(
            name="SQL",
            aliases=["sql", "postgresql", "mysql", "sqlite"],
            pygments_lexer="sql",
            category="database"
        ),

        # Add more languages as needed - 500+ supported by Pygments!
    }

    @classmethod
    def detect(cls, hint: str | None = None, content: str | None = None) -> LanguageSpec:
        """Detect language from fence hint or content analysis.

        Args:
            hint: Language hint from code fence (e.g., "python" from ```python)
            content: Source code content for fallback detection

        Returns:
            LanguageSpec for detected language, or plaintext fallback

        Example:
            >>> lang = LanguageRegistry.detect(hint="py")
            >>> lang.name
            'Python'
        """
        # Try fence hint first
        if hint:
            hint_lower = hint.lower().strip()
            for lang_id, spec in cls.LANGUAGES.items():
                if hint_lower in spec.aliases or hint_lower == lang_id:
                    return spec

        # Fallback: content-based detection (future enhancement)
        # Could use Pygments' guess_lexer(content) here

        # Unknown language - return plaintext
        return cls.get_plaintext()

    @classmethod
    def get_plaintext(cls) -> LanguageSpec:
        """Get fallback spec for unknown/plain text.

        Returns:
            LanguageSpec for plain text (no syntax highlighting)
        """
        return LanguageSpec(
            name="Plain Text",
            aliases=["text", "plaintext", "txt"],
            pygments_lexer="text",
            category="plaintext"
        )

    @classmethod
    def get_by_id(cls, lang_id: str) -> LanguageSpec | None:
        """Get language spec by ID.

        Args:
            lang_id: Language identifier (e.g., "python", "javascript")

        Returns:
            LanguageSpec if found, None otherwise
        """
        return cls.LANGUAGES.get(lang_id.lower())
