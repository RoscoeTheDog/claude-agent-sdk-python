# Handoff Document: Semantic UI Element Coloring Architecture

**Date**: 2025-11-09 00:15
**Status**: Ready for Next Agent
**Priority**: HIGH
**Context**: Sprint 1.5 Architecture Enhancement - Phase 2

---

## Executive Summary

We need to add **semantic UI element coloring** to the Sprint 1.5 architecture. The current redesign (Phase 1) focused on **code syntax highlighting** for programming languages. This phase (Phase 2) addresses **structured output formatting** - how the renderer colors different UI elements based on their semantic role (tool calls, warnings, headers, lists, technical references, etc.).

**Key Insight**: The Claude CLI doesn't just do syntax highlighting - it does **semantic role-based coloring** for the entire UI. Our architecture needs both.

---

## What We've Completed (Phase 1)

### ✅ Modular Syntax Highlighting Architecture

Successfully redesigned Sprint 1.5 to support unlimited programming languages:

**5-Module Architecture**:
1. `language_registry.py` - Language catalog (500+ via Pygments)
2. `token_mapper.py` - Pygments token → semantic category
3. `semantic_mapping.py` - Semantic category → theme color
4. `structured_formatter.py` - Type-aware JSON/YAML formatting
5. `highlighter.py` - Orchestration layer

**Story 4 v2**: Unified Syntax & Semantic Highlighting
- **File**: `.claude/implementation/stories/4-unified-syntax-semantic-highlighting.md` (28.5 KB)
- **Status**: Design complete, ready for implementation
- **Scope**: Code blocks (Python, JS, JSON, YAML, etc.)

**Related Documents**:
- `.claude/implementation/index.md` - Sprint plan with dependency graph
- `.claude/implementation/SPRINT-1.5-ARCHITECTURE-REDESIGN-SUMMARY.md` - Phase 1 summary
- `.claude/implementation/stories/12-architecture-documentation.md` - Documentation strategy

---

## What We Need to Add (Phase 2)

### ❌ Semantic UI Element Coloring

**Problem**: The current architecture only handles **code syntax** coloring. It doesn't handle **UI element** coloring based on semantic roles.

**Missing Functionality**:
- Tool call headers (green bullets, warnings)
- Section markers (bullets, bold headers)
- Technical references (issue numbers, hex codes, environment variables)
- Emphasis/warnings (bold, yellow highlighting)
- List formatting (numbered, bulleted)
- Truncation indicators
- Status messages

---

## Research Findings (User-Provided)

### Claude CLI Screenshot Analysis

User provided screenshot showing Claude Code's structured output with these patterns:

#### 1. Tool/MCP Call Headers
```
● gptr-mcp - deep_research (MCP)(query: "...")
  ⚠️ Large MCP response (~11.5k tokens)
```
- **Green bullet** (`●`) - Active/successful tool
- **White** - Tool name and description
- **Yellow** - Warning text (`⚠️` + message)

#### 2. Structured Data (JSON Output)
```json
{
  "status": "success",
  "research_id": "1d3427d7-74a4-4af7-84ca-6e1c2adfbe6a",
```
- **Gray/dim** - Property names (`"status"`, `"research_id"`)
- **Green** - String values (`"success"`, `"..."`)
- **Gray/dim** - Expansion hints (`… +1140 lines (ctrl+o to expand)`)

#### 3. Section Headers
```
● Key Findings from Research
  Claude CLI Technical Details
  Important Implications for Our SDK
```
- **White bullet** (`●`) - Section markers
- **Bold white** - Section titles
- **Gray/dim** - Subsection headers

#### 4. Technical References
```
References: #9812, #6635, sharkdp/bat, COLORTERM, #13A10E
```
- **Cyan** - Issue numbers (`#9812`)
- **Cyan** - Hex color codes (`#13A10E`)
- **Cyan** - Environment variables (`COLORTERM`)
- **Cyan** - Repository names (`sharkdp/bat`)

#### 5. Emphasis & Warnings
```
**NOT** - Important warning
**bold text** - Emphasis
```
- **Bold white** - Emphasized text
- **Yellow** - Warning indicators

---

## Key Research Insight: Renderer-Side Processing

**User's Research Question**: "Is the LLM doing this coloring, or the renderer?"

**Answer**: **The renderer handles semantic UI coloring**

### Why Renderer-Side?

1. **Structured JSONL Stream**: Claude CLI returns structured data over JSONL streams with semantic metadata
   ```jsonl
   {"type": "tool_call", "tool": "gptr-mcp", "status": "pending"}
   {"type": "tool_result", "data": {...}}
   {"type": "text", "content": "..."}
   ```

2. **Separation of Concerns**: LLM shouldn't know about:
   - Terminal color capabilities
   - User theme configuration
   - UI implementation details

3. **Evidence from Screenshot**: UI affordances like `"… +1140 lines (ctrl+o to expand)"` are renderer-added, not LLM output

4. **Consistent Formatting**: Tool call headers, bullet styles, indentation are too consistent to be LLM-generated

### Proposed Architecture (From User's Research)

```
┌─────────────┐
│   LLM       │ → Outputs structured JSONL
│  (Claude)   │
└─────────────┘
      ↓
┌─────────────┐
│   Parser    │ → Parses JSONL stream
└─────────────┘
      ↓
┌─────────────┐
│  Semantic   │ → Assigns semantic roles:
│  Classifier │    - tool_call
└─────────────┘    - user_message
      ↓            - assistant_message
┌─────────────┐    - code_block
│    Ink      │    - list_item
│  Renderer   │    - emphasis
└─────────────┘    - technical_reference
      ↓            - warning
┌─────────────┐
│  Theme Map  │ → Maps roles to ANSI colors
└─────────────┘
      ↓
  Terminal Output
```

---

## Architecture Challenge

We have **two separate coloring concerns**:

### 1. Code Syntax Coloring (✅ Solved in Phase 1)
**Scope**: Programming language syntax within code blocks
**Input**: Source code string + language hint
**Output**: ANSI-styled code with syntax colors
**Module**: `SyntaxHighlighter` (Story 4 v2)

**Example**:
```python
def hello():  # 'def' → blue, 'hello' → white
    print("world")  # 'print' → blue, "world" → red
```

### 2. Semantic UI Element Coloring (❌ Needs Design)
**Scope**: UI elements based on their semantic role in structured output
**Input**: Message block + semantic role metadata
**Output**: ANSI-styled UI elements (bullets, warnings, headers, references)
**Module**: TBD - needs design

**Example**:
```
● tool_name - description     # Green bullet, white text
  ⚠️ Large response (~11k tokens)  # Yellow warning

  Property: "value"           # Gray key, green value
  #9812                       # Cyan issue reference
  **Important**               # Bold white emphasis
```

---

## Current Architecture Gap

**Story 4 v2 handles**:
- ✅ Code syntax highlighting (keywords, strings, numbers, etc.)
- ✅ JSON/YAML semantic formatting (keys→gray, values→green)

**Story 4 v2 does NOT handle**:
- ❌ Tool call headers with colored bullets
- ❌ Warning indicators (yellow `⚠️` + text)
- ❌ Section markers (white/green bullets)
- ❌ Technical reference detection (issue #s, hex codes, env vars)
- ❌ Emphasis/bold text
- ❌ List formatting
- ❌ Truncation indicators

**Why the gap?** Story 4 v2 assumes it receives **code strings** to highlight. It doesn't handle **message-level semantic roles** for UI elements.

---

## Proposed Solution

### Option A: Extend Story 4 v2 (Unified Approach)

Add semantic UI coloring to the existing `SyntaxHighlighter` orchestrator:

**Pros**:
- Single entry point for all coloring
- Reuses `semantic_mapping.py` infrastructure
- Consistent with modular architecture

**Cons**:
- `SyntaxHighlighter` becomes more complex
- Mixing code highlighting with UI element highlighting

### Option B: Separate Module (Parallel Approach)

Create new `UIElementFormatter` parallel to `SyntaxHighlighter`:

**Pros**:
- Clean separation: code vs UI
- Independent evolution
- Clear responsibilities

**Cons**:
- Two formatters to maintain
- Potential inconsistency in semantic mapping

### Option C: Renderer-Level Integration (Recommended)

Create **semantic role detection** in the renderer that works with formatters:

**Architecture**:
```
MessageFormatter (renderer)
  ├─→ detect_semantic_role(block) → "tool_call" | "warning" | "reference" | etc.
  ├─→ SyntaxHighlighter (for code blocks)
  ├─→ PatternDetector (for technical references) [Story 9]
  └─→ UIElementFormatter (NEW - for structured UI elements)
```

**Pros**:
- Renderer knows message context (tool calls, results, etc.)
- Can apply role-based styling before syntax highlighting
- Aligns with user's research (renderer-side semantic classification)
- Clean pipeline: role detection → formatter selection → styling

**Cons**:
- More complex renderer logic
- Need to define semantic role taxonomy

---

## Technical Requirements

### 1. Semantic Role Taxonomy

Define all UI element roles:

```python
class SemanticRole(Enum):
    # Message Types
    TOOL_CALL_HEADER = "tool_call_header"
    TOOL_RESULT = "tool_result"
    USER_MESSAGE = "user_message"
    ASSISTANT_MESSAGE = "assistant_message"
    SYSTEM_MESSAGE = "system_message"

    # UI Elements
    SECTION_HEADER = "section_header"
    SUBSECTION_HEADER = "subsection_header"
    LIST_ITEM = "list_item"
    CODE_BLOCK = "code_block"

    # Emphasis
    BOLD_TEXT = "bold_text"
    EMPHASIS = "emphasis"
    WARNING = "warning"

    # Technical References
    ISSUE_REFERENCE = "issue_reference"      # #9812
    HEX_COLOR = "hex_color"                  # #13A10E
    ENV_VARIABLE = "env_variable"            # COLORTERM
    REPO_REFERENCE = "repo_reference"        # sharkdp/bat

    # Data Elements
    JSON_KEY = "json_key"
    JSON_STRING_VALUE = "json_string_value"
    JSON_NUMBER_VALUE = "json_number_value"
    JSON_BOOLEAN_VALUE = "json_boolean_value"

    # UI Affordances
    TRUNCATION_HINT = "truncation_hint"
    EXPANSION_HINT = "expansion_hint"

    # Status Indicators
    SUCCESS_BULLET = "success_bullet"        # Green ●
    ACTIVE_BULLET = "active_bullet"          # Green ●
    SECTION_BULLET = "section_bullet"        # White ●
```

### 2. Pattern Detection (Story 9 Enhancement)

Story 9 already covers pattern detection. Needs integration with semantic roles:

**Current Story 9 Patterns**:
- Issue numbers: `#\d+`
- Hex colors: `#[0-9A-Fa-f]{6}`
- Environment variables: `[A-Z_]+`
- Repository paths: `\w+/\w+`

**Enhancement Needed**: Map detected patterns to semantic roles

### 3. UIElementFormatter Module

**New Module**: `src/claude_agent_sdk/rendering/ui_element_formatter.py`

**Responsibilities**:
- Apply role-based styling to UI elements
- Handle bullets (●) with appropriate colors
- Handle warnings (⚠️ + yellow text)
- Handle emphasis (bold, italic)
- Handle technical references (cyan coloring)

**Interface**:
```python
class UIElementFormatter:
    def __init__(self, theme: Theme, semantic_mapping: SemanticMapping):
        self.theme = theme
        self.semantic_mapping = semantic_mapping

    def format_by_role(self, text: str, role: SemanticRole) -> str:
        """Apply styling based on semantic role."""
        pass

    def format_tool_call_header(
        self,
        tool_name: str,
        description: str,
        status: str = "success"
    ) -> str:
        """Format tool call header with bullet and warning."""
        pass

    def format_warning(self, text: str) -> str:
        """Format warning with ⚠️ and yellow styling."""
        pass

    def format_technical_reference(self, text: str, ref_type: str) -> str:
        """Format technical references (issues, hex, env vars)."""
        pass
```

### 4. Renderer Integration

**Modified**: `src/claude_agent_sdk/rendering/formatters.py`

**Changes**:
```python
class MessageFormatter:
    def __init__(self, config: RendererConfig):
        self.config = config
        self.theme = config.theme

        # Existing
        self.syntax_highlighter = SyntaxHighlighter(theme)

        # NEW
        self.ui_element_formatter = UIElementFormatter(theme, semantic_mapping)
        self.pattern_detector = PatternDetector()  # From Story 9

    def format_tool_use(self, tool_use: ToolUseBlock) -> str:
        """Format tool call with semantic UI styling."""
        # Detect if large response → add warning
        # Apply green bullet
        # Use ui_element_formatter
        pass

    def format_text_block(self, text: str) -> str:
        """Format text with pattern detection and semantic roles."""
        # Detect patterns (Story 9)
        # Apply semantic roles
        # Use ui_element_formatter for UI elements
        # Use syntax_highlighter for code blocks
        pass
```

---

## Sprint Plan Impact

### New Stories Required

#### Story 4.5: Semantic Role Taxonomy & Detection
**Time**: 1.5 hours
**Dependencies**: Story 4 v2
**Deliverables**:
- `SemanticRole` enum definition
- Role detection logic in `MessageFormatter`
- Integration with existing `SyntaxHighlighter`

#### Story 4.6: UI Element Formatter
**Time**: 2.5 hours
**Dependencies**: Story 4.5
**Deliverables**:
- `UIElementFormatter` class
- Bullet formatting (colored ●)
- Warning formatting (⚠️ + yellow)
- Emphasis formatting (bold, italic)
- Technical reference formatting (cyan)

#### Story 9 Enhancement: Pattern-to-Role Mapping
**Time**: +0.5 hours (add to existing 2.5h = 3h total)
**Dependencies**: Story 4.5
**Deliverables**:
- Map detected patterns to semantic roles
- Integration with `UIElementFormatter`

### Updated Sprint Metrics

| Metric | Phase 1 | Phase 2 | Total |
|--------|---------|---------|-------|
| Stories | 11 | +2 (4.5, 4.6) | **13** |
| Duration | 12.25h | +4.5h | **16.75h** |
| Scope | Code syntax + JSON/YAML | + UI elements | **Complete** |

### Updated Dependency Graph

```
Story 1 (COMPLETED) ✅
  ↓
Story 2 (Theme)
  ↓
  ├─→ Story 4 v2 (Syntax - 5 modules) ──────┐
  │     ↓                                    │
  │   Story 4.5 (Semantic Roles) ─────┐     │
  │     ↓                              │     │
  │   Story 4.6 (UI Formatter) ────────┤     │
  │     ↓                              │     │
  │   Story 11 (Cleanup)               │     │
  │                                    │     │
  ├─→ Story 3 (Tool Formatting) ───────┼─────┤
  ├─→ Story 5 (System Messages) ───────┼─────┤
  ├─→ Story 6 (Bullet Indentation) ────┼─────┼─→ Story 7 (Tests)
  └─→ Story 9 (Pattern Detection) ─────┘     │       ↓
                                              │   Story 8 (Docs)
                                              │       ↓
                                              └─→ Story 12 (Arch Docs)
                                                  [MUST BE LAST]
```

---

## Questions for Next Agent

### Architecture Decisions

1. **Option Preference**: Do we extend Story 4 v2 (Option A), create parallel module (Option B), or integrate at renderer level (Option C)?
   - **Recommendation**: Option C (renderer-level) based on user research

2. **Story Structure**: Should we create Story 4.5 & 4.6, or fold into existing stories?
   - **Recommendation**: Separate stories for clear dependency tracking

3. **Pattern Detection Integration**: How tightly should Story 9 integrate with semantic roles?
   - **Recommendation**: Story 9 detects patterns, Story 4.6 applies role-based styling

### Implementation Questions

1. **Semantic Role Detection**: Where in the pipeline does role detection happen?
   - **Recommendation**: In `MessageFormatter` before calling formatters

2. **Theme Mapping**: Should semantic roles use same `SemanticMapping` as syntax highlighting?
   - **Recommendation**: Yes, extend existing `SemanticMapping` with UI role mappings

3. **Backward Compatibility**: How do we ensure existing code still works?
   - **Recommendation**: Default roles to existing theme categories, opt-in for advanced features

---

## Critical Context to Preserve

### What the User Cares About

1. **Comprehensive Language Support**: Must support all languages, not just a select few
2. **Clean Architecture**: Modular design with separation of concerns
3. **Extensibility**: Easy to add new languages, roles, patterns without code changes
4. **Documentation as Last Step**: Prevents drift from refactoring (Story 12 strategy)
5. **Claude CLI Parity**: Match Claude Code CLI's rendering exactly

### What We've Solved

✅ Unlimited language support (500+ via Pygments)
✅ Modular architecture (5 focused modules)
✅ Zero code duplication (unified pipeline)
✅ Extensible semantic mapping (dict-based, customizable)
✅ Documentation-as-last-step strategy

### What We Need to Solve

❌ Semantic UI element coloring (tool calls, warnings, references)
❌ Integration with pattern detection (Story 9)
❌ Renderer-level semantic role detection
❌ UI element formatter module
❌ Complete Claude CLI parity for structured output

---

## Reference Documents

### Phase 1 (Completed)
- **Sprint Plan**: `.claude/implementation/index.md`
- **Story 4 v2**: `.claude/implementation/stories/4-unified-syntax-semantic-highlighting.md`
- **Architecture Summary**: `.claude/implementation/SPRINT-1.5-ARCHITECTURE-REDESIGN-SUMMARY.md`
- **Archive Rationale**: `.claude/implementation/archive/2025-11-08-2344/ARCHIVE-REASON.md`
- **Story 9**: `.claude/implementation/stories/9-pattern-detection.md`
- **Story 12**: `.claude/implementation/stories/12-architecture-documentation.md`

### User Research (This Session)
- User screenshot analysis (semantic UI coloring patterns)
- User research insight (renderer-side processing)
- Proposed architecture diagram
- Color mapping specifications

---

## Recommended Next Steps

1. **Review this handoff** to understand the full context
2. **Read Story 4 v2** (`.claude/implementation/stories/4-unified-syntax-semantic-highlighting.md`) to understand existing architecture
3. **Read Story 9** (`.claude/implementation/stories/9-pattern-detection.md`) to understand pattern detection
4. **Make architecture decision**: Option A, B, or C for semantic UI coloring
5. **Create Story 4.5**: Semantic Role Taxonomy & Detection
6. **Create Story 4.6**: UI Element Formatter
7. **Update Story 9**: Add pattern-to-role mapping
8. **Update Sprint Index**: New stories, dependencies, metrics
9. **Perform QA**: Ensure architecture is comprehensive and extensible
10. **Create handoff summary**: Document decisions and next implementation steps

---

## Success Criteria

When this phase is complete, the architecture should support:

✅ All programming language syntax highlighting (Phase 1)
✅ Semantic UI element coloring (Phase 2)
✅ Pattern detection with role mapping (Story 9 enhanced)
✅ Tool call headers with colored bullets and warnings
✅ Technical reference highlighting (issues, hex codes, env vars, repos)
✅ Emphasis and bold text
✅ Consistent theme-based coloring across all elements
✅ Clean separation: detection → role assignment → formatting → styling
✅ Extensible for new roles and patterns
✅ Complete Claude CLI parity

---

**Handoff Status**: ✅ Ready for next agent
**Priority**: HIGH
**Estimated Work**: 4.5 hours (Stories 4.5, 4.6, Story 9 enhancement)
**Complexity**: Medium-High (architectural integration)
**Risk**: Low (builds on solid Phase 1 foundation)

**Note**: This handoff preserves all critical context about the architecture challenge. The next agent should have enough context to make architectural decisions, create new stories, update the sprint plan, and perform QA without needing to re-research.

---

**Document Version**: 1.0
**Created**: 2025-11-09 00:15
**Author**: Claude QA Agent (Phase 1)
**For**: Next Agent (Phase 2)
