# Gap Analysis: Semantic UI Coloring Research

**Date**: 2025-11-09 11:15
**Phase 1 Quick Search**: COMPLETE (15 queries)
**Status**: Analyzing gaps for deep research needs

---

## What We Successfully Discovered

### ✅ Technology Stack (HIGH CONFIDENCE)

| Component | Technology | Evidence | Confidence |
|-----------|-----------|----------|------------|
| **Renderer** | Ink (React for CLI) | Issue #127, #9812 | **VERY HIGH** |
| **Coloring** | Chalk (ANSI library) | Issue #6214, #1341, ccstatusline deps | **VERY HIGH** |
| **Streaming** | JSONL (JSON Lines) | Rust/Go parsers, SDK docs | **VERY HIGH** |
| **Testing** | ink-visual-testing + node-pty | Issue #9812 | **HIGH** |

### ✅ Architecture Pattern (HIGH CONFIDENCE)

**Confirmed Pipeline**:
```
LLM Output → JSONL Stream → Parser → Ink Components → Chalk Styling → Terminal
```

**Key Validation**:
- Renderer-side processing (not LLM-generated colors)
- Separation of concerns (structure vs presentation)
- **Supports Option C from handoff** (renderer-level integration)

### ✅ Color Capability Detection (HIGH CONFIDENCE)

| Capability | Detection Method | Evidence |
|------------|-----------------|----------|
| **24-bit RGB** | COLORTERM=truecolor | Medium article |
| **256-color** | $TERM detection | Medium article |
| **16-color** | Fallback | Inferred |
| **Monochrome** | No color support | Inferred |

**Environment Variables**: `$COLORTERM`, `$TERM`, `$LS_COLORS`

### ✅ Output Formats (MEDIUM CONFIDENCE)

| Format | Usage | Evidence |
|--------|-------|----------|
| **text** | Human-readable (default) | CLI reference |
| **json** | Structured output | CLI reference |
| **stream-json** | JSONL streaming | Multiple parsers |

### ✅ General UI Conventions (MEDIUM CONFIDENCE)

- **Bullet points**: Used for lists (●)
- **Numbered lists**: Used for sequences
- **Sections**: Headers with bold/emphasis
- **Concise style**: Direct, to-the-point
- **Bright ANSI**: Preferred for visibility

### ✅ Tool Call Lifecycle (MEDIUM CONFIDENCE)

1. **Registration**: `claude mcp add`
2. **Permission Handling**: `--dangerously-skip-permissions`
3. **Execution**: SSE (Server-Sent Events) streaming
4. **Logging**: JSONL format
5. **Verbose Mode**: `--verbose` for full lifecycle

### ✅ JSON Truncation (HIGH CONFIDENCE)

**Fixed Thresholds**: 4k, 6k, 8k, 10k, 12k, 16k characters
**Issue**: Causes JSON parsing failures (GitHub #913)

---

## Critical Gaps Requiring Deep Research

### ❌ Gap 1: Semantic Role Taxonomy (CRITICAL)

**What We Need**:
- Complete list of semantic roles (tool_call, warning, error, success, etc.)
- Role definitions and usage patterns
- Role hierarchy/relationships

**What We Know**:
- Green used for success/good states (par-cc-usage)
- Yellow used for warnings (screenshot analysis)
- White bullets for sections
- Gray/dim for subsections

**Evidence Quality**: LOW - Inferred from scattered sources

**Impact**: **BLOCKING** - Can't design SemanticRole enum without taxonomy

---

### ❌ Gap 2: Chalk Color Mappings (CRITICAL)

**What We Need**:
- Semantic role → Chalk method mapping
- Specific chalk API calls used (e.g., `chalk.green.bold()`, `chalk.yellow()`)
- Color combinations for complex UI elements

**What We Know**:
- Chalk library is used
- Background color bleed issues exist (#1341)
- Bright ANSI colors preferred

**Evidence Quality**: LOW - Know library, not mappings

**Impact**: **BLOCKING** - Can't implement UIElementFormatter without color specs

---

### ❌ Gap 3: Ink Component Structure (HIGH PRIORITY)

**What We Need**:
- Specific Ink components used (Box, Text, Newline, etc.)
- Component hierarchy for messages
- Layout patterns (flex, padding, margins)
- Nested component structures

**What We Know**:
- Ink is the rendering framework
- TTY detection before initialization
- Visual testing with node-pty

**Evidence Quality**: LOW - Know framework, not structure

**Impact**: HIGH - Needed for renderer architecture design

---

### ❌ Gap 4: JSONL Message Schema (HIGH PRIORITY)

**What We Need**:
- Message type field names (`type`, `tool`, `status`, etc.)
- Schema for different message types (tool_call, tool_result, text, etc.)
- Metadata fields for semantic roles
- UI affordance markers (truncation, expansion hints)

**What We Know**:
- JSONL format confirmed
- Truncation at specific thresholds
- Parsers exist in multiple languages

**Evidence Quality**: LOW - Format known, schema unknown

**Impact**: HIGH - Needed for MessageFormatter role detection

---

### ❌ Gap 5: Tool Call Header Format (MEDIUM PRIORITY)

**What We Need**:
- Bullet character (●) and color (green vs white)
- Tool name formatting
- Description formatting
- Status indicators (pending, success, error)
- Warning format (⚠️ + yellow text)
- Large response threshold (~11.5k tokens)

**What We Know**:
- Tool call headers exist (from screenshot)
- MCP tool integration
- SSE streaming

**Evidence Quality**: MEDIUM - Screenshot analysis, no spec

**Impact**: MEDIUM - Specific UI element, not architectural

---

### ❌ Gap 6: Technical Reference Patterns (MEDIUM PRIORITY)

**What We Need**:
- Regex patterns for detection:
  - Issue numbers: `#\d+`
  - Hex colors: `#[0-9A-Fa-f]{6}`
  - Env variables: `[A-Z_][A-Z0-9_]*`
  - Repo paths: `[\w-]+/[\w-]+`
- Detection triggers (when to scan for patterns)
- Coloring for each pattern type (cyan, green, etc.)

**What We Know**:
- Patterns appear in output (#2081, $COLORTERM)
- No evidence of automatic detection/styling

**Evidence Quality**: VERY LOW - Usage inferred, no detection found

**Impact**: MEDIUM - Nice-to-have feature, not core architecture

---

### ❌ Gap 7: Emphasis & Typography (LOW PRIORITY)

**What We Need**:
- Bold text rendering (`**text**`)
- Italic rendering (`*text*` or `_text_`)
- Underline support
- Strikethrough support
- Inline code (`\`code\``)

**What We Know**:
- Bold mentioned in screenshot analysis
- Concise, direct style preferred

**Evidence Quality**: LOW - Mentioned, not specified

**Impact**: LOW - Markdown-style formatting, well-understood

---

## Gap Severity Matrix

| Gap | Priority | Blocking | Deep Research Needed | Estimated Queries |
|-----|----------|----------|---------------------|-------------------|
| **1. Semantic Role Taxonomy** | CRITICAL | ✅ YES | ✅ YES | 2-3 |
| **2. Chalk Color Mappings** | CRITICAL | ✅ YES | ✅ YES | 2-3 |
| **3. Ink Component Structure** | HIGH | ❌ NO | ✅ YES | 1-2 |
| **4. JSONL Message Schema** | HIGH | ❌ NO | ✅ YES | 1-2 |
| **5. Tool Call Header Format** | MEDIUM | ❌ NO | ⚠️ MAYBE | 0-1 |
| **6. Technical Reference Patterns** | MEDIUM | ❌ NO | ⚠️ MAYBE | 0-1 |
| **7. Emphasis & Typography** | LOW | ❌ NO | ❌ NO | 0 |

**Total Deep Research Queries Needed**: **6-12 queries**

---

## Research Strategy Recommendation

### Phase 2A: Critical Deep Research (BLOCKING - 4-6 queries)

**Must-Have for Architecture Design**:

1. **Semantic Role Taxonomy + Chalk Mappings**
   - Query: "Claude Code CLI complete semantic role taxonomy including tool calls, warnings, errors, success indicators, and their corresponding ANSI color codes and chalk method mappings"
   - **OR** Query: "Claude Code CLI renderer semantic coloring system including role definitions and chalk color API usage patterns"

2. **Ink Component Architecture**
   - Query: "Claude Code CLI Ink component structure and hierarchy for rendering messages, tool calls, code blocks, and structured output including layout patterns"

3. **JSONL Message Schema**
   - Query: "Claude Code CLI stream-json message schema including type field definitions, tool call metadata, status indicators, and UI affordance markers"

### Phase 2B: Implementation Details (OPTIONAL - 2-4 queries)

**Nice-to-Have for Complete Implementation**:

4. **Tool Call Rendering**
   - Query: "Claude Code CLI tool call header rendering including bullet colors, status indicators, warning format, and large response handling"

5. **Pattern Detection**
   - Query: "Claude Code CLI technical reference detection patterns for issue numbers, hex colors, environment variables, and repository paths with highlighting conventions"

### Alternative: Source Code Research (2-3 queries)

Instead of feature-focused queries, search for implementation:

1. **Source Code** (if available)
   - Query: "anthropic claude-code github source code renderer chalk colors ink components"
   - Query: "claude-code open source renderer implementation message formatting"

2. **Developer Documentation**
   - Query: "Claude Code CLI developer documentation renderer architecture semantic roles theming"

---

## Recommended Approach

### Option A: Minimal Deep Research (4 queries)
- Focus on Gaps 1-4 only
- Skip tool call and pattern details
- Design based on general principles
- **Pros**: Fast, cost-effective
- **Cons**: May need assumptions for implementation

### Option B: Comprehensive Deep Research (8 queries)
- Cover Gaps 1-6
- Include implementation details
- Full spec for Story creation
- **Pros**: Complete specification
- **Cons**: Higher cost, more time

### Option C: Source Code Discovery (2-3 queries)
- Search for open-source renderer code
- Reverse-engineer from public repos
- May find complete implementation
- **Pros**: Most accurate
- **Cons**: May not find anything (Claude Code is proprietary)

---

## Recommendation

**Start with Option A (Minimal)** - 4 critical queries:
1. Semantic roles + Chalk mappings (combined)
2. Ink component structure
3. JSONL message schema
4. (Optional) Tool call rendering

**Rationale**:
- Unblocks architecture design
- Sufficient for Story 4.5, 4.6, 4.9 outlines
- Can add details during implementation if needed
- Balances quality vs cost

**Total Estimated Cost**: ~$4-8 (4 deep queries × $1-2 each)

---

## Next Steps

1. **Present gap analysis to user**
2. **Request approval for 4 deep research queries** (Option A)
3. **Execute approved deep research**
4. **Synthesize findings into final recommendations**
5. **Present architecture decision (Option C validation)**

---

**Gap Analysis Status**: ✅ COMPLETE
**Recommendation**: Option A (4 critical deep queries)
**Blocking Gaps**: 2 (Semantic roles, Chalk mappings)
**High Priority Gaps**: 2 (Ink structure, JSONL schema)
**Total Queries Needed**: 4-6
