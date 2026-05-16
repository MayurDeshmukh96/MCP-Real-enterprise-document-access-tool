#!/usr/bin/env python3
"""
MCP Server for PM Tool - Direct VS Code Integration
Listens to PM tool, exposes tasks via MCP tools
"""

import os
import asyncio
import logging
from datetime import datetime
import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.types as types

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize MCP Server
server = Server("pm-vscode-agent")

# Configuration from environment
PM_TOOL_API = os.getenv("PM_TOOL_API", "http://localhost:3000/api")
PM_TOOL_TOKEN = os.getenv("PM_TOOL_TOKEN", "")
POLLING_INTERVAL = int(os.getenv("POLLING_INTERVAL", "5"))

# Global state
current_task = None
all_pending_tasks = []
last_poll_time = None


class PMToolClient:
    """Client for PM tool API"""

    def __init__(self, base_url: str, api_token: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.client = httpx.AsyncClient(timeout=30)

    async def get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers

    async def get_pending_tasks(self, limit: int = 5) -> list:
        try:
            headers = await self.get_headers()
            response = await self.client.get(
                f"{self.base_url}/tasks",
                params={"status": "pending", "limit": limit},
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "tasks" in data:
                return data["tasks"]
            return []
        except Exception as e:
            logger.error(f"Failed to fetch pending tasks: {e}")
            return []

    async def get_task_details(self, task_id: str) -> dict:
        try:
            headers = await self.get_headers()
            response = await self.client.get(
                f"{self.base_url}/tasks/{task_id}",
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch task {task_id}: {e}")
            return {"error": str(e)}

    async def update_task_status(
        self,
        task_id: str,
        status: str,
        result: str = "",
        logs: str = "",
    ) -> dict:
        try:
            headers = await self.get_headers()
            payload = {
                "status": status,
                "updated_at": datetime.now().isoformat(),
            }
            if result:
                payload["result"] = result
            if logs:
                payload["logs"] = logs

            response = await self.client.patch(
                f"{self.base_url}/tasks/{task_id}",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            return {"error": str(e)}

    async def add_task_comment(self, task_id: str, comment: str) -> dict:
        try:
            headers = await self.get_headers()
            response = await self.client.post(
                f"{self.base_url}/tasks/{task_id}/comments",
                json={"comment": comment},
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to add comment: {e}")
            return {"error": str(e)}

    async def close(self):
        await self.client.aclose()


pm_client = PMToolClient(PM_TOOL_API, PM_TOOL_TOKEN)


# ============================================================================
# POLLING - Listens to PM Tool
# ============================================================================

async def poll_for_tasks():
    """Continuously poll PM tool for new tasks"""
    global current_task, all_pending_tasks, last_poll_time

    logger.info("🚀 Starting task polling...")
    print("\n" + "="*60)
    print("  🚀 PM TASK AGENT MCP SERVER STARTED")
    print(f"  PM Tool API: {PM_TOOL_API}")
    print(f"  Polling Interval: {POLLING_INTERVAL}s")
    print("="*60 + "\n")

    while True:
        try:
            logger.info("📡 Polling PM tool for pending tasks...")
            
            tasks = await pm_client.get_pending_tasks(limit=10)
            all_pending_tasks = tasks
            last_poll_time = datetime.now().isoformat()

            if tasks:
                current_task = tasks[0]
                logger.info(f"✅ Found {len(tasks)} pending task(s)")
                logger.info(f"   Current: {current_task.get('id')} - {current_task.get('title')}")
                
                print("\n" + "="*60)
                print("  ✅ TASKS AVAILABLE IN VS CODE MCP")
                print("="*60)
                print(f"  Current Task: {current_task.get('title')}")
                print(f"  Task ID: {current_task.get('id')}")
                print(f"  Total Pending: {len(tasks)}")
                print("="*60 + "\n")
            else:
                current_task = None
                logger.info("No pending tasks")

        except Exception as e:
            logger.error(f"Polling error: {e}")

        await asyncio.sleep(POLLING_INTERVAL)


# ============================================================================
# MCP TOOLS
# ============================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="get_current_task",
            description="Get the current pending task from PM tool to display in editor",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_all_pending_tasks",
            description="Get all pending tasks from PM tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Max tasks to return",
                    }
                },
            },
        ),
        Tool(
            name="get_task_details",
            description="Get full details of a specific task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"}
                },
                "required": ["task_id"],
            },
        ),
        Tool(
            name="update_task_status",
            description="Update task status when work is done",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "failed"],
                    },
                    "result": {"type": "string"},
                    "logs": {"type": "string"},
                },
                "required": ["task_id", "status"],
            },
        ),
        Tool(
            name="add_task_comment",
            description="Add comment to task in PM tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "comment": {"type": "string"},
                },
                "required": ["task_id", "comment"],
            },
        ),
        Tool(
            name="get_server_status",
            description="Get MCP server status",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.ContentBlock]:
    """Handle MCP tool calls"""

    try:
        if name == "get_current_task":
            logger.info("Tool called: get_current_task")
            
            if current_task:
                task_text = f"""
📋 **CURRENT TASK** (Available in VS Code)

**Task ID:** `{current_task.get('id')}`  
**Title:** {current_task.get('title')}  
**Type:** {current_task.get('type', 'TASK')}  
**Status:** `{current_task.get('status')}`  
**Branch:** `{current_task.get('branch', 'N/A')}`  

### 📝 Description
{current_task.get('description', 'No description')}

### ✅ Acceptance Criteria / Requirements
{current_task.get('requirements', 'No requirements')}

---

**You can now:**
1. Work on implementing this task
2. Use `update_task_status` to mark as `in_progress` when you start
3. Use `add_task_comment` to add notes
4. Use `update_task_status` with status `completed` when done
"""
                return [TextContent(type="text", text=task_text)]
            else:
                return [TextContent(
                    type="text",
                    text="📭 **No Pending Tasks**\n\nAll tasks are complete! 🎉"
                )]

        elif name == "get_all_pending_tasks":
            logger.info("Tool called: get_all_pending_tasks")
            limit = arguments.get("limit", 5)
            tasks = all_pending_tasks[:limit]

            if tasks:
                task_list = "\n".join(
                    [
                        f"{i + 1}. **[{t.get('id')}]** {t.get('title')} (`{t.get('status')}`)"
                        for i, t in enumerate(tasks)
                    ]
                )
                return [TextContent(
                    type="text",
                    text=f"📋 **Pending Tasks** ({len(tasks)})\n\n{task_list}"
                )]
            else:
                return [TextContent(type="text", text="✅ No pending tasks!")]

        elif name == "get_task_details":
            logger.info(f"Tool called: get_task_details")
            task_id = arguments["task_id"]
            task = await pm_client.get_task_details(task_id)

            if "error" in task:
                return [TextContent(type="text", text=f"❌ Error: {task['error']}")]

            task_text = f"""
📋 **Task: {task_id}**

**Title:** {task.get('title')}  
**Type:** {task.get('type', 'TASK')}  
**Status:** `{task.get('status')}`  
**Branch:** `{task.get('branch')}`  

### Description
{task.get('description')}

### Requirements
{task.get('requirements')}

### Info
- Created: {task.get('created_at')}
- Updated: {task.get('updated_at')}
"""
            return [TextContent(type="text", text=task_text)]

        elif name == "update_task_status":
            logger.info(f"Tool called: update_task_status")
            task_id = arguments["task_id"]
            status = arguments["status"]
            result = arguments.get("result", "")
            logs = arguments.get("logs", "")

            response = await pm_client.update_task_status(task_id, status, result, logs)

            if "error" in response:
                return [TextContent(type="text", text=f"❌ Error: {response['error']}")]

            return [TextContent(
                type="text",
                text=f"✅ **Task Updated**\n\nTask `{task_id}` is now `{status}`"
            )]

        elif name == "add_task_comment":
            logger.info(f"Tool called: add_task_comment")
            task_id = arguments["task_id"]
            comment = arguments["comment"]

            response = await pm_client.add_task_comment(task_id, comment)

            if "error" in response:
                return [TextContent(type="text", text=f"❌ Error: {response['error']}")]

            return [TextContent(
                type="text",
                text=f"💬 **Comment Added** to task `{task_id}`"
            )]

        elif name == "get_server_status":
            logger.info("Tool called: get_server_status")
            return [TextContent(
                type="text",
                text=f"""
🔌 **MCP Server Status**

✅ **Status:** Running  
**PM Tool API:** `{PM_TOOL_API}`  
**Polling Interval:** {POLLING_INTERVAL}s  
**Pending Tasks:** {len(all_pending_tasks)}  
**Current Task:** {current_task.get('id') if current_task else 'None'}  

Everything is working!
"""
            )]

        else:
            return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Error: {e}")
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


async def main():
    """Start MCP server"""
    from mcp.server.stdio import stdio_server

    # Start polling in background
    asyncio.create_task(poll_for_tasks())

    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream)
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
        await pm_client.close()


if __name__ == "__main__":
    import sys

    if not PM_TOOL_API:
        print("Error: PM_TOOL_API not set", file=sys.stderr)
        sys.exit(1)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✋ Server stopped")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
