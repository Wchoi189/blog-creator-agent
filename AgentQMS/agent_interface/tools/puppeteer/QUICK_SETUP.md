# Quick Setup: Puppeteer MCP for Claude Desktop

## 1. Find Your Claude Desktop Config File

**macOS:**
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
notepad %APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
nano ~/.config/Claude/claude_desktop_config.json
```

## 2. Add Puppeteer MCP Server

Add this to your `claude_desktop_config.json`:

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

**Important:** Replace `/workspaces/upstage-prompt-hack-a-thon-dev` with your actual project path!

## 3. Get Your Project Path

```bash
# From project root, run:
pwd
```

Copy the output and use it in the config file above.

## 4. Restart Claude Desktop

Close and reopen Claude Desktop for the changes to take effect.

## 5. Test It

In Claude Desktop, ask:
> "Can you use Puppeteer to capture http://localhost:8501?"

Claude should now have access to Puppeteer tools!

## Troubleshooting

**Can't find Python:**
- Use full path: `which python3` or `which python`
- Update `command` in config to use full path

**Import errors:**
- Make sure `PYTHONPATH` points to project root
- Verify script exists: `ls agent_interface/tools/puppeteer/agent_puppeteer_mcp.py`

**Node.js not found:**
- Puppeteer needs Node.js 20+: `node --version`
- Install via nvm if needed

See `README.md` for detailed documentation.

