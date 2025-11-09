"""Pygments token to semantic category mapper.

This module maps Pygments token types to language-agnostic semantic
categories. This abstraction layer allows themes to customize syntax
coloring without knowledge of specific Pygments token types.

Token Hierarchy:
    Pygments uses a token hierarchy where specific tokens inherit from
    parent types. For example:
        Token.Name.Function inherits from Token.Name
        Token.Keyword.Type inherits from Token.Keyword

    This mapper uses exact matches first, then walks up the hierarchy
    to find the most specific semantic category.

Usage:
    >>> from pygments.token import Token
    >>> mapper = TokenMapper()
    >>> mapper.map_token(Token.Keyword)
    'keyword'
    >>> mapper.map_token(Token.Name.Function)
    'function_name'
"""

from pygments.token import Token


class TokenMapper:
    """Maps Pygments token types to semantic categories.

    This provides a language-agnostic abstraction layer between Pygments
    tokenization and theme styling. Themes can then map semantic categories
    to colors without needing to know about specific Pygments tokens.

    Semantic Categories:
        - keyword: Language keywords (if, def, class, etc.)
        - keyword_operator: Keyword-style operators (and, or, not)
        - string_literal: String values
        - escape_sequence: Escape sequences in strings
        - number_literal: Numeric values
        - boolean_literal: Boolean values (true/false)
        - comment: Comments and documentation
        - doc_string: Docstrings
        - type_annotation: Type hints and annotations
        - class_type: Class names in type context
        - class_name: Class names in definition context
        - function_name: Function/method names
        - builtin_function: Built-in functions (print, len, etc.)
        - decorator: Decorators (@dataclass, etc.)
        - special_identifier: Special names (self, this, cls)
        - identifier: Generic identifiers
        - operator: Operators (+, -, ==, etc.)
        - punctuation: Brackets, commas, etc.
        - default: Fallback for unknown tokens
    """

    # Complete Pygments token → semantic category mapping
    TOKEN_TO_SEMANTIC: dict[Token, str] = {
        # ===== Keywords =====
        Token.Keyword: "keyword",
        Token.Keyword.Constant: "boolean_literal",  # True, False, true, false
        Token.Keyword.Declaration: "keyword",  # var, let, const
        Token.Keyword.Namespace: "keyword",  # import, package, use
        Token.Keyword.Pseudo: "keyword",  # self in some contexts
        Token.Keyword.Reserved: "keyword",
        Token.Keyword.Type: "type_annotation",  # class in type context

        # ===== Names (Identifiers) =====
        Token.Name: "identifier",
        Token.Name.Attribute: "identifier",  # object.attribute
        Token.Name.Builtin: "builtin_function",  # print, len, range
        Token.Name.Builtin.Pseudo: "special_identifier",  # self, this, super
        Token.Name.Class: "class_name",
        Token.Name.Constant: "identifier",  # Constants like MAX_SIZE
        Token.Name.Decorator: "decorator",  # @decorator
        Token.Name.Entity: "identifier",
        Token.Name.Exception: "class_type",  # Exception types
        Token.Name.Function: "function_name",
        Token.Name.Function.Magic: "builtin_function",  # __init__, __str__
        Token.Name.Label: "identifier",
        Token.Name.Namespace: "identifier",  # Module names
        Token.Name.Other: "identifier",
        Token.Name.Property: "identifier",
        Token.Name.Tag: "keyword",  # HTML/XML tags
        Token.Name.Variable: "identifier",
        Token.Name.Variable.Class: "special_identifier",  # cls
        Token.Name.Variable.Global: "identifier",
        Token.Name.Variable.Instance: "special_identifier",  # self
        Token.Name.Variable.Magic: "special_identifier",  # __name__

        # ===== Literals =====
        Token.Literal: "string_literal",
        Token.Literal.Date: "string_literal",

        # Strings
        Token.Literal.String: "string_literal",
        Token.Literal.String.Affix: "string_literal",  # r, f, u prefixes
        Token.Literal.String.Backtick: "string_literal",  # `template string`
        Token.Literal.String.Char: "string_literal",  # 'c'
        Token.Literal.String.Delimiter: "string_literal",  # String delimiters
        Token.Literal.String.Doc: "doc_string",  # """Docstrings"""
        Token.Literal.String.Double: "string_literal",  # "double quoted"
        Token.Literal.String.Escape: "escape_sequence",  # \n, \t, etc.
        Token.Literal.String.Heredoc: "string_literal",
        Token.Literal.String.Interpol: "string_literal",  # ${interpolation}
        Token.Literal.String.Other: "string_literal",
        Token.Literal.String.Regex: "string_literal",  # /regex/
        Token.Literal.String.Single: "string_literal",  # 'single quoted'
        Token.Literal.String.Symbol: "string_literal",  # :symbol

        # Numbers
        Token.Literal.Number: "number_literal",
        Token.Literal.Number.Bin: "number_literal",  # 0b1010
        Token.Literal.Number.Float: "number_literal",  # 3.14
        Token.Literal.Number.Hex: "number_literal",  # 0xFF
        Token.Literal.Number.Integer: "number_literal",
        Token.Literal.Number.Integer.Long: "number_literal",
        Token.Literal.Number.Oct: "number_literal",  # 0o755

        # ===== Operators =====
        Token.Operator: "operator",
        Token.Operator.Word: "keyword_operator",  # and, or, not, in, is

        # ===== Punctuation =====
        Token.Punctuation: "punctuation",
        Token.Punctuation.Marker: "punctuation",  # @ in @decorator context

        # ===== Comments =====
        Token.Comment: "comment",
        Token.Comment.Hashbang: "comment",  # #!/usr/bin/env python
        Token.Comment.Multiline: "comment",  # /* ... */
        Token.Comment.Preproc: "keyword",  # #include, #define
        Token.Comment.PreprocFile: "string_literal",  # #include "file.h"
        Token.Comment.Single: "comment",  # // comment
        Token.Comment.Special: "comment",  # TODO, FIXME

        # ===== Generic (diffs, errors, etc.) =====
        Token.Generic: "identifier",
        Token.Generic.Deleted: "error",  # - deleted line
        Token.Generic.Emph: "identifier",  # *emphasis*
        Token.Generic.Error: "error",
        Token.Generic.Heading: "keyword",  # # Heading
        Token.Generic.Inserted: "success",  # + inserted line
        Token.Generic.Output: "identifier",
        Token.Generic.Prompt: "keyword",  # >>> prompt
        Token.Generic.Strong: "identifier",  # **strong**
        Token.Generic.Subheading: "keyword",
        Token.Generic.Traceback: "error",

        # ===== Other =====
        Token.Error: "error",
        Token.Other: "identifier",
        Token.Whitespace: "whitespace",  # Usually not styled
    }

    def map_token(self, token_type: Token) -> str:
        """Map Pygments token type to semantic category.

        Uses exact match first, then walks up token hierarchy to find
        the most specific semantic category.

        Args:
            token_type: Pygments token type (e.g., Token.Keyword.Type)

        Returns:
            Semantic category name (e.g., "keyword", "string_literal")

        Example:
            >>> mapper = TokenMapper()
            >>> mapper.map_token(Token.Keyword.Type)
            'type_annotation'
            >>> mapper.map_token(Token.Name.Function)
            'function_name'
            >>> mapper.map_token(Token.Name.Function.Magic)
            'builtin_function'
        """
        # Try exact match first
        if token_type in self.TOKEN_TO_SEMANTIC:
            return self.TOKEN_TO_SEMANTIC[token_type]

        # Walk up token hierarchy
        current = token_type
        while current.parent is not None:
            if current.parent in self.TOKEN_TO_SEMANTIC:
                return self.TOKEN_TO_SEMANTIC[current.parent]
            current = current.parent

        # Default fallback
        return "default"
