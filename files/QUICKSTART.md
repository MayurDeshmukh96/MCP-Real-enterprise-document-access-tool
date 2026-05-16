# Quick Start Guide - 5 Minutes to Automation

## What You'll Have After This

A fully functional system where:
1. You create a task in PM tool
2. Task automatically appears in Claude/Agent
3. Code is generated automatically
4. Results updated back to PM tool

---

## Step 1: Setup (2 minutes)

```bash
# Clone files into a directory
cd ~/pm-agent-automation

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

---

## Step 2: Configure (1 minute)

Edit `.env`:

```bash
nano .env
```

**Minimal configuration:**
```env
PM_TOOL_API=http://localhost:3000/api
ANTHROPIC_API_KEY=sk-ant-your_key_here
```

Get your Anthropic key from: https://console.anthropic.com

---

## Step 3: Start Everything (2 minutes)

**Terminal 1: Mock PM Tool (simulates your project management tool)**
```bash
python mock_pm_tool.py
# Output: Running on http://localhost:3000
```

**Terminal 2: Code Generation Agent**
```bash
python agent.py
# Output: Agent started - checking for tasks every 60s
```

**Terminal 3: (Optional) Webhook Handler**
```bash
python webhook_handler.py
# Output: Running on http://localhost:8000
```

---

## Step 4: Test It!

### Create a Task

**Option A: Via API**
```bash
curl -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Build a REST API",
    "description": "Create a simple REST API",
    "requirements": "Use Python FastAPI, PostgreSQL, JWT authentication"
  }'
```

**Option B: Use Demo Data**
```bash
curl -X POST http://localhost:3000/demo/seed-tasks
```

### Watch Agent Process It

Check Terminal 2 output:
```
2024-01-15 10:30:01 - agent - INFO - Fetching pending tasks...
2024-01-15 10:30:02 - agent - INFO - Found 1 pending task(s)
2024-01-15 10:30:02 - agent - INFO - Processing task TASK-1: Build a REST API
2024-01-15 10:30:02 - agent - INFO - Task TASK-1 updated to in_progress
2024-01-15 10:30:25 - agent - INFO - Task TASK-1 completed successfully
```

### Check Results

```bash
# View the completed task
curl http://localhost:3000/tasks/TASK-1

# Response includes:
{
  "id": "TASK-1",
  "status": "completed",
  "result": "[Generated Python code...]",
  "comments": ["✅ Task completed at...", "🚀 Agent started..."]
}
```

---

## Common Scenarios

### Scenario 1: Single Task Processing (Testing)

```bash
python agent.py --task TASK-1
```

Processes just one task and exits. Great for debugging.

### Scenario 2: Continuous Processing

```bash
python agent.py
```

Checks for tasks every 60 seconds and processes them.

### Scenario 3: Real-time with Webhooks

```bash
# Terminal 1
python mock_pm_tool.py

# Terminal 2
python webhook_handler.py

# Terminal 3
python agent.py
```

When webhook gets task, agent processes immediately.

---

## Folder Structure

```
pm-agent-automation/
├── agent.py                    # Main code generation agent
├── mcp_pm_server.py           # MCP server (advanced)
├── webhook_handler.py          # Webhook receiver (optional)
├── mock_pm_tool.py            # Test PM tool
├── requirements.txt           # Python dependencies
├── .env                       # Your configuration
├── .env.example               # Configuration template
└── SETUP_GUIDE.md             # Detailed setup guide
```

---

## API Reference

### Create Task
```bash
POST /tasks
{
  "title": "Task name",
  "description": "What needs to be done",
  "requirements": "Technical requirements"
}
```

### Get Task
```bash
GET /tasks/TASK-123
```

### List Pending Tasks
```bash
GET /tasks?status=pending
```

### Update Task (Agent does this automatically)
```bash
PATCH /tasks/TASK-123
{
  "status": "completed",
  "result": "Generated code here",
  "logs": "Execution logs"
}
```

### Add Comment (Agent does this too)
```bash
POST /tasks/TASK-123/comments
{
  "comment": "Status update message"
}
```

---

## Troubleshooting

### "Connection refused" error?
Make sure all terminals are running:
- Terminal 1: `python mock_pm_tool.py`
- Terminal 2: `python agent.py`

### "ANTHROPIC_API_KEY not set" error?
```bash
# Check .env file
cat .env

# Should show: ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### "No tasks being processed"?

1. Check tasks exist:
   ```bash
   curl http://localhost:3000/stats
   ```
   Look for `"pending"` count > 0

2. Check agent logs (Terminal 2):
   ```
   Fetching pending tasks...
   Found X pending task(s)
   ```

3. If logs show "Found 0", create a task first

### "Code generation failed"?

1. Check API key is valid
2. Try specific task: `python agent.py --task TASK-1`
3. Look at error message in logs

---

## Customization Quick Tips

### Change Check Interval

Edit `.env`:
```env
AGENT_RUN_INTERVAL=30  # Check every 30 seconds instead of 60
```

### Modify Code Generation

Edit `agent.py`, find `generate_code_for_task()` function:
```python
prompt = f"""
You are a code generation assistant...
[Customize this prompt]
"""
```

### Add Custom Task Fields

Edit task creation in `mock_pm_tool.py` or your real PM tool to add fields like:
- `priority`
- `assignee`
- `due_date`
- `tags`

Then use these in the agent prompt.

---

## Next Steps

1. ✅ **Get it running** - Follow steps 1-4 above
2. ✅ **Test with demo tasks** - Use `/demo/seed-tasks`
3. ✅ **Try single task** - Use `--task` argument
4. ✅ **Integrate with your PM tool** - Update PM_TOOL_API in .env
5. ✅ **Deploy to production** - See SETUP_GUIDE.md

---

## Getting Help

Check `SETUP_GUIDE.md` for:
- Detailed architecture explanation
- Integration with real PM tools (Jira, Asana, Linear)
- Production deployment
- Monitoring and logging
- Email notifications
- Docker setup

---

## Key Files Explained

| File | Purpose |
|------|---------|
| `agent.py` | Main automation engine - polls tasks and generates code |
| `mcp_pm_server.py` | Exposes PM tool as MCP server (for advanced usage) |
| `webhook_handler.py` | Receives webhooks from PM tool (optional) |
| `mock_pm_tool.py` | Test server simulating your PM tool |

---

## Architecture Overview

```
Your PM Tool          Mock PM Tool (for testing)
    │                       │
    │                       │
    └─────► Agent ◄─────────┘
            │
            ├─► Claude API (generates code)
            │
            └─► Updates task status & comments
```

---

## Quick Wins 🚀

1. **Right now**: You have a working prototype
2. **Next**: Swap mock_pm_tool.py for your real PM tool API URL
3. **Then**: Add webhooks for real-time processing
4. **Finally**: Deploy to production with Docker/Systemd

---

Good luck! 🎉
