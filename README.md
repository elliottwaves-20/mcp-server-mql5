# MQL5 Developer MCP Server

A specialized Model Context Protocol (MCP) server for **MetaTrader 5 (MQL5)** developers.
It bridges the gap between AI assistants (Claude, Cursor, Antigravity) and your local MetaEditor.

**Maintained by [Elliott Waves 2.0]** – *Advanced Algorithmic Trading Solutions.*

## Features

1. **Local Compilation (`compile_mql5`)**
   - Compiles MQL5 code locally using your installed `metaeditor64.exe`.
   - Returns the exact compiler log with line and column numbers, error codes and
     warnings, which is what lets an assistant fix its own code instead of guessing.
   - No trading account connection required (safe and fast).
   - Code is written to a temporary directory that is removed after each call.

2. **Documentation Lookup (`search_mql5_docs`)**
   - Queries the MQL5 reference through [Context7](https://context7.com), which
     serves it as a pre-indexed library.
   - Returns function signatures, parameters, return values and examples.
   - `max_tokens` controls how much comes back per call, so broad topics and
     narrow ones both stay usable.

## Requirements

- Python 3.10 or newer
- [`uv`](https://docs.astral.sh/uv/) (recommended)
- MetaTrader 5 installed on Windows

## Setup

Add this to your MCP configuration (for example `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "mql5-dev": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/elliottwaves-20/mcp-server-mql5.git", "mcp-server-mql5"],
      "env": {
        "MQL5_EDITOR_PATH": ""
      }
    }
  }
}
```

### MetaEditor path

The server looks for MetaEditor by itself, checking these locations:

- `C:\Program Files\MetaTrader 5*\metaeditor64.exe`
- `C:\Program Files (x86)\MetaTrader 5*\metaeditor64.exe`
- `%APPDATA%\MetaQuotes\Terminal\*\metaeditor64.exe`

If none of them match — brokers install into their own folders — set the path manually:

1. Right-click the MetaEditor shortcut → **Properties** → **Shortcut** tab
2. Copy the full path from the **Target** field
3. Put it into the config and double every backslash

```json
"env": {
  "MQL5_EDITOR_PATH": "C:\\Program Files\\MetaTrader 5 [YOUR_BROKER]\\metaeditor64.exe"
}
```

### Context7 API key (optional)

Documentation lookups work without a key, subject to Context7's public rate limit.
That is fine for occasional questions but throttles during longer sessions. With a
key from [context7.com](https://context7.com), pass it through the environment —
never commit it to a repository:

```json
"env": {
  "MQL5_EDITOR_PATH": "",
  "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"
}
```

Some MCP clients resolve `${VAR}` against your system environment; others do not.
If yours does not, set the variable for your user account and let the client inherit it.

## Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `MQL5_EDITOR_PATH` | Full path to `metaeditor64.exe` | auto-detected |
| `CONTEXT7_API_KEY` | Raises the Context7 rate limit | unset (public limit) |
| `MQL5_DOCS_LIBRARY` | Context7 library ID for the MQL5 reference | `/websites/mql5docs_onrender` |
| `CONTEXT7_BASE_URL` | Context7 API host | `https://context7.com/api/v1` |

## Usage

Ask your assistant to write MQL5 code and compile it. A clean run returns:

```
Result: 0 errors, 0 warnings, 1327 ms elapsed, cpu='X64 Regular'
```

A failing one returns the diagnostics the assistant needs to correct itself:

```
TestFehler.mq5(9,15) : error 256: undeclared identifier 'UndefinierteFunktion'
TestFehler.mq5(9,36) : error 157: ')' - expression expected
TestFehler.mq5(11,4) : error 154: 'return' - semicolon expected
TestFehler.mq5(8,16) : warning 93: implicit conversion from 'string' to 'int'
Result: 3 errors, 1 warnings
```

For documentation, ask about one concept per call (`OrderSend`, `ArrayResize`,
`MqlTradeRequest`). Context7 always answers with its closest match, so an unrelated
term returns unrelated documentation rather than an error.

## Version history

### 0.2.0

- Documentation lookup moved from DuckDuckGo scraping to Context7. The old approach
  parsed search-result HTML, broke whenever DuckDuckGo answered `202` to block
  automated traffic, and truncated every page at 12,000 characters.
- Migrated to the MCP Python SDK 2.x, where `FastMCP` became `MCPServer`.
  The dependency is now pinned to `mcp>=2,<3`, because 1.x and 2.x are not
  interchangeable.
- Dropped the `beautifulsoup4` dependency; no HTML is parsed any more.
- Status codes from the documentation API (401, 404, 429) are now reported with
  what to do about them instead of a bare number.

### 0.1.2

- Automatic MetaEditor detection, PyPI entry point fix.
