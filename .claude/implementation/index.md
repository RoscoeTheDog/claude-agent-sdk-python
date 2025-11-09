# Implementation Sprint: Sprint 1.5 - Color Theme Accuracy & Tool Formatting

**Created**: 2025-11-08 21:55
**Updated**: 2025-11-08 23:58 (Architecture Redesign Complete)
**Status**: active
**Sprint Goal**: Achieve complete Claude CLI feature parity with modular, extensible syntax highlighting architecture supporting 500+ languages

---

## Overview

This sprint achieves pixel-perfect replication of Claude Code CLI rendering through empirical color analysis and modular architecture redesign. Story 1 revealed critical findings, QA identified architectural gaps, leading to comprehensive architecture overhaul.

**Key Achievements**:
- ✅ Complete ANSI color mapping via live CLI analysis
- ✅ QA analysis identified architectural gaps in original plan
- ✅ Modular architecture designed for 500+ language support
- ✅ Separation of concerns: detection → tokenization → semantic mapping → styling
- ✅ Unified code path for code blocks AND tool results

**Architecture Highlights**:
- 5 clean modules with single responsibilities
- Language-agnostic semantic mapping layer
- Customizable theming per language/context
- No code duplication between formatters
- Future-proof for new languages and token types

**Dependencies**:
- Sprint 1.3 (Theming system) - COMPLETED
- Sprint 1.4 (Screen Reader Mode) - DEFERRED

**Estimated Duration**: 12.25 hours (refined after architecture redesign)

---

## Architecture Redesign Summary

**Trigger**: User QA review identified that original plan would only support 7 hard-coded languages with duplicated JSON/YAML formatters.

**Solution**: Modular architecture with:
- `LanguageRegistry`: 500+ language support via Pygments
- `TokenMapper`: Universal token → semantic category mapping
- `SemanticMapping`: Customizable semantic → theme color mapping
- `StructuredDataFormatter`: Type-aware JSON/YAML formatting
- `SyntaxHighlighter`: Orchestration layer

**Impact**: Same scope, better architecture, eliminates code duplication

**Archived**: Stories 4 & 10 (replaced by new Story 4 v2)

---

## QA Analysis

**Status**: ✅ Phase 1 Complete | ✅ Architecture Redesign Complete
**Documents**:
- [sprint-1.5-qa-analysis.md](./sprint-1.5-qa-analysis.md) - Initial QA findings
- [.claude/implementation/archive/2025-11-08-2344/ARCHIVE-REASON.md](./archive/2025-11-08-2344/ARCHIVE-REASON.md) - Architecture redesign rationale

**Critical Findings**:
- Initial QA: 7 issues identified, 2 new stories added
- Architecture QA: Monolithic design, hard-coded languages, code duplication
- **Resolution**: Modular architecture with unlimited language support

---

## Stories

### ✅ Story 1: Visual Color Analysis & Mapping
**Status**: completed | **Time**: 35 min | **File**: [stories/1-color-analysis.md](./stories/1-color-analysis.md)

Complete empirical analysis of Claude CLI colors via live output generation.

**Deliverables**:
- 690-line color mapping document (v1.2)
- Syntax highlighting mappings (keywords→blue, strings→red, etc.)
- Structured output patterns (JSON keys→gray, values→green)
- Renderer architecture analysis
- Pattern detection requirements

---

### Story 2: Update CLAUDE-CODE-DEFAULT Theme
**Status**: unassigned | **Time**: 30 min | **File**: [stories/2-update-theme.md](./stories/2-update-theme.md)

Update theme with `semantic_mapping` field and reference Story 1 findings.

**Dependencies**: Story 1 ✅

**Deliverables**:
- Add `semantic_mapping: Optional[SemanticMapping]` to Theme
- Update `claude_code_default()` to include semantic mapping
- Document as LAST STEP (Story 12 requirement)

---

### Story 3: Separate Tool Call Component Styling
**Status**: unassigned | **Time**: 2.5 hr | **File**: [stories/3-tool-formatting.md](./stories/3-tool-formatting.md)

Component-level styling for tool calls (name, params, values) plus state-based UI (green bullets, warnings).

**Dependencies**: Story 1 ✅, Story 2

**Enhanced**: Added state-based bullets, warning indicators

**Deliverables**:
- State-based bullet coloring (green for success, white for sections)
- Warning indicators for large responses
- Document as LAST STEP

---

### 🔄 Story 4: Unified Syntax & Semantic Highlighting (v2)
**Status**: unassigned | **Time**: 4 hr | **File**: [stories/4-unified-syntax-semantic-highlighting.md](./stories/4-unified-syntax-semantic-highlighting.md)
**Priority**: HIGH
**Version**: 2.0 (Replaces archived Stories 4 & 10)

Implement modular syntax highlighting architecture supporting 500+ languages.

**Dependencies**: Story 1 ✅, Story 2

**Architecture** (5 modules):
1. `language_registry.py` - Language catalog (20+ predefined, extensible to 500+)
2. `token_mapper.py` - Pygments token → semantic category (100+ mappings)
3. `semantic_mapping.py` - Semantic category → theme color (customizable)
4. `structured_formatter.py` - Type-aware JSON/YAML formatting
5. `highlighter.py` - Orchestration layer

**Key Features**:
- Unified code path for code blocks AND tool results
- No code duplication
- Clean separation of concerns
- Customizable theming per language
- Graceful degradation if Pygments not installed

**Deliverables**:
- All 5 modules implemented
- Integration with theme.py, config.py, formatters.py
- Pygments optional dependency
- Complete test suite
- **Document as LAST STEP** (module/class/method docstrings)

**Replaces**:
- ❌ Old Story 4 (archived - only 7 languages, hard-coded)
- ❌ Old Story 10 (archived - duplicate JSON/YAML formatter)

---

### Story 5: Control System Message Visibility
**Status**: unassigned | **Time**: 1 hr | **File**: [stories/5-system-message-visibility.md](./stories/5-system-message-visibility.md)

Render level controls for system messages (hide info/warning by default).

**Dependencies**: Story 2

**Deliverables**:
- Visibility controls implementation
- Document as LAST STEP

---

### Story 6: Fix Bullet List Indentation
**Status**: unassigned | **Time**: 1.5 hr | **File**: [stories/6-bullet-indentation.md](./stories/6-bullet-indentation.md)

Fix nested list indentation and multi-line wrapping.

**Dependencies**: Story 2

**Deliverables**:
- Indentation algorithm implementation
- Document as LAST STEP

---

### Story 7: Update Tests for All Changes
**Status**: unassigned | **Time**: 1 hr | **File**: [stories/7-update-tests.md](./stories/7-update-tests.md)

Update all tests for new architecture, colors, formatting, and features.

**Dependencies**: Stories 2-6, 9, 11

**Deliverables**:
- Test updates for all changes
- New tests for modular architecture
- Document test organization as LAST STEP

---

### Story 8: Update Documentation & Examples
**Status**: unassigned | **Time**: 45 min | **File**: [stories/8-update-docs.md](./stories/8-update-docs.md)

Update README, examples, API docs for all new features.

**Dependencies**: Story 7

**Deliverables**:
- Updated user-facing docs
- Migration guide (if needed)
- Document as LAST STEP

---

### 🆕 Story 9: Pattern Detection Infrastructure
**Status**: unassigned | **Time**: 2.5 hr | **File**: [stories/9-pattern-detection.md](./stories/9-pattern-detection.md)
**Priority**: HIGH

Automatic detection and highlighting of technical references (issue #s, hex codes, env vars, repos).

**Dependencies**: Story 1 ✅, Story 2

**Critical**: Required for CLI feature parity

**Deliverables**:
- Pattern detection engine
- 4+ built-in patterns
- Custom pattern support
- Document as LAST STEP

---

### 🆕 Story 11: Legacy Code Removal & Cleanup
**Status**: unassigned | **Time**: 1 hr | **File**: [stories/11-legacy-code-removal.md](./stories/11-legacy-code-removal.md)
**Priority**: MEDIUM

Remove redundant legacy code that conflicts with new modular architecture.

**Dependencies**: Story 4 (must be complete and tested)

**Deliverables**:
- Identify and remove legacy syntax highlighting code
- Remove duplicate/obsolete formatters
- Clean up imports and tests
- Document removed components for migration guide

**Safety**: Incremental removal with tests after each step

---

### 🆕 Story 12: Architecture & API Documentation
**Status**: unassigned | **Time**: 1.5 hr | **File**: [stories/12-architecture-documentation.md](./stories/12-architecture-documentation.md)
**Priority**: HIGH

Create comprehensive architecture docs AFTER all implementation complete.

**Dependencies**: ALL stories (2-11) must be completed first

**Critical Principle**: Documentation created as LAST STEP of each story to prevent drift from refactoring.

**Deliverables**:
- Per-story documentation (created during each story as final step)
- `syntax-highlighting-architecture.md` - Complete system overview
- `api-reference.md` - Public API documentation
- `extension-guide.md` - How to add languages, customize mappings
- `migration-guide.md` - Upgrading from old architecture (if applicable)
- **Documentation verification** - Re-check all docs against final code

**Verification**:
- Extract and test all code examples
- Check for documentation drift
- Validate signatures match code
- Fix any discrepancies

---

## Dependency Graph (Updated for New Architecture)

```
Story 1 (COMPLETED) ✅
  ↓
Story 2 (Update Theme - add semantic_mapping)
  ↓
  ├─→ Story 4 v2 (Unified Syntax - 5 modules) ─────┐
  │     ↓                                           │
  │   Story 11 (Legacy Cleanup)                     │
  │                                                  │
  ├─→ Story 3 (Tool Formatting) ────────────────────┤
  ├─→ Story 5 (System Messages) ────────────────────┤
  ├─→ Story 6 (Bullet Indentation) ─────────────────┼─→ Story 7 (Tests)
  └─→ Story 9 (Pattern Detection) ──────────────────┘       ↓
                                                         Story 8 (Docs)
                                                             ↓
                                                    Story 12 (Architecture Docs)
                                                    [MUST BE LAST]
```

**Execution Strategy**:
- **Phase 1**: 2 (foundation)
- **Phase 2**: 4 v2 (critical architecture)
- **Phase 3**: 11 (cleanup after 4 tested)
- **Phase 4**: 3, 5, 6, 9 (parallel - independent)
- **Phase 5**: 7 (tests all changes)
- **Phase 6**: 8 (user docs)
- **Phase 7**: 12 (architecture docs - LAST, verifies everything)

**Recommended Sequence**: 2 → 4 → 11 → {3, 5, 6, 9} → 7 → 8 → 12

---

## Sprint Metrics (Updated for Architecture Redesign)

| Metric | Original | After QA | After Architecture Redesign | Final |
|--------|----------|----------|----------------------------|-------|
| Stories | 8 | 10 | 11 | **11** |
| Duration | 6-8h | 9-12h | 12.25h | **12.25h** |
| Story 4+10 Time | 4h (separate) | 4h (separate) | 4h (unified) | **4h** |
| Languages Supported | Assumed unlimited | 7 (hard-coded) | 500+ (Pygments) | **500+** |
| Code Duplication | Unknown | High (2 formatters) | None (unified) | **None** |
| Extensibility | Unknown | Low (schema changes) | High (config changes) | **High** |
| Architecture Quality | Unknown | Monolithic | Modular (5 modules) | **Modular** |

**Value Proposition**: Same time investment, vastly superior architecture

**Architecture Benefits**:
- ✅ Unlimited language support (via Pygments catalog)
- ✅ Zero code duplication (unified pipeline)
- ✅ Clean separation of concerns (5 focused modules)
- ✅ Customizable theming (semantic mapping layer)
- ✅ Future-proof (easy to extend)

---

## Progress Log

### 2025-11-08 23:58 - Architecture Redesign Complete
- ✅ Identified architectural gaps in original plan
- ✅ Archived obsolete Stories 4 & 10 to `.claude/implementation/archive/2025-11-08-2344/`
- ✅ Created comprehensive Story 4 v2 with 5-module architecture
- ✅ Created Story 11 (Legacy Code Removal)
- ✅ Created Story 12 (Architecture Documentation)
- ✅ Updated sprint index with new metrics and dependency graph
- **Impact**: Unlimited language support, zero duplication, modular design
- **Remaining**: Implementation of Stories 2-12

### 2025-11-08 23:20 - Phase 1 QA Remediation Complete
- ✅ Comprehensive QA analysis (7 findings, 117 lines)
- ✅ All stories extracted to individual files
- ✅ Stories 9-10 created (pattern detection, structured data)
- ✅ Sprint index updated with dependency graph
- **Remaining**: Architecture redesign, implementation

### 2025-11-08 22:45 - Story 1 Enhanced
- ✅ Added structured output color mappings
- ✅ Added renderer architecture analysis
- ✅ Added diff tool color mappings
- Document v1.2 (690 lines)

### 2025-11-08 22:35 - Story 1 Completed
- ✅ Complete color mapping (35 minutes)
- ✅ SyntaxMapping design
- ✅ Implementation guidance
- Document v1.0

### 2025-11-08 21:55 - Sprint Started
- Archived Sprint 1.4
- Created Sprint 1.5 structure
- Defined initial 8 stories

---

## Architecture Documents

**Reference Documents**:
- [QA Analysis](./sprint-1.5-qa-analysis.md) - Initial critical findings
- [Archive Reason](./archive/2025-11-08-2344/ARCHIVE-REASON.md) - Architecture redesign rationale
- [Story 1: Color Analysis](./stories/1-color-analysis.md) - Complete ANSI mappings (690 lines)

**To Be Created (Story 12)**:
- `architecture/syntax-highlighting-architecture.md` - System overview
- `architecture/api-reference.md` - Public API docs
- `architecture/extension-guide.md` - How to extend
- `architecture/migration-guide.md` - Migration from old arch (if applicable)

---

## Archived Stories

**Location**: `.claude/implementation/archive/2025-11-08-2344/`

**Archived**:
- ❌ Old Story 4: Code Syntax Highlighting Infrastructure (v1)
  - Reason: Only supported 7 hard-coded languages, monolithic design
- ❌ Old Story 10: Structured Data Formatting (v1)
  - Reason: Duplicated JSON/YAML formatting instead of unified approach

**Replacement**: Story 4 v2 (Unified Syntax & Semantic Highlighting)

**Archive Document**: [ARCHIVE-REASON.md](./archive/2025-11-08-2344/ARCHIVE-REASON.md)

---

## Sprint Summary

_To be filled upon completion_

**Target Completion**: TBD
**Actual Completion**: TBD
**Total Time**: TBD
**Blockers**: None
**Key Learnings**: TBD

---

**Sprint Version**: 2.0 (Architecture Redesigned)
**Last Updated**: 2025-11-08 23:58
**Status**: Ready for implementation - modular architecture
