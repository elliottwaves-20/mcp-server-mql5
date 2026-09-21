from mcp.server.mcpserver import MCPServer
import subprocess
import os
import tempfile
import requests
import glob

# --- AUTO-DETECTION ---
def find_metaeditor():
    """
    Searches common MetaTrader 5 installation paths for metaeditor64.exe.
    """
    search_patterns = [
        r"C:\Program Files\MetaTrader 5*\metaeditor64.exe",
        r"C:\Program Files (x86)\MetaTrader 5*\metaeditor64.exe",
        os.path.expanduser(r"~\AppData\Roaming\MetaQuotes\Terminal\*\metaeditor64.exe"),
    ]

    for pattern in search_patterns:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]  # First installation found

    return None


# --- CONFIGURATION ---
METAEDITOR_PATH = os.getenv("MQL5_EDITOR_PATH") or find_metaeditor()

# Documentation lookups go through Context7, which serves the MQL5 reference as a
# pre-indexed library. The ID and the API host stay configurable so the server
# keeps working if the library is renamed or a self-hosted instance is used.
CONTEXT7_BASE_URL = os.getenv("CONTEXT7_BASE_URL", "https://context7.com/api/v1")
CONTEXT7_LIBRARY = os.getenv("MQL5_DOCS_LIBRARY", "/websites/mql5docs_onrender")

# Optional. Without a key the public rate limit applies, which is enough for
# occasional lookups but throttles quickly during a longer session.
CONTEXT7_API_KEY = os.getenv("CONTEXT7_API_KEY")

DEFAULT_DOC_TOKENS = 5000

mcp = MCPServer("MQL5 Developer Suite")


@mcp.tool()
def compile_mql5(code: str, filename: str = "ExpertAdvisor") -> str:
    """
    Compiles MQL5 code with the local MetaEditor and returns the exact errors
    and warnings from the compiler log, including line and column numbers.
    """
    if not METAEDITOR_PATH:
        return """CONFIGURATION ERROR: MetaEditor was not found.

Set 'MQL5_EDITOR_PATH' in your MCP configuration:

Common paths:
- C:\\Program Files\\MetaTrader 5 [YOUR_BROKER]\\metaeditor64.exe
- C:\\Program Files (x86)\\MetaTrader 5 [YOUR_BROKER]\\metaeditor64.exe

How to find your path:
1. Right-click the MetaEditor shortcut -> Properties -> copy the "Target" field
2. Add it to your MCP configuration as "MQL5_EDITOR_PATH"
"""

    if not os.path.exists(METAEDITOR_PATH):
        return f"PATH ERROR: MetaEditor not found at:\n{METAEDITOR_PATH}\nPlease check the path."

    with tempfile.TemporaryDirectory() as temp_dir:
        mq5_file = os.path.join(temp_dir, f"{filename}.mq5")
        log_file = os.path.join(temp_dir, f"{filename}.log")

        try:
            with open(mq5_file, "w", encoding="utf-8") as f:
                f.write(code)
        except Exception as e:
            return f"WRITE ERROR: {str(e)}"

        try:
            # Headless compilation
            subprocess.run(
                [METAEDITOR_PATH, f"/compile:{mq5_file}", f"/log:{log_file}"],
                check=False,
            )
        except Exception as e:
            return f"EXECUTION ERROR: {str(e)}"

        if os.path.exists(log_file):
            try:
                # MetaEditor writes UTF-16 logs
                with open(log_file, "r", encoding="utf-16") as f:
                    return f.read()
            except UnicodeError:
                with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                    return f"LOG ENCODING WARNING:\n{f.read()}"
        else:
            return "ERROR: No log file was created."


@mcp.tool()
def search_mql5_docs(search_term: str, max_tokens: int = DEFAULT_DOC_TOKENS) -> str:
    """
    Looks up the official MQL5 reference through Context7 and returns the
    matching sections, including function signatures, parameters and examples.

    Ask one concept per call ("OrderSend", "ArrayResize", "MqlTradeRequest").
    Raise max_tokens for broader topics, lower it to save context.
    """
    url = f"{CONTEXT7_BASE_URL}{CONTEXT7_LIBRARY}"
    params = {"type": "txt", "topic": search_term, "tokens": max_tokens}
    headers = {"User-Agent": "mcp-server-mql5"}
    if CONTEXT7_API_KEY:
        headers["Authorization"] = f"Bearer {CONTEXT7_API_KEY}"

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
    except requests.RequestException as e:
        return f"Documentation lookup failed: {str(e)}"

    # The status codes are reported separately because each one calls for a
    # different reaction, and a bare number tells the model nothing.
    if response.status_code == 401:
        return (
            "Context7 rejected the API key (401). Check CONTEXT7_API_KEY in your MCP "
            "configuration, or remove it to use the public rate limit."
        )
    if response.status_code == 429:
        return (
            "Context7 rate limit reached (429). Set CONTEXT7_API_KEY in your MCP "
            "configuration for a higher limit, or retry in a moment."
        )
    if response.status_code == 404:
        return (
            f"Context7 does not know the library '{CONTEXT7_LIBRARY}' (404). "
            "Override it with MQL5_DOCS_LIBRARY if the library was renamed."
        )
    if response.status_code != 200:
        return f"Documentation lookup failed with status code {response.status_code}."

    text = response.text.strip()
    if not text or text.lower().startswith("no content"):
        return (
            f"No documentation found for '{search_term}'. Try a single MQL5 identifier "
            "such as 'OrderSend', 'ArrayResize' or 'MqlTradeRequest'."
        )

    return f"SOURCE: Context7 {CONTEXT7_LIBRARY}\n\n{text}"


def main():
    mcp.run()


if __name__ == "__main__":
    main()
