# Archive Reason: Story 4 & 10 (2025-11-08)

**Date**: 2025-11-08 23:44
**Archived Stories**:
- Story 4: Code Syntax Highlighting Infrastructure
- Story 10: Structured Data Formatting

**Reason**: Architectural redesign for comprehensive multi-language support

---

## Issues with Original Design

### 1. Artificial Separation
- Story 4: Pygments for "code blocks" only
- Story 10: Manual JSON/YAML parsing for "tool results"
- **Problem**: JSON/YAML are supported by Pygments - created code duplication

### 2. Hard-Coded Language List
- Original Story 4 listed only 7 languages: Python, JS, TS, SQL, Bash, JSON, YAML
- **Problem**: Pygments supports 500+ languages, but architecture limited extensibility

### 3. Monolithic SyntaxMapping
- 14 hard-coded fields in dataclass
- **Problem**: Not extensible, required schema changes for new token types

### 4. No Separation of Concerns
- Single `SyntaxHighlighter` class mixed:
  - Language detection
  - Token mapping
  - Theme application
  - ANSI encoding
- **Problem**: Tight coupling, difficult to customize

---

## Replacement Architecture

**New Story 4 (v2)**: Unified Syntax & Semantic Highlighting

**Modular Design** (5 separate modules):
1. `language_registry.py` - Language catalog (supports 500+ languages)
2. `token_mapper.py` - Pygments token → semantic categories
3. `semantic_mapping.py` - Semantic categories → theme colors (customizable)
4. `structured_formatter.py` - Type-aware JSON/YAML formatting
5. `highlighter.py` - Orchestration layer

**Benefits**:
- Unified code path for code blocks AND tool results
- Extensible to all Pygments-supported languages
- Clean separation of concerns
- Customizable theming per language
- No code duplication

---

## Migration Path

**For developers**: If implementing from old stories, disregard and use new Story 4 (v2).

**Archived files preserved** for reference/comparison purposes.
