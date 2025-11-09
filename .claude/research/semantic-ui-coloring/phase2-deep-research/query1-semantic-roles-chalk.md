# Query 1: Semantic Roles & Chalk Color Mappings

**Date**: 2025-11-09 12:00
**Research ID**: d78cf92d-3267-4414-ba84-8f17005067a0
**Sources**: 20
**Status**: COMPLETE

---

## Query

"Claude Code CLI complete semantic role taxonomy including tool calls, warnings, errors, success indicators, and their corresponding ANSI color codes and chalk method mappings"

---

## Key Findings

### 1. **Technology Stack Confirmed** (CRITICAL!)

**Chalk for ANSI Coloring**:
- **Source**: GitHub Issue #881, #6214
- **Finding**: "color ansi codes were not rendered properly", "Background color bleed in terminal from chalk usage #1341"
- **Implication**: **Claude Code uses Chalk library for all ANSI color formatting**

**Color Rendering Issues**:
- **Background color bleed**: Known issue with chalk usage (Issue #1341)
- **ANSI escape sequences**: Terminal compatibility issues with certain patterns
- **Combined sequences work better**: `\e[42;30m` format preferred over `\e[42m\e[30m`

### 2. **Terminal Color Capability Detection**

**Environment Variables**:
- `COLORTERM=truecolor` - Signals 24-bit RGB support
- `$TERM` - Terminal type detection
- `$LS_COLORS` - Color configuration
- **Source**: Medium article, docs

**Color Modes Supported**:
1. **24-bit RGB (truecolor)**: Full palette
2. **256-color**: Limited palette
3. **16-color**: Basic ANSI
4. **Monochrome**: No colors

### 3. **Semantic UI Patterns Discovered**

#### Output Styles System
- **Source**: Official docs, output-styles reference
- **Finding**: "Output styles allow you to use Claude Code as any type of agent while keeping its core capabilities"
- **Three Built-in Styles**:
  1. **Default**: Efficient software engineering tasks
  2. **Explanatory**: Educational "Insights" mode
  3. **Learning**: Collaborative with `TODO(human)` markers

**Style Configuration**:
- Stored in `.claude/settings.local.json`
- Custom styles in `~/.claude/output-styles/` (global) or `.claude/output-styles/` (project)
- Markdown files with YAML frontmatter

#### Status Line Rendering
- **Source**: CC Statusline MCP, Issue #6466
- **Finding**: "Customizable status line formatter for Claude Code CLI with real-time metrics"
- **Capabilities**:
  - Model information display
  - Token usage tracking
  - Git status integration
  - Session timing
  - Powerline-style rendering

**Color Rendering Challenges**:
- Washed-out or missing background colors in Claude Code terminal
- Poor foreground/background contrast
- Separator arrows appearing in wrong colors
- **Workaround**: Use combined ANSI escape sequences

### 4. **Tool Permission and UI Indicators**

**Settings Schema**:
```json
{
  "model": "claude-sonnet-4-20250514",
  "maxTokens": 4096,
  "permissions": {
    "allowedTools": ["Read", "Write", "Bash(git *)"],
    "deny": ["Read(./.env)", "Write(./production.config.*)"]
  }
}
```

**Tool Categories**:
- **Read/Search** (No permission): Read, Grep, Glob, NotebookRead
- **Write/Modify** (Yes permission): Write, Edit, NotebookEdit
- **Execute** (Yes permission): Bash
- **External** (Yes permission): WebFetch, WebSearch
- **Management** (No permission): TodoWrite, Task

### 5. **CLI Output Formatting**

**Output Formats**:
- `text` - Human-readable (default)
- `json` - Structured output
- `stream-json` - JSONL streaming

**Print Mode**:
- Flag: `-p` or `--print`
- Non-interactive, single query
- `--output-format` control
- `--no-color` disables ANSI

**Verbose Mode**:
- Flag: `--verbose`
- Shows full tool lifecycle
- Authentication flows visible
- Protocol-level communications

### 6. **Session Management UI Elements**

**Commands**:
- `/help` - Show available commands
- `/exit` - End session
- `/compact` - Reduce context size
- `/microcompact` - Smart context cleanup
- `/clear` - Reset session
- `/cost` - Show token costs

**Status Indicators**:
- Session cost info in status line (v1.0.85+)
- Token usage tracking
- Progress spinners
- "Shimmering spinner" (v1.0.83+)

### 7. **Semantic Role Inferences**

Based on the research, we can infer these semantic roles (not explicitly documented but evident from patterns):

1. **System Messages**:
   - Status updates (model, token counts)
   - Permission prompts
   - Error messages

2. **Tool Execution**:
   - Tool call headers
   - Tool results
   - Background task indicators

3. **Code Output**:
   - Syntax highlighting (language-specific)
   - Diff rendering
   - File paths and line numbers

4. **Interactive Elements**:
   - Menus (vim-style j/k navigation)
   - Selection prompts
   - @-mention autocomplete

5. **Metadata Display**:
   - Git branch/status
   - File paths
   - Timestamps

### 8. **ANSI Escape Sequence Patterns**

**Working Pattern** (from Issue #6466):
```bash
# Combined escape sequence - WORKS in Claude Code
printf '\e[42;30m +10 \e[0m'  # Green bg, black fg
printf '\e[32;41m'              # Separator transition
printf '\e[41;97m -5 \e[0m\n'  # Red bg, white fg
```

**Problematic Pattern** (FAILS in Claude Code):
```bash
# Separate escape sequences - FAILS in Claude Code
printf '\e[42m\e[30m +10 \e[0m'  # Green bg, black fg
printf '\e[32m\e[41m'             # Separator transition
printf '\e[41m\e[97m -5 \e[0m\n' # Red bg, white fg
```

---

## Critical Gaps Still Present

### ❌ Gap 1: Explicit Semantic Role Taxonomy

**What We Still Need**:
- Complete enumeration of semantic roles (e.g., `tool_call`, `warning`, `error`, `success`)
- Formal role definitions and when each is used
- Role hierarchy and relationships

**What We Have**:
- Inferred roles from UI patterns
- General categories (system, tool, code, interactive, metadata)
- No formal specification

**Evidence Quality**: MEDIUM - Strong patterns but no official taxonomy

---

### ❌ Gap 2: Chalk Method Mappings

**What We Still Need**:
- Semantic role → Chalk API method mapping
- Specific calls (e.g., `chalk.green.bold()`, `chalk.yellow()`, `chalk.dim()`)
- Color combinations for complex UI elements

**What We Have**:
- Confirmation Chalk is used
- ANSI escape sequence patterns
- Color rendering best practices

**Evidence Quality**: MEDIUM - Library confirmed, methods not documented

---

## Confidence Assessment

| Finding | Confidence | Evidence |
|---------|-----------|----------|
| **Chalk Library Used** | VERY HIGH | Multiple GitHub issues, deps |
| **Color Capability Detection** | HIGH | Environment variables documented |
| **ANSI Rendering Patterns** | HIGH | Issue #6466 detailed analysis |
| **Output Styles System** | VERY HIGH | Official documentation |
| **Tool Permission Schema** | VERY HIGH | Settings docs, examples |
| **Semantic Role Taxonomy** | LOW | Inferred from patterns, not documented |
| **Chalk Method Mappings** | LOW | No source code or specs found |

---

## Next Steps

1. **Option A**: Proceed with inferred semantic roles and ANSI patterns
2. **Option B**: Attempt source code analysis of Claude Code CLI
3. **Option C**: Design extensible taxonomy based on common patterns
4. **Option D**: Request clarification from Anthropic

**Recommendation**: **Option C** - Design based on strong evidence, make extensible

---

## Sources Summary

| Source Type | Count | Key Topics |
|------------|-------|-----------|
| **GitHub Issues** | 4 | ANSI rendering, chalk usage, color bugs |
| **Official Docs** | 6 | CLI reference, output styles, settings |
| **Medium Articles** | 3 | Color configuration, COLORTERM |
| **Community Tools** | 2 | ccstatusline, powerline |
| **Stack Overflows** | 2 | ANSI escape sequences |
| **Release Notes** | 3 | Feature additions, bug fixes |

**Total**: 20 sources

---

**Research Status**: ✅ COMPLETE (Gaps identified, proceed with recommendations)
**Next Query**: Ink Component Structure
