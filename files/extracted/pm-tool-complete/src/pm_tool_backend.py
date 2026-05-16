#!/usr/bin/env python3
"""
PM Tool Backend Server
Serves the PM tool API and frontend
"""

import json
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import uvicorn

app = FastAPI(title="PM Tool API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory database
tasks_db = {}
comments_db = {}


# ============================================================================
# Data Models
# ============================================================================

class TaskCreate(BaseModel):
    title: str
    description: str = ""
    requirements: str = ""
    type: str = "TASK"
    branch: str = "main"


class TaskUpdate(BaseModel):
    title: str = None
    description: str = None
    requirements: str = None
    status: str = None
    result: str = None
    logs: str = None
    updated_at: str = None


class CommentCreate(BaseModel):
    comment: str


# ============================================================================
# Helper Functions
# ============================================================================

def generate_task_id():
    """Generate task ID like TASK-1, TASK-2, etc."""
    if not tasks_db:
        return "TASK-1"
    max_num = max([int(task_id.split('-')[1]) for task_id in tasks_db.keys()])
    return f"TASK-{max_num + 1}"


def get_task_response(task_id: str, task: dict) -> dict:
    """Format task response with comments"""
    return {
        "id": task_id,
        "title": task["title"],
        "description": task["description"],
        "requirements": task["requirements"],
        "type": task["type"],
        "branch": task["branch"],
        "status": task["status"],
        "result": task.get("result"),
        "logs": task.get("logs"),
        "created_at": task["created_at"],
        "updated_at": task["updated_at"],
        "comments": comments_db.get(task_id, [])
    }


# ============================================================================
# Routes - Frontend
# ============================================================================

@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML"""
    frontend_path = Path(__file__).parent.parent / "pm-tool-frontend" / "index.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)
    return {"message": "Frontend not found"}


# ============================================================================
# Routes - API
# ============================================================================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "pm-tool"}


@app.get("/stats")
async def get_stats():
    """Get task statistics"""
    tasks = list(tasks_db.values())

    stats = {
        "total_tasks": len(tasks),
        "pending": len([t for t in tasks if t["status"] == "pending"]),
        "in_progress": len([t for t in tasks if t["status"] == "in_progress"]),
        "completed": len([t for t in tasks if t["status"] == "completed"]),
        "failed": len([t for t in tasks if t["status"] == "failed"]),
    }

    return stats


@app.get("/api/tasks")
async def list_tasks(status: str = None, limit: int = 10):
    """List tasks, optionally filtered by status"""
    tasks = list(tasks_db.items())

    if status:
        tasks = [(id, task) for id, task in tasks if task["status"] == status]

    # Sort by creation time (newest first)
    tasks.sort(key=lambda x: x[1]["created_at"], reverse=True)

    result = [
        get_task_response(task_id, task)
        for task_id, task in tasks[:limit]
    ]

    return result


@app.post("/api/tasks")
async def create_task(task: TaskCreate):
    """Create a new task"""
    task_id = generate_task_id()
    now = datetime.now().isoformat()

    new_task = {
        "title": task.title,
        "description": task.description,
        "requirements": task.requirements,
        "type": task.type,
        "branch": task.branch,
        "status": "pending",
        "result": None,
        "logs": None,
        "created_at": now,
        "updated_at": now,
    }

    tasks_db[task_id] = new_task
    comments_db[task_id] = []

    print(f"✨ Created task: {task_id} - {task.title}")

    # ===== AUTOMATION CODE =====
    # Trigger Antigravity Agent in a background thread to avoid blocking the API response
    import threading
    import subprocess
    import os

    def trigger_agent():
        print(f"🤖 Automatically launching Antigravity agent for task: {task_id}...")

        # Build prompt — strip newlines so it's a clean single-line string
        prompt = (
            f"Please work on the following task:\n"
            f"Task ID: {task_id}\n"
            f"Title: {task.title}\n"
            f"Description: {task.description}\n"
            f"Requirements: {task.requirements}\n"
            f"When done, update the task status to completed via PATCH /api/tasks/{task_id}."
        ).strip()

        # Workspace root: d:\Mayur\Learning\MCP (4 levels up from src/)
        workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        print(f"📁 Workspace dir: {workspace_dir}")
        print(f"📝 Prompt:\n{prompt}\n")

        try:
            import tempfile

            # Write the prompt to a temp file to completely avoid Windows shell quoting issues.
            # Then pipe it via: type "file.txt" | antigravity.cmd chat -m agent -r -
            # This is the documented stdin usage from `antigravity.cmd chat --help`
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.txt', delete=False, encoding='utf-8'
            ) as f:
                f.write(prompt)
                temp_path = f.name

            print(f"📄 Prompt written to temp file: {temp_path}")

            # Feed the prompt file directly to Antigravity stdin. The trailing
            # "-" tells `antigravity chat` to use stdin as the prompt.
            cmd = "antigravity.cmd chat -m agent -r -"
            print(f"🔧 CMD: {cmd}")

            prompt_file = open(temp_path, "r", encoding="utf-8")
            subprocess.Popen(
                cmd,
                cwd=workspace_dir,
                shell=True,
                stdin=prompt_file,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print("✅ Agent launched successfully!")
        except Exception as e:
            print(f"❌ Failed to launch agent: {e}")

    # Start the thread
    threading.Thread(target=trigger_agent, daemon=True).start()
    # ===========================

    return get_task_response(task_id, new_task)


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """Get a specific task"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return get_task_response(task_id, tasks_db[task_id])


@app.patch("/api/tasks/{task_id}")
async def update_task(task_id: str, task_update: TaskUpdate):
    """Update a task"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    task = tasks_db[task_id]

    # Update fields
    if task_update.title is not None:
        task["title"] = task_update.title
    if task_update.description is not None:
        task["description"] = task_update.description
    if task_update.requirements is not None:
        task["requirements"] = task_update.requirements
    if task_update.status is not None:
        task["status"] = task_update.status
    if task_update.result is not None:
        task["result"] = task_update.result
    if task_update.logs is not None:
        task["logs"] = task_update.logs

    task["updated_at"] = datetime.now().isoformat()

    print(f"📝 Updated task: {task_id} -> {task['status']}")

    return get_task_response(task_id, task)


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    deleted = tasks_db.pop(task_id)
    if task_id in comments_db:
        comments_db.pop(task_id)

    print(f"🗑️  Deleted task: {task_id}")

    return {"success": True, "deleted_id": task_id}


@app.post("/api/tasks/{task_id}/comments")
async def add_comment(task_id: str, comment_data: CommentCreate):
    """Add a comment to a task"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    comment_id = str(uuid.uuid4())[:8]
    comment = {
        "id": comment_id,
        "text": comment_data.comment,
        "created_at": datetime.now().isoformat(),
    }

    if task_id not in comments_db:
        comments_db[task_id] = []

    comments_db[task_id].append(comment)

    print(f"💬 Added comment to {task_id}: {comment_data.comment[:50]}...")

    return comment


@app.get("/api/tasks/{task_id}/comments")
async def get_comments(task_id: str):
    """Get comments for a task"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return comments_db.get(task_id, [])


# ============================================================================
# Demo Endpoints
# ============================================================================

@app.post("/demo/seed-tasks")
async def seed_demo_tasks():
    """Create demo tasks for testing"""
    demo_tasks = [
        {
            "title": "Build User Authentication API",
            "description": "Create a REST API for user login and registration",
            "requirements": "Use Python FastAPI, implement JWT token authentication, PostgreSQL database for user storage, password hashing with bcrypt",
            "type": "BACKEND",
            "branch": "feat/task-1-auth-api",
        },
        {
            "title": "Create Database Schema",
            "description": "Design and implement database schema for e-commerce platform",
            "requirements": "PostgreSQL, support for users, products, orders, inventory management, proper indexing",
            "type": "BACKEND",
            "branch": "feat/task-2-database",
        },
        {
            "title": "Build Frontend Login Form",
            "description": "Create a beautiful login form UI component",
            "requirements": "React, form validation, error handling, loading states",
            "type": "FRONTEND",
            "branch": "feat/task-3-login-ui",
        },
    ]

    created = []
    for task_data in demo_tasks:
        task_create = TaskCreate(**task_data)
        task_id = generate_task_id()
        now = datetime.now().isoformat()

        new_task = {
            "title": task_create.title,
            "description": task_create.description,
            "requirements": task_create.requirements,
            "type": task_create.type,
            "branch": task_create.branch,
            "status": "pending",
            "result": None,
            "logs": None,
            "created_at": now,
            "updated_at": now,
        }

        tasks_db[task_id] = new_task
        comments_db[task_id] = []
        created.append(get_task_response(task_id, new_task))

    return {
        "success": True,
        "created": len(created),
        "tasks": created,
    }


@app.post("/demo/clear")
async def clear_demo_data():
    """Clear all demo data"""
    count = len(tasks_db)
    tasks_db.clear()
    comments_db.clear()

    return {
        "success": True,
        "cleared": count,
    }


# ============================================================================
# Startup
# ============================================================================

def kill_port_3000():
    """Kill any process running on port 3000 (Windows)"""
    import subprocess
    try:
        # Find PID on port 3000
        output = subprocess.check_output('netstat -ano | findstr :3000', shell=True).decode()
        for line in output.splitlines():
            if 'LISTENING' in line:
                pid = line.strip().split()[-1]
                print(f"🛑 Killing existing process on port 3000 (PID: {pid})...")
                subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
    except Exception:
        pass

if __name__ == "__main__":
    kill_port_3000()
    print("\n" + "="*60)
    print("  🚀 PM TOOL BACKEND SERVER")
    print("="*60)
    print("  API: http://localhost:3000/api")
    print("  Frontend: http://localhost:3000")
    print("  Health: http://localhost:3000/health")
    print("\n  Demo endpoints:")
    print("  POST http://localhost:3000/demo/seed-tasks")
    print("  POST http://localhost:3000/demo/clear")
    print("="*60 + "\n")

    uvicorn.run(
        "pm_tool_backend:app",
        host="0.0.0.0",
        port=3000,
        reload=False,
        log_level="info",
    )
