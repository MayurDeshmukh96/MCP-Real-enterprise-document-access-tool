# PM Tool + MCP Integration - Complete Guide 🎯

## 📁 Project Structure

```
pm-tool-complete/
├── .vscode/
│   └── settings.json                 ← VS Code MCP Configuration
├── pm-tool-frontend/
│   └── index.html                    ← Frontend (One Page App)
├── src/
│   ├── pm_tool_backend.py           ← PM Tool API Server
│   └── mcp_task_agent.py            ← MCP Server
├── .env                              ← Environment Variables
├── requirements.txt                  ← Python Dependencies
├── README.md                         ← This file
└── QUICKSTART.md                     ← Quick Start Guide
```

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Python Dependencies

```bash
# Navigate to project
cd pm-tool-complete

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start PM Tool Backend

```bash
# In Terminal 1
python src/pm_tool_backend.py

# You should see:
# ============================================================
#   🚀 PM TOOL BACKEND SERVER
# ============================================================
#   API: http://localhost:3000/api
#   Frontend: http://localhost:3000
```

### Step 3: Open PM Tool in Browser

Visit: http://localhost:3000

You'll see the PM Tool frontend where you can:
- ➕ Add new tasks
- 📋 View all tasks
- ✅ Mark tasks as complete
- 🗑️ Delete tasks

### Step 4: Add Demo Tasks (Optional)

Run in a new terminal:
```bash
curl -X POST http://localhost:3000/demo/seed-tasks
```

This creates 3 sample tasks automatically.

### Step 5: Start MCP Server

```bash
# In Terminal 2
python src/mcp_task_agent.py

# You should see:
# ============================================================
#   🚀 PM TASK AGENT MCP SERVER STARTED
#   PM Tool API: http://localhost:3000/api
#   Polling Interval: 5s
# ============================================================
```

### Step 6: Open in VS Code

```bash
# In Terminal 3
code .
```

---

## 💻 How to Use

### Create a Task

1. **Open** http://localhost:3000 in your browser
2. **Fill in** the form:
   - Title: "Build User Authentication API"
   - Description: "Create a REST API for user login"
   - Requirements: "FastAPI, JWT, PostgreSQL"
   - Type: "BACKEND"
   - Branch: "feat/task-1-auth"
3. **Click** "➕ Add Task"

### Use Task in VS Code

1. **Open VS Code** with the project
2. **Open Copilot Chat** (Ctrl+Shift+I)
3. **Type** in the chat:
   ```
   Get my current task from PM tool
   ```

4. **Copilot shows:**
   ```
   📋 **CURRENT TASK**
   
   **Task ID:** TASK-1
   **Title:** Build User Authentication API
   **Type:** BACKEND
   ...
   ```

5. **Ask Copilot to generate code:**
   ```
   Generate code for this task
   ```

6. **Copilot generates the code**

7. **Mark task complete:**
   ```
   Mark this task as completed with the generated code
   ```

8. **Task is updated** in PM Tool automatically!

---

## 🎯 Complete Workflow

### What Happens Step-by-Step

```
1. You create task in PM Tool UI
   ↓
2. PM Tool saves task (pending status)
   ↓
3. MCP Server polls every 5 seconds
   ↓
4. MCP Server finds the task
   ↓
5. Task appears in VS Code via MCP tools
   ↓
6. You ask Copilot: "Get my current task"
   ↓
7. Copilot calls MCP tool: get_current_task
   ↓
8. Task details appear in chat
   ↓
9. You ask: "Generate code for this"
   ↓
10. Copilot generates code
    ↓
11. You ask: "Mark it complete"
    ↓
12. Copilot calls MCP tool: update_task_status
    ↓
13. Task status changes to "completed" in PM Tool
    ↓
14. Next pending task loads automatically
```

---

## 🔧 Available APIs

### Frontend (Browser)

Visit: http://localhost:3000

- Add tasks
- View tasks
- Update task status
- Delete tasks
- See statistics

### Backend API

```
GET    http://localhost:3000/api/tasks                 - List tasks
POST   http://localhost:3000/api/tasks                 - Create task
GET    http://localhost:3000/api/tasks/{id}            - Get task details
PATCH  http://localhost:3000/api/tasks/{id}            - Update task
DELETE http://localhost:3000/api/tasks/{id}            - Delete task
POST   http://localhost:3000/api/tasks/{id}/comments   - Add comment
GET    http://localhost:3000/stats                     - Get statistics
```

### MCP Tools (In VS Code)

Available tools via MCP:
- `get_current_task` - Get the current task
- `get_all_pending_tasks` - List all pending tasks
- `get_task_details` - Get full task info
- `update_task_status` - Mark task complete
- `add_task_comment` - Add notes to task
- `get_server_status` - Check server status

---

## 📋 Example Task Data

When you create a task, it includes:

```json
{
  "id": "TASK-1",
  "title": "Build User Authentication API",
  "description": "Create a REST API for user login and registration",
  "requirements": "FastAPI, JWT authentication, PostgreSQL database",
  "type": "BACKEND",
  "branch": "feat/task-1-auth-api",
  "status": "pending",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "comments": []
}
```

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to localhost:3000"

**Solution:**
```bash
# Check if backend is running
curl http://localhost:3000/health

# Should return:
# {"status": "healthy", "service": "pm-tool"}
```

### Issue: "MCP server not found in VS Code"

**Solution:**
1. Check `.vscode/settings.json` exists
2. Verify `mcp_task_agent.py` path is correct
3. Restart VS Code completely
4. Check MCP server is running in terminal

### Issue: "No pending tasks showing"

**Solution:**
1. Create a task in the browser UI
2. Check MCP server logs for "Found X pending task(s)"
3. Wait a few seconds (polling is every 5s)
4. Refresh VS Code

### Issue: Python module not found

**Solution:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify MCP installation
python -c "import mcp; print(mcp.__version__)"
```

---

## 📝 Example Prompts for Copilot

You can use these prompts in VS Code Copilot Chat:

```
"Get my current task from PM tool"
"Show me all pending tasks"
"Get details for task TASK-1"
"Generate code for this task"
"Mark this task as in progress"
"Complete the task with the generated code"
"Add a comment: Implementation complete"
"Check server status"
```

---

## 🎓 Key Features

✅ **One-Page PM Tool** - Simple, intuitive task management  
✅ **Add Tasks** - Create tasks with title, description, requirements  
✅ **View Tasks** - See all tasks with filtering and statistics  
✅ **Update Status** - Mark tasks as pending, in_progress, or completed  
✅ **MCP Integration** - Direct VS Code integration  
✅ **Auto Polling** - MCP server polls PM tool every 5 seconds  
✅ **Task Display** - Tasks appear in Copilot chat  
✅ **Full Automation** - No manual copying needed  

---

## 🚀 Next Steps

1. ✅ Install dependencies
2. ✅ Start PM tool backend
3. ✅ Open http://localhost:3000
4. ✅ Create a task
5. ✅ Start MCP server
6. ✅ Open VS Code
7. ✅ Use Copilot Chat to get task
8. ✅ Let Copilot generate code
9. ✅ Mark task complete
10. ✅ Watch PM Tool update

---

## 📞 Support

### Check Server Status

```bash
# Backend
curl http://localhost:3000/health

# Statistics
curl http://localhost:3000/stats

# List tasks
curl http://localhost:3000/api/tasks
```

### View Logs

```bash
# MCP Server logs
tail -f mcp_server.log

# Check for errors
grep -i error mcp_server.log
```

### Reset Everything

```bash
# Clear all demo data
curl -X POST http://localhost:3000/demo/clear

# Or delete individual tasks
curl -X DELETE http://localhost:3000/api/tasks/TASK-1
```

---

## 🎉 You're All Set!

Everything is configured and ready to use. Start by:

1. Running the PM tool backend
2. Creating a task in the browser
3. Opening VS Code
4. Using Copilot Chat to work with the task

Enjoy! 🚀
