# Pretty Printer Demo Guide

Welcome! This guide will help you test the new pretty printer features added in Sprint 1.

## Quick Start (30 seconds)

For a fast demo, run:

```bash
python quick_demo.py
```

This shows the simplest usage - just one line of code for beautiful output!

## Full Demo (5-10 minutes)

For a comprehensive showcase of all features, run:

```bash
python demo_pretty_printer.py
```

This interactive demo includes:

1. **Simple Usage** - `display_message()` convenience function
2. **Render Levels** - MINIMAL, STANDARD, DETAILED verbosity
3. **Multiple Destinations** - Console + file simultaneously
4. **Custom Configuration** - Customize bullets, limits, settings
5. **Tool Use Formatting** - Beautiful tool call/result display
6. **UTF-8 Characters** - Showcase of Unicode formatting
7. **Before/After** - Compare raw vs formatted output

## Demo Features

### Demo 1: Simple Usage
```python
display_message(message)  # That's it!
```

Shows how easy it is to get started.

### Demo 2: Render Levels

Demonstrates three verbosity levels:
- **MINIMAL**: Only user/assistant text
- **STANDARD**: + tool names and summaries (default)
- **DETAILED**: + full tool inputs/outputs

### Demo 3: Multiple Handlers

Shows how to send output to multiple destinations:
- Console with STANDARD level (concise)
- File with DETAILED level (verbose)

Output file: `demo_output.txt` (automatically created)

### Demo 4: Custom Configuration

Examples of customization:
- Compact mode
- Text length limits
- Custom bullet characters
- Metadata display toggles

### Demo 5: Tool Use

Watch the pretty printer format tool calls beautifully:
```
● Read(file_path: "test.py", limit: 100)
  ⎿  File content line 1
     File content line 2
     ... +5 lines (ctrl+o to expand)
```

### Demo 6: UTF-8 Characters

Showcases the Unicode characters used:
- ● (U+25CF) - Bullet points
- ⎿ (U+23BF) - Tree connectors
- → (U+2192) - Arrows
- … (U+2026) - Ellipsis
- · (U+00B7) - List bullets

### Demo 7: Before/After

Side-by-side comparison of raw message output vs pretty printed output.

## Output Files

After running the demos, you'll see:

- `demo_output.txt` - Detailed output from Demo 3
- `pretty_printer_output.txt` - Output from examples/pretty_printer_basic.py (if run)

These files demonstrate the FileHandler writing to disk.

## Testing Different Scenarios

### Test 1: Console Output
```bash
python quick_demo.py
```
**Expected**: Beautiful formatted output to console

### Test 2: File Output
```bash
python demo_pretty_printer.py
# Follow prompts to Demo 3
cat demo_output.txt
```
**Expected**: More detailed output in file than console

### Test 3: Tool Use
```bash
python demo_pretty_printer.py
# Follow prompts to Demo 5
```
**Expected**: Tool calls formatted with ● and ⎿ characters

### Test 4: UTF-8 Rendering
Check that your terminal displays UTF-8 correctly:
```bash
python demo_pretty_printer.py
# Follow prompts to Demo 6
```
**Expected**: Unicode characters (●, ⎿, →, …) display correctly

## Troubleshooting

### Issue: Unicode characters not displaying
**Solution**: Ensure your terminal supports UTF-8 encoding
- Windows: Use Windows Terminal or ConEmu
- macOS/Linux: Most terminals support UTF-8 by default

### Issue: "No module named 'claude_agent_sdk'"
**Solution**: Install the SDK in development mode:
```bash
pip install -e .
```

### Issue: Authentication errors
**Solution**: Ensure you have Claude Code CLI installed and authenticated:
```bash
claude-code --version
claude-code auth login
```

## Next Steps

After running the demos:

1. **Read the docs**: `docs/rendering.md` for complete documentation
2. **Try the example**: `examples/pretty_printer_basic.py` for more code examples
3. **Create your own**: Try using the pretty printer in your own code!

## Quick Reference

```python
from claude_agent_sdk.rendering import (
    display_message,      # Simple usage
    MessageRenderer,      # Advanced usage
    ClaudeCodeFormatter,  # Default formatter
    StreamHandler,        # Console output
    FileHandler,          # File output
    RendererConfig,       # Configuration
    RenderLevel,          # MINIMAL/STANDARD/DETAILED/DEBUG/ALL
)

# Simple
display_message(message)

# Advanced
renderer = MessageRenderer()
renderer.add_handler(StreamHandler(ClaudeCodeFormatter()))
renderer.render(message)
```

## Questions or Issues?

- Check `docs/rendering.md` for detailed documentation
- Look at `examples/pretty_printer_basic.py` for code examples
- Review test files in `tests/test_rendering_*.py` for usage patterns

Happy testing! 🎉
