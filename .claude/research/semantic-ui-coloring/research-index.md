# Semantic UI Coloring Research Index

**Research Date**: 2025-11-09
**Objective**: Understand Claude Code CLI's semantic UI element coloring system
**Strategy**: Batched quick search → gap analysis → targeted deep research

---

## Research Strategy

### Phase 1: Quick Search (Broad Coverage)
- **Batches**: 5 batches, ~20 queries total
- **Tool**: `mcp__gptr-mcp__quick_search`
- **Cost**: $ (low)
- **Duration**: ~5-30s per query

### Phase 2: Deep Research (Gap Filling)
- **Queries**: TBD (after gap analysis)
- **Tool**: `mcp__gptr-mcp__deep_research`
- **Cost**: $$ (medium)
- **Duration**: ~30s-5m per query
- **Approval**: Required before execution

---

## Token Budget Tracking

| Checkpoint | Threshold | Status | Action |
|------------|-----------|--------|--------|
| Start | 145k | ✓ | Continue |
| Checkpoint 1 | 120k | - | Review progress, adjust strategy |
| Checkpoint 2 | 100k | - | Final check before deep research |
| Checkpoint 3 | 80k | - | Emergency stop, summarize findings |

---

## Research Batches

### Batch 1: General UI Conventions (5 queries)
- **Status**: ✅ COMPLETE
- **File**: `phase1-quick-scan/batch1-general-ui.md`
- **Queries**:
  1. "Claude Code CLI" ui elements coloring scheme
  2. "Claude Code CLI" structured output formatting
  3. "Claude Code CLI" terminal rendering colors
  4. "Claude Code CLI" ANSI color mapping
  5. "Claude Code CLI" output formatting conventions

### Batch 2: Tool Call Formatting (3 queries)
- **Status**: ✅ COMPLETE
- **File**: `phase1-quick-scan/batch2-tool-calls.md`
- **Queries**:
  1. "Claude Code CLI" tool call header format
  2. "Claude Code CLI" MCP tool rendering
  3. "Claude Code CLI" tool result display

### Batch 3: Technical References (3 queries)
- **Status**: ✅ COMPLETE
- **File**: `phase1-quick-scan/batch3-technical-refs.md`
- **Queries**:
  1. "Claude Code CLI" issue number highlighting
  2. "Claude Code CLI" hex color detection
  3. "Claude Code CLI" environment variable styling

### Batch 4: Implementation Details (4 queries)
- **Status**: ✅ COMPLETE
- **File**: `phase1-quick-scan/batch4-implementation.md`
- **Queries**:
  1. "Claude Code CLI" ink components
  2. "Claude Code CLI" chalk colors
  3. "Claude Code CLI" JSONL stream parsing
  4. "Claude Code CLI" renderer architecture

### Batch 5: Source Code Research
- **Status**: ❌ SKIPPED (Not needed, sufficient findings from Batches 1-4)

---

## Gap Analysis
- **Status**: ✅ COMPLETE
- **File**: `gap-analysis.md`
- **Key Gaps**: 7 identified (2 critical, 2 high priority)
- **Recommendation**: Option A (4 deep queries)

---

## Deep Research Queries
- **Status**: ✅ COMPLETE (4/4 queries executed)
- **Files**: `phase2-deep-research/query*.md`

### Query 1: Semantic Roles & Chalk Mappings
- **Status**: ✅ COMPLETE
- **File**: `phase2-deep-research/query1-semantic-roles-chalk.md`
- **Sources**: 20
- **Key Findings**: Chalk confirmed, ANSI patterns documented, semantic roles inferred

### Query 2: Ink Component Structure
- **Status**: ✅ COMPLETE
- **File**: `phase2-deep-research/query2-ink-components.md`
- **Sources**: 16
- **Key Findings**: React + Ink + Yoga confirmed, component hierarchy inferred

### Query 3: JSONL Message Schema
- **Status**: ✅ COMPLETE
- **File**: `phase2-deep-research/query3-jsonl-schema.md`
- **Sources**: 12
- **Key Findings**: Stream-JSON format confirmed, message structure documented

### Query 4: Tool Call Rendering
- **Status**: ✅ COMPLETE
- **File**: `phase2-deep-research/query4-tool-rendering.md`
- **Sources**: 18
- **Key Findings**: Status indicators, large response handling, ANSI patterns

---

## Key Findings Summary

### Technology Stack (VERY HIGH CONFIDENCE)
- **Renderer**: Ink (React for CLI) + Yoga (Flexbox layout)
- **Coloring**: Chalk (ANSI library)
- **Format**: JSONL (stream-json output mode)
- **Build**: Bun (speed optimization)
- **Sources**: 16 independent confirmations

### Semantic Role Taxonomy (MEDIUM CONFIDENCE)
- **Inferred Roles**: system, user, assistant, tool, error, warning, success, info
- **Evidence**: UI patterns, status indicators, output styles
- **Gap**: No formal specification found
- **Recommendation**: Design extensible taxonomy based on patterns

### Color Mappings (MEDIUM CONFIDENCE)
- **ANSI Pattern**: Combined sequences (`\e[42;30m`) preferred over separate
- **Capability Detection**: COLORTERM, $TERM, $LS_COLORS
- **Known Colors**: Green (success), Red (error), Yellow (warning), Cyan (info)
- **Gap**: Exact Chalk method mappings not documented
- **Recommendation**: Map semantic roles to ANSI codes via configuration

### Component Architecture (HIGH CONFIDENCE)
- **Pattern**: React state → Ink components → ANSI output → Terminal
- **Components**: StatusLine, MessageList, InputArea, InteractiveMenu
- **Layout**: Yoga flexbox constraints
- **Gap**: Specific component names/props unknown
- **Recommendation**: Implement with standard Ink components

### Message Schema (MEDIUM CONFIDENCE)
- **Format**: Nested message objects (v0.2.117+)
- **Tool Schema**: JSON Schema with input_schema (no oneOf/allOf/anyOf at top level)
- **Lifecycle**: tool_use → tool_result (ID matching)
- **Gap**: UI affordance markers, complete metadata schema
- **Recommendation**: Extend Anthropic message format with ui.metadata

### Tool Call Rendering (HIGH CONFIDENCE)
- **Status Indicators**: ✓ (success), ✗ (error), ⚠️ (warning), ⟳ (running)
- **Bullet Styles**: ● (selected), ○ (unselected), → (separator)
- **Large Response**: ~11.5k tokens warning, truncation at 4k/6k/8k/10k/12k/16k chars
- **Gap**: Exact threshold values, complete bullet semantics
- **Recommendation**: Implement observed patterns with configurable thresholds

---

## Final Recommendations
- **File**: `final-recommendations.md`
- **Status**: IN PROGRESS

---

**Last Updated**: 2025-11-09 12:20
**Research Status**: ✅ COMPLETE (Phase 1 + Phase 2)
**Next Step**: Architecture decision and story creation
