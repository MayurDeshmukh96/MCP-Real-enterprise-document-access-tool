# Quick Start Guide ⚡

Get everything running in **5 minutes**!

---

## 📋 Prerequisites

- Python 3.9+
- VS Code (optional, for MCP integration)
- A terminal

---

## 🚀 Step 1: Setup (2 minutes)

```bash
# Navigate to project
cd pm-tool-complete

# Create virtual environment
python -m venv venv

# Activate it
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🔧 Step 2: Start Services (3 minutes)

### Terminal 1: Start PM Tool Backend

```bash
python src/pm_tool_backend.py
```

**Expected output:**
```
============================================================
  🚀 PM TOOL BACKEND SERVER
============================================================
  API: http://localhost:3000/api
  Frontend: http://localhost:3000
  Health: http://localhost:3000/health

  Demo endpoints:
  POST http://localhost:3000/demo/seed-tasks
  POST http://localhost:3000/demo/clear
============================================================
```

### Terminal 2: Start MCP Server

```bash
python src/mcp_task_agent.py
```

**Expected output:**
```
============================================================
  🚀 PM TASK AGENT MCP SERVER STARTED
  PM Tool API: http://localhost:3000/api
  Polling Interval: 5s
============================================================
```

### Terminal 3: Open PM Tool

```bash
# Open in browser
http://localhost:3000
```

---

## ✅ Step 3: Create Your First Task

1. **In the browser**, fill the form:
   - Title: "Build Login Page"
   - Description: "Create a login form UI"
   - Requirements: "React, form validation, error handling"
   - Type: "FRONTEND"
   - Branch: "feat/login-page"

2. **Click**: "➕ Add Task"

3. **See it appear** in the Tasks list!

---

## 🎯 Step 4: Use in VS Code

1. **Open VS Code**:
   ```bash
   code .
   ```

2. **Open Copilot Chat** (Ctrl+Shift+I)

3. **Type**:
   ```
   Get my current task from PM tool
   ```

4. **See the task appear** with all details!

5. **Ask Copilot**:
   ```
   Generate the React code for this login page
   ```

6. **Ask to complete**:
   ```
   Mark this task as completed with the code
   ```

7. **Check the browser** - Task is now marked ✅!

---

## 📊 What You Should See

### Browser at http://localhost:3000

```
┌────────────────────────────────────┐
│  PM Tool - Task Management         │
├────────────────────────────────────┤
│                                    │
│  [Form to add new task]            │
│                                    │
│  Stats: Total: 1, Pending: 1      │
│                                    │
│  ┌──────────────────────────────┐ │
│  │ TASK-1: Build Login Page     │ │
│  │ FRONTEND | pending           │ │
│  │ [Description...]             │ │
│  │ [▶️ Start] [🗑️ Delete]       │ │
│  └──────────────────────────────┘ │
│                                    │
└────────────────────────────────────┘
```

### MCP Server Logs

```
📡 Polling PM tool for pending tasks...
✅ Found 1 pending task(s)
   Current: TASK-1 - Build Login Page
   Total Pending: 1
```

### VS Code Copilot Chat

```
You: Get my current task from PM tool

Copilot: Let me fetch your current task...

📋 **CURRENT TASK**

**Task ID:** TASK-1
**Title:** Build Login Page
**Type:** FRONTEND
...
```

---

## 🔄 The Full Workflow

```
Browser (Step 3)
    ↓
Create task "Build Login Page"
    ↓
MCP Server polls (automatically)
    ↓
VS Code Copilot Chat (Step 4)
    ↓
Ask: "Get my current task"
    ↓
Copilot calls MCP tool: get_current_task
    ↓
Task details appear in chat
    ↓
Ask: "Generate code"
    ↓
Copilot generates React code
    ↓
Ask: "Mark complete"
    ↓
Copilot calls MCP tool: update_task_status
    ↓
Browser shows task as ✅ COMPLETED
    ↓
Next pending task loads automatically
```

---

## ✨ Key Commands

### Add Demo Tasks (Quick Testing)

```bash
curl -X POST http://localhost:3000/demo/seed-tasks
```

Creates 3 sample tasks instantly!

### Clear All Tasks

```bash
curl -X POST http://localhost:3000/demo/clear
```

### Check Server Status

```bash
curl http://localhost:3000/health
```

### View All Tasks via API

```bash
curl http://localhost:3000/api/tasks
```

---

## 🎯 Common Prompts for Copilot

```
"Get my current task"
"Show all pending tasks"
"Generate code for TASK-1"
"Mark the task as completed"
"Add a comment: Work in progress"
"Check the server status"
```

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 3000 already in use | `lsof -i :3000` then kill the process |
| ModuleNotFoundError | Run `pip install -r requirements.txt` |
| MCP not showing in VS Code | Restart VS Code completely |
| No tasks showing | Create one, wait 5s, the MCP polls |
| Backend won't start | Check `python --version` is 3.9+ |

---

## 🎉 You're Done!

You now have:

✅ **PM Tool** running at http://localhost:3000  
✅ **MCP Server** listening for tasks  
✅ **VS Code** integrated with Copilot  
✅ **Full automation** between PM tool and editor  

**Start creating tasks and let Copilot generate code!** 🚀

---

## 📚 Next Steps

1. Read `README.md` for detailed documentation
2. Explore the API endpoints
3. Customize task types and fields
4. Integrate with your own PM tool (change `PM_TOOL_API`)
5. Deploy to production

---

**Questions?** Check the full `README.md` file!
