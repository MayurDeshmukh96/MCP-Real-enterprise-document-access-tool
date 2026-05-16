#!/bin/bash
# PM Tool Complete - Terminal Commands Reference
# Copy & paste these commands to get started

# ============================================================================
# SETUP COMMANDS (Run Once)
# ============================================================================

# 1. Extract the ZIP
unzip pm-tool-complete.zip
cd pm-tool-complete

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# On Windows (Command Prompt):
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# Done! You're ready to run


# ============================================================================
# RUNNING COMMANDS (Use Every Time)
# ============================================================================

# ===== TERMINAL 1 =====
# Start the PM Tool Backend API
python src/pm_tool_backend.py

# Expected output:
# ============================================================
#   🚀 PM TOOL BACKEND SERVER
# ============================================================
#   API: http://localhost:3000/api
#   Frontend: http://localhost:3000


# ===== TERMINAL 2 =====
# Start the MCP Server
python src/mcp_task_agent.py

# Expected output:
# ============================================================
#   🚀 PM TASK AGENT MCP SERVER STARTED
#   PM Tool API: http://localhost:3000/api
#   Polling Interval: 5s
# ============================================================


# ===== TERMINAL 3 =====
# Open the PM Tool in browser
open http://localhost:3000  # macOS
xdg-open http://localhost:3000  # Linux
start http://localhost:3000  # Windows


# ============================================================================
# API COMMANDS (For Testing)
# ============================================================================

# Check if server is running
curl http://localhost:3000/health

# Get all tasks
curl http://localhost:3000/api/tasks

# Get statistics
curl http://localhost:3000/stats

# Create a task
curl -X POST http://localhost:3000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Build User Authentication API",
    "description": "Create a REST API for user login",
    "requirements": "FastAPI, JWT, PostgreSQL",
    "type": "BACKEND",
    "branch": "feat/task-1-auth"
  }'

# Get a specific task
curl http://localhost:3000/api/tasks/TASK-1

# Update task status
curl -X PATCH http://localhost:3000/api/tasks/TASK-1 \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'

# Delete a task
curl -X DELETE http://localhost:3000/api/tasks/TASK-1

# Add comment to task
curl -X POST http://localhost:3000/api/tasks/TASK-1/comments \
  -H "Content-Type: application/json" \
  -d '{"comment": "Working on this task"}'

# Seed demo tasks
curl -X POST http://localhost:3000/demo/seed-tasks

# Clear all tasks
curl -X POST http://localhost:3000/demo/clear


# ============================================================================
# VS CODE COMMANDS
# ============================================================================

# Open VS Code in current directory
code .

# Open in VS Code with settings
code . --user-data-dir=.vscode

# VS Code Keyboard Shortcuts
# Ctrl+Shift+I = Open Copilot Chat
# Ctrl+Shift+P = Command Palette
# Ctrl+` = Open Terminal


# ============================================================================
# DEBUGGING COMMANDS
# ============================================================================

# Check Python version
python --version

# Check pip packages
pip list

# Check if mcp is installed
pip show mcp

# View MCP server logs
tail -f mcp_server.log

# Check if port 3000 is in use (macOS/Linux)
lsof -i :3000

# Check if port 3000 is in use (Windows)
netstat -ano | findstr :3000

# Kill process on port 3000 (macOS/Linux)
kill -9 <PID>

# Kill process on port 3000 (Windows)
taskkill /PID <PID> /F

# View all environment variables
env | grep PM_TOOL


# ============================================================================
# COMMON ISSUES & FIXES
# ============================================================================

# Issue: ModuleNotFoundError
# Fix: Reinstall dependencies
pip install --upgrade -r requirements.txt

# Issue: Port 3000 already in use
# Fix: Kill the process using the port (see debugging commands above)

# Issue: MCP server not connecting to VS Code
# Fix: Restart VS Code completely
# Also check: .vscode/settings.json exists and has correct path

# Issue: Virtual environment not activating
# Fix: Make sure you're in the correct directory (pm-tool-complete)

# Issue: Python command not found
# Fix: Make sure Python 3.9+ is installed
# Download from: https://www.python.org/downloads/

# Issue: pip command not found
# Fix: Python installation is broken. Reinstall Python.


# ============================================================================
# USEFUL ALIASES (Optional)
# ============================================================================

# Add to your ~/.bashrc or ~/.zshrc:

# Quick startup alias
alias pm-start='python src/pm_tool_backend.py'

# MCP server alias
alias mcp-start='python src/mcp_task_agent.py'

# Open frontend
alias pm-open='open http://localhost:3000'

# Check all status
alias pm-health='curl http://localhost:3000/health'

# See all tasks
alias pm-tasks='curl http://localhost:3000/api/tasks'


# ============================================================================
# DOCKER COMMANDS (Optional - Advanced)
# ============================================================================

# If you want to run in Docker (create Dockerfile first):

# Build Docker image
docker build -t pm-tool-complete .

# Run PM Tool container
docker run -p 3000:3000 -e PM_TOOL_API=http://localhost:3000/api pm-tool-complete

# Run MCP server container
docker run -p 8000:8000 -e PM_TOOL_API=http://localhost:3000/api pm-tool-complete-mcp


# ============================================================================
# PRODUCTION DEPLOYMENT (Advanced)
# ============================================================================

# Run with production server (gunicorn)
pip install gunicorn
gunicorn src.pm_tool_backend:app --host 0.0.0.0 --port 8000

# Run MCP with systemd service
# Create /etc/systemd/system/pm-mcp.service:
# [Unit]
# Description=PM Tool MCP Server
# After=network.target
#
# [Service]
# Type=simple
# User=pm-user
# WorkingDirectory=/opt/pm-tool-complete
# ExecStart=/opt/pm-tool-complete/venv/bin/python src/mcp_task_agent.py
# Restart=always
#
# [Install]
# WantedBy=multi-user.target

# Then:
sudo systemctl enable pm-mcp
sudo systemctl start pm-mcp


# ============================================================================
# USEFUL TIPS
# ============================================================================

# Tip 1: Keep three terminals open
# Terminal 1: Backend
# Terminal 2: MCP Server
# Terminal 3: Work terminal for other commands

# Tip 2: Use tmux or screen for persistent sessions
tmux new-session -d -s pm-tool
tmux send-keys -t pm-tool 'python src/pm_tool_backend.py' Enter

# Tip 3: Monitor logs in real-time
tail -f mcp_server.log &

# Tip 4: Auto-reload Python on changes (development)
pip install watchfiles
python -m watchfiles "python src/pm_tool_backend.py"

# Tip 5: Pretty print JSON responses
curl http://localhost:3000/api/tasks | python -m json.tool

# Tip 6: Save long responses to file
curl http://localhost:3000/api/tasks > tasks.json

# Tip 7: Test with different task data
for i in {1..5}; do curl -X POST http://localhost:3000/api/tasks \
  -d "{\"title\":\"Task $i\"}" -H "Content-Type: application/json"; done


# ============================================================================
# QUICK REFERENCE CARD
# ============================================================================

cat << 'EOF'

┌─────────────────────────────────────────────────────────┐
│          PM TOOL COMPLETE - QUICK REFERENCE             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  SETUP:                                                 │
│  $ unzip pm-tool-complete.zip                          │
│  $ cd pm-tool-complete                                 │
│  $ python -m venv venv                                 │
│  $ source venv/bin/activate                            │
│  $ pip install -r requirements.txt                     │
│                                                         │
│  RUN (3 Terminals):                                     │
│  Terminal 1: python src/pm_tool_backend.py            │
│  Terminal 2: python src/mcp_task_agent.py             │
│  Browser:   http://localhost:3000                     │
│                                                         │
│  VS CODE:                                               │
│  $ code .                                              │
│  Press: Ctrl+Shift+I (Open Copilot Chat)              │
│  Type: "Get my current task"                           │
│                                                         │
│  TEST:                                                  │
│  $ curl http://localhost:3000/health                  │
│  $ curl http://localhost:3000/api/tasks               │
│                                                         │
│  DEMO TASKS:                                            │
│  $ curl -X POST http://localhost:3000/demo/seed-tasks │
│                                                         │
│  CLEAR ALL:                                             │
│  $ curl -X POST http://localhost:3000/demo/clear      │
│                                                         │
└─────────────────────────────────────────────────────────┘

EOF


# ============================================================================
# END OF COMMANDS
# ============================================================================

# For more help, check:
# - README.md (detailed documentation)
# - QUICKSTART.md (5-minute guide)
# - PACKAGE_SUMMARY.txt (overview)
# - VISUAL_GUIDE.txt (diagrams)
