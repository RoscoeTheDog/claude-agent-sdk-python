# Query 3: JSONL Message Schema

**Date**: 2025-11-09 12:10
**Research ID**: 85177420-8c4f-4718-b4a2-b8612166518f
**Sources**: 12
**Status**: COMPLETE

---

## Query

"Claude Code CLI stream-json message schema including type field definitions, tool call metadata, status indicators, and UI affordance markers"

---

## Key Findings

### 1. **Stream-JSON Output Format** (CRITICAL!)

**Format Confirmed**:
- **Source**: CLI Reference, comprehensive guide
- **Finding**: "`--output-format stream-json` - Streaming JSONL format"
- **Usage**: Print mode with streaming

**Output Format Options**:
1. `text` - Human-readable (default, ANSI-colored)
2. `json` - Structured JSON output
3. `stream-json` - JSON Lines (JSONL) streaming

**Print Mode with Stream-JSON**:
```bash
# Non-interactive with JSON streaming
claude -p "run tests" --output-format stream-json

# Available since v0.2.66
# Breaking change in v0.2.117: now returns nested message objects
```

### 2. **Message Object Structure** (v0.2.117+)

**Breaking Change Note**:
- **Source**: Release notes v0.2.117
- **Finding**: "Breaking change: --print JSON output now returns nested message objects, for forwards-compatibility as we introduce new metadata fields"

**Implication**:
- Previously: Flat JSON structure
- Now: Nested message objects
- Future: Additional metadata fields coming

**Current Schema** (inferred from breaking change):
```json
{
  "message": {
    "type": "...",
    "content": "...",
    "metadata": {...}
  }
}
```

### 3. **Tool Call Schema Components**

**From Anthropic Docs**:
- **Source**: docs.claude.com/tool-use/implement-tool-use
- **Finding**: JSON Schema format for tool definitions

**Tool Definition Example**:
```json
{
  "name": "get_stock_price",
  "description": "Gets the stock price for a ticker.",
  "input_schema": {
    "type": "object",
    "properties": {
      "ticker": {
        "type": "string",
        "description": "The stock ticker symbol, e.g. AAPL for Apple Inc."
      }
    },
    "required": ["ticker"]
  }
}
```

**Tool Call/Result Lifecycle**:
```json
// Tool call from Claude
{
  "type": "tool_use",
  "id": "toolu_01234...",
  "name": "get_stock_price",
  "input": {"ticker": "AAPL"}
}

// Tool result back to Claude
{
  "type": "tool_result",
  "tool_use_id": "toolu_01234...",
  "content": "150.25"
}
```

**ID Matching**:
- **Source**: Release notes v1.0.84
- **Finding**: "Fix tool_use/tool_result id mismatch error when network is unstable"
- **Implication**: Tool calls and results matched by ID field

### 4. **Tool Input Schema Constraints**

**Schema Limitations**:
- **Source**: GitHub Issue #3940
- **Finding**: "tools.45.custom.input_schema: input_schema does not support oneOf, allOf, or anyOf at the top level"

**Supported JSON Schema**:
- `type: "object"`
- `properties: {...}`
- `required: [...]`
- `additionalProperties: false`

**NOT Supported at Top Level**:
- `oneOf`
- `allOf`
- `anyOf`

**Error Example**:
```
Error: 400 {"type":"error","error":{
  "type":"invalid_request_error",
  "message":"tools.45.custom.input_schema: input_schema
   does not support oneOf, allOf, or anyOf at the top level"
}}
```

### 5. **MCP Tool Integration**

**MCP Tool Schema**:
- **Source**: Comprehensive guide, MCP docs
- **Finding**: "MCP servers are configured in `.claude/agents/` directory"

**MCP Configuration Example**:
```json
{
  "mcpServers": {
    "google-drive": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-google-drive"],
      "env": {...}
    }
  }
}
```

**Tool Availability**:
- **Discovery**: MCP tools loaded at session start
- **Permission**: Managed through settings
- **Errors**: "Invalid Tool Input Schema" if schema malformed

### 6. **Tool Runner Pattern** (Beta)

**From Anthropic Docs**:
- **Finding**: "The tool runner provides an out-of-the-box solution for executing tools with Claude"

**Tool Runner Flow**:
```python
# Tool runner automatically:
# 1. Executes tools when Claude calls them
# 2. Handles the request/response cycle
# 3. Manages conversation state
# 4. Provides type safety and validation

from anthropic import Anthropic

@beta_tool
def calculate_sum(left: int, right: int) -> str:
    """Adds two integers together."""
    return str(left + right)

# Tool runner iterates over tool calls
for event in tool_runner():
    if event.type == "tool_use":
        # Execute and return result
        ...
```

**Automatic JSON Schema Generation**:
```json
{
  "name": "calculate_sum",
  "description": "Adds two integers together.",
  "input_schema": {
    "type": "object",
    "properties": {
      "left": {"type": "integer", "description": "The first integer to add."},
      "right": {"type": "integer", "description": "The second integer to add."}
    },
    "required": ["left", "right"],
    "additionalProperties": false
  }
}
```

### 7. **Built-in Tools Available**

**From Comprehensive Guide**:

| Tool | Purpose | Permission Required |
|------|---------|---------------------|
| Read | Read files, images, PDFs | No |
| Write | Create new files | Yes |
| Edit | Modify existing files | Yes |
| Bash | Execute shell commands | Yes |
| Grep | Search content with regex | No |
| Glob | Find files by pattern | No |
| TodoWrite | Task management | No |
| Task | Launch sub-agents | No |
| WebFetch | Fetch web content | Yes |
| WebSearch | Search the web | Yes |
| NotebookEdit | Edit Jupyter notebooks | Yes |
| NotebookRead | Read Jupyter notebooks | No |

**Tool Permission Schema**:
```json
{
  "permissions": {
    "allowedTools": [
      "Read",
      "Write",
      "Bash(git *)"
    ],
    "deny": [
      "Read(./.env)",
      "Write(./production.config.*)"
    ]
  }
}
```

### 8. **JSONL Log Format**

**From Quick Scan Batch 2**:
- **Finding**: "Claude Code generates JSONL log files"
- **Tools**: `claude-code-usage` analyzes JSONL logs for usage/cost reports

**Log Location**: Session logs stored for:
- Usage monitoring
- Cost tracking
- Session search and resume
- Observability and tracing

**Verbose Mode Output**:
- **Flag**: `--verbose`
- **Finding**: "reveals the entire lifecycle of your AI interactions"
- **Content**:
  - Authentication flows
  - Connection attempts
  - Protocol-level communications
  - Tool execution details

### 9. **Session Management Fields**

**Session Commands**:
- `/help` - Available commands
- `/exit` - End session
- `/compact` - Reduce context
- `/microcompact` - Smart cleanup
- `/clear` - Reset session
- `/cost` - Token costs

**Continue/Resume**:
```bash
# Continue most recent
claude --continue
claude -c

# Resume specific session
claude --resume "abc123"
claude -r "abc123" "continue task"
```

**Session Metadata** (inferred):
- Session ID
- Conversation history
- Context size tracking
- Cost accumulation
- Timestamp information

### 10. **Debug Mode and Logging**

**Debug Flag** (v0.2.117+):
- **Flag**: `--debug`
- **Purpose**: Enhanced logging
- **Output**: Detailed request/response data

**Log Request Flag** (v0.2.120+):
- **Flag**: `--log-requests`
- **Purpose**: Log all API requests
- **Use Case**: Debugging, audit trails

**Cleanup Configuration**:
- **Setting**: `settings.cleanupPeriodDays`
- **Purpose**: Session log retention
- **Default**: (Not specified in sources)

---

## JSONL Schema Synthesis

Based on all evidence, here's the inferred stream-json schema:

### Message Types

```typescript
type StreamMessage =
  | SystemMessage
  | UserMessage
  | AssistantMessage
  | ToolUseMessage
  | ToolResultMessage
  | StatusMessage
  | ErrorMessage;

interface SystemMessage {
  type: "system";
  content: string;
  timestamp: string;
}

interface UserMessage {
  type: "user";
  content: string;
  timestamp: string;
}

interface AssistantMessage {
  type: "assistant";
  content: string;
  metadata?: {
    model: string;
    thinking?: string;  // Extended thinking mode
    usage?: TokenUsage;
  };
  timestamp: string;
}

interface ToolUseMessage {
  type: "tool_use";
  id: string;  // e.g., "toolu_01234..."
  name: string;
  input: Record<string, any>;
  timestamp: string;
}

interface ToolResultMessage {
  type: "tool_result";
  tool_use_id: string;  // Matches ToolUseMessage.id
  content: string;
  is_error?: boolean;
  timestamp: string;
}

interface StatusMessage {
  type: "status";
  status: "pending" | "running" | "completed" | "error";
  message: string;
  metadata?: {
    tool?: string;
    progress?: number;
  };
  timestamp: string;
}

interface ErrorMessage {
  type: "error";
  error: {
    type: string;
    message: string;
    code?: number;
  };
  timestamp: string;
}

interface TokenUsage {
  input_tokens: number;
  output_tokens: number;
  cache_creation_input_tokens?: number;
  cache_read_input_tokens?: number;
}
```

### Tool Schema

```typescript
interface ToolDefinition {
  name: string;
  description: string;
  input_schema: {
    type: "object";
    properties: Record<string, JSONSchemaProperty>;
    required: string[];
    additionalProperties?: boolean;
  };
}

interface JSONSchemaProperty {
  type: "string" | "integer" | "number" | "boolean" | "array" | "object";
  description: string;
  title?: string;
  enum?: any[];
  items?: JSONSchemaProperty;  // For arrays
  properties?: Record<string, JSONSchemaProperty>;  // For objects
}
```

---

## Critical Gaps Still Present

### ❌ Gap 1: Complete Message Type Enumeration

**What We Still Need**:
- All possible `type` values
- Message type transitions and lifecycle
- UI-specific message types (spinners, menus, etc.)

**What We Have**:
- Core types inferred (system, user, assistant, tool_use, tool_result)
- Error message structure
- Status indicators mentioned

**Evidence Quality**: MEDIUM - Core types evident, edge cases unknown

---

### ❌ Gap 2: UI Affordance Markers

**What We Still Need**:
- Truncation indicators (11.5k token warning from gap analysis)
- Expansion hints
- Interactive element markers (clickable, navigable, etc.)
- Progress indicators schema

**What We Have**:
- Truncation thresholds (4k, 6k, 8k, 10k, 12k, 16k) from Batch 4
- Status messages exist
- Interactive menus use vim keys (j/k)

**Evidence Quality**: LOW - Features exist, schema not documented

---

### ❌ Gap 3: Metadata Fields

**What We Still Need**:
- Complete metadata field definitions
- Nested metadata structures
- Forwards-compatibility fields (mentioned in v0.2.117)

**What We Have**:
- Breaking change note about "nested message objects"
- Token usage structure (from Anthropic API docs)
- Thinking mode mentioned

**Evidence Quality**: LOW - Structure changing, incomplete documentation

---

## Confidence Assessment

| Finding | Confidence | Evidence |
|---------|-----------|----------|
| **Stream-JSON Format** | VERY HIGH | CLI reference, release notes |
| **Tool Schema Structure** | VERY HIGH | Official Anthropic docs |
| **Message Nesting (v0.2.117+)** | HIGH | Breaking change note |
| **Tool ID Matching** | HIGH | Bug fix reference |
| **Built-in Tools List** | VERY HIGH | Comprehensive guide |
| **Complete Message Types** | MEDIUM | Core types inferred |
| **UI Affordance Markers** | LOW | Features known, schema unknown |
| **Metadata Schema** | LOW | Evolving, incomplete |

---

## Recommendations

### Option A: Design Minimal Schema
- Core message types only
- Standard tool call/result pattern
- Basic status indicators

### Option B: Design Extensible Schema
- Base message interface
- Extensible metadata field
- Version field for schema evolution

### Option C: Mirror Anthropic API Messages
- Use standard Anthropic message format
- Add CLI-specific extensions
- Maintain compatibility

**Recommendation**: **Option B + C Hybrid**
- Use Anthropic API format as base (proven, documented)
- Add `metadata.ui` extension for CLI-specific fields
- Include `schema_version` for forward compatibility

---

## Proposed Schema Design

```typescript
// Base message format (Anthropic API compatible)
interface BaseMessage {
  type: string;
  content: string | ContentBlock[];
  timestamp: string;
  schema_version: "1.0";  // For evolution
  metadata?: MessageMetadata;
}

interface MessageMetadata {
  // Standard fields
  model?: string;
  usage?: TokenUsage;

  // CLI-specific extensions
  ui?: UIMetadata;
}

interface UIMetadata {
  // Semantic role for coloring
  role?: "system" | "user" | "assistant" | "tool" | "error" | "warning" | "success";

  // UI affordances
  truncated?: boolean;
  truncation_threshold?: number;
  expandable?: boolean;

  // Interactive elements
  interactive?: boolean;
  navigation_hints?: string[];

  // Progress indicators
  progress?: {
    status: "pending" | "running" | "completed" | "error";
    percent?: number;
    message?: string;
  };

  // Syntax highlighting hints
  syntax?: {
    language?: string;
    theme?: string;
  };
}
```

---

## Sources Summary

| Source Type | Count | Key Topics |
|------------|-------|-----------|
| **Official Docs** | 4 | Tool use, CLI reference, messages API |
| **Release Notes** | 3 | Breaking changes, bug fixes, new features |
| **GitHub Issues** | 2 | Schema errors, tool ID mismatches |
| **Comprehensive Guide** | 2 | Tools reference, permissions |
| **AWS Bedrock Docs** | 1 | Message format, system prompts |

**Total**: 12 sources

---

**Research Status**: ✅ COMPLETE (Core schema inferred, recommend extensible design)
**Next Query**: Tool Call Rendering Details
