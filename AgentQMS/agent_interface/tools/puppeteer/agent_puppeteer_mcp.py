#!/usr/bin/env python3
"""
Puppeteer MCP Server for Claude Desktop

This MCP server exposes Puppeteer browser automation capabilities to Claude.
It wraps the existing puppeteer_wrapper.py utility for MCP protocol compatibility.
"""

import json
import sys
from typing import Any

from AgentQMS.agent_tools.utils.runtime import ensure_project_root_on_sys_path

ensure_project_root_on_sys_path()

from AgentQMS.agent_tools.utilities.puppeteer_wrapper import (
    capture_page,
    run_puppeteer_script,
    verify_page,
)


class PuppeteerMCPServer:
    """MCP Server wrapper for Puppeteer browser automation."""

    def __init__(self):
        self.tools = {
            "puppeteer_capture_page": {
                "name": "puppeteer_capture_page",
                "description": "Capture page content and accessibility snapshot using Puppeteer",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to capture"},
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in seconds (default: 30)",
                            "default": 30,
                        },
                    },
                    "required": ["url"],
                },
            },
            "puppeteer_verify_page": {
                "name": "puppeteer_verify_page",
                "description": "Verify a page for errors using Puppeteer",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to verify"},
                        "page_name": {
                            "type": "string",
                            "description": "Optional page name for logging",
                            "default": "",
                        },
                    },
                    "required": ["url"],
                },
            },
            "puppeteer_run_script": {
                "name": "puppeteer_run_script",
                "description": "Run a custom Puppeteer script",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "script_path": {
                            "type": "string",
                            "description": "Path to Puppeteer JavaScript file",
                        },
                        "args": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Arguments to pass to the script",
                            "default": [],
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in seconds (default: 60)",
                            "default": 60,
                        },
                    },
                    "required": ["script_path"],
                },
            },
        }

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Handle MCP protocol request (JSON-RPC format)."""
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        def make_response(
            result: Any = None, error: dict[str, Any] | None = None
        ) -> dict[str, Any]:
            """Create JSON-RPC response."""
            response = {"jsonrpc": "2.0", "id": request_id}
            if error:
                response["error"] = error
            else:
                response["result"] = result
            return response

        if method == "initialize":
            return make_response(
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "puppeteer-mcp-server", "version": "1.0.0"},
                }
            )

        elif method == "tools/list":
            return make_response({"tools": list(self.tools.values())})

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            try:
                if tool_name == "puppeteer_capture_page":
                    url = arguments.get("url")
                    timeout = arguments.get("timeout", 30)
                    result = capture_page(url, timeout=timeout)
                    return make_response(
                        {
                            "content": [
                                {"type": "text", "text": json.dumps(result, indent=2)}
                            ]
                        }
                    )

                elif tool_name == "puppeteer_verify_page":
                    url = arguments.get("url")
                    page_name = arguments.get("page_name", "")
                    result = verify_page(url, page_name=page_name)
                    return make_response(
                        {
                            "content": [
                                {"type": "text", "text": json.dumps(result, indent=2)}
                            ]
                        }
                    )

                elif tool_name == "puppeteer_run_script":
                    script_path = arguments.get("script_path")
                    args = arguments.get("args", [])
                    timeout = arguments.get("timeout", 60)
                    result = run_puppeteer_script(script_path, *args, timeout=timeout)
                    return make_response(
                        {
                            "content": [
                                {"type": "text", "text": json.dumps(result, indent=2)}
                            ]
                        }
                    )

                else:
                    return make_response(
                        error={"code": -32601, "message": f"Unknown tool: {tool_name}"}
                    )

            except Exception as e:
                return make_response(
                    error={"code": -32603, "message": f"Internal error: {e!s}"}
                )

        else:
            return make_response(
                error={"code": -32601, "message": f"Unknown method: {method}"}
            )


def main():
    """Main entry point for MCP server."""
    server = PuppeteerMCPServer()

    # Read from stdin (MCP protocol uses JSON-RPC over stdio)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            response = server.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except json.JSONDecodeError as e:
            # Invalid JSON - send error response
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {e!s}"},
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
        except Exception as e:
            # Unexpected error
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": f"Internal error: {e!s}"},
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
