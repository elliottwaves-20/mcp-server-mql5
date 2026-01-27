# MQL5 Developer MCP Server

A specialized Model Context Protocol (MCP) server for **MetaTrader 5 (MQL5)** developers. 
It bridges the gap between AI Assistants (Claude, Cursor, Antigravity) and your local MetaEditor.

**Maintained by [Elliott Waves 2.0]** – *Advanced Algorithmic Trading Solutions.*

## Features

1.  **Local Compilation (`compile_mql5`)**: 
    - Compiles MQL5 code locally using your installed `metaeditor64.exe`.
    - Returns exact error logs and warnings to the AI, enabling auto-fixing loops.
    - No trading account connection required (safe & fast).

2.  **Documentation Search (`search_mql5_docs`)**: 
    - Smart search via DuckDuckGo restricted to `mql5.com/docs`.
    - Fetches clean documentation without requiring API keys or Firecrawl credits.
    - Helps the AI understand parameters and syntax correctly.

## Configuration

### 1. Prerequisites
- Python installed
- `uv` installed (Recommended)
- MetaTrader 5 installed on Windows

### 2. Setup (Claude Desktop / Antigravity)

Add this to your configuration file (e.g., `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "mql5-dev": {
      "command": "uvx",
      "args": ["--from", "git+[https://github.com/DEIN_GITHUB_USERNAME/mcp-server-mql5.git](https://github.com/DEIN_GITHUB_USERNAME/mcp-server-mql5.git)", "mcp-server-mql5"],
      "env": {
        "MQL5_EDITOR_PATH": "C:\\Program Files\\MetaTrader 5\\metaeditor64.exe"
      }
    }
  }
}