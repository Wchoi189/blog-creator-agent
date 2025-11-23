# Puppeteer MCP Server Configuration Guide

This guide explains how to register Puppeteer with Claude Desktop's MCP (Model Context Protocol).

## Prerequisites

1. **Node.js 20+** installed (via nvm recommended)
2. **Puppeteer** installed in the project (`npm install` should have done this)
3. **Python 3.9+** with access to the project's scripts

## Claude Desktop Configuration

Claude Desktop reads MCP server configuration from:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Configuration Steps

1. **Create or edit the config file** (create if it doesn't exist):

```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "python3",
      "args": [
        "/workspaces/upstage-prompt-hack-a-thon-dev/agent_interface/tools/puppeteer/agent_puppeteer_mcp.py"
      ],
      "env": {
        "PYTHONPATH": "/workspaces/upstage-prompt-hack-a-thon-dev"
      }
    }
  }
}
```

2. **Adjust paths** for your system:
   - Replace `/workspaces/upstage-prompt-hack-a-thon-dev` with your actual project path
   - Use `python` instead of `python3` if that's your Python command

3. **Restart Claude Desktop** to load the new MCP server

## Available Tools

Once registered, Claude will have access to these Puppeteer tools:

### 1. `puppeteer_capture_page`
Capture page content and accessibility snapshot.

**Parameters:**
- `url` (required): URL to capture
- `timeout` (optional): Timeout in seconds (default: 30)

**Example:**
```json
{
  "name": "puppeteer_capture_page",
  "arguments": {
    "url": "http://localhost:8501",
    "timeout": 30
  }
}
```

### 2. `puppeteer_verify_page`
Verify a page for errors.

**Parameters:**
- `url` (required): URL to verify
- `page_name` (optional): Page name for logging

**Example:**
```json
{
  "name": "puppeteer_verify_page",
  "arguments": {
    "url": "http://localhost:8501",
    "page_name": "Data Explorer"
  }
}
```

### 3. `puppeteer_run_script`
Run a custom Puppeteer script.

**Parameters:**
- `script_path` (required): Path to Puppeteer JavaScript file
- `args` (optional): Array of arguments to pass to script
- `timeout` (optional): Timeout in seconds (default: 60)

**Example:**
```json
{
  "name": "puppeteer_run_script",
  "arguments": {
    "script_path": "/workspaces/upstage-prompt-hack-a-thon-dev/scripts/browser-automation/verify_fixes.js",
    "args": ["http://localhost:8501"],
    "timeout": 60
  }
}
```

## Testing the Setup

1. **Verify the MCP server starts**:
   ```bash
   python3 agent_interface/tools/puppeteer/agent_puppeteer_mcp.py
   ```

2. **Test in Claude Desktop**:
   - Ask Claude: "Can you use Puppeteer to capture http://localhost:8501?"
   - Claude should be able to use the `puppeteer_capture_page` tool

## Troubleshooting

### Server Not Found
- Check that the Python path is correct in the config
- Ensure `PYTHONPATH` includes the project root
- Verify the script file exists and is executable

### Import Errors
- Ensure Puppeteer wrapper is accessible:
  ```bash
  python3 -c "from AgentQMS.agent_tools.utilities.puppeteer_wrapper import capture_page; print('OK')"
  ```

### Node.js Not Found
- Verify Node.js 20+ is installed: `node --version`
- Ensure nvm is configured if using it

### Permission Issues
- Make the script executable: `chmod +x agent_interface/tools/puppeteer/agent_puppeteer_mcp.py`

## Alternative: Using Node.js Directly

If you prefer a Node.js-based MCP server, you can create one that directly uses Puppeteer without the Python wrapper. However, the Python wrapper provides better integration with the existing project structure.

## Integration with Cursor/VS Code

For Cursor/VS Code, add to `.vscode/settings.json`:

```json
{
  "chat.mcp.servers": {
    "puppeteer": {
      "command": "python3",
      "args": [
        "/workspaces/upstage-prompt-hack-a-thon-dev/agent_interface/tools/puppeteer/agent_puppeteer_mcp.py"
      ],
      "env": {
        "PYTHONPATH": "/workspaces/upstage-prompt-hack-a-thon-dev"
      }
    }
  }
}
```

