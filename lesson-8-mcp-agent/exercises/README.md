# Lesson 8: MCP Autonomous Agent Exercise

## Overview

This exercise extends the simple chatbot example from Module 10 to create an **autonomous agent** that can plan and execute complex multi-step tasks without human intervention.

## Learning Path

### Prerequisites
- Completed Module 8 (Building MCP Clients)
- Worked with `python-sdk-main/examples/clients/simple-chatbot/`
- Understanding of MCP tool execution
- Familiarity with async Python

### What You'll Build
Transform a reactive chatbot into a proactive agent that:
- 🎯 Analyzes goals and creates execution plans
- 🔄 Executes tools in proper sequence
- 🧠 Maintains memory and context
- ⚡ Handles errors autonomously
- 📊 Provides progress tracking

## Directory Structure

```
lesson-8-mcp-agent/exercises/
├── README.md                    # This file
├── servers_config.json          # MCP server configuration
├── starter/
│   ├── instructions.md          # Detailed exercise instructions
│   └── mcp_agent_starter.py     # Starter code with TODOs
└── solution/
    └── mcp_agent_solution.py    # Complete solution
```

## Quick Start

### 1. Setup Environment

```bash
# Navigate to exercise directory
cd lesson-8-mcp-agent/exercises

# Install dependencies
pip install anthropic mcp

# Copy starter code to your workspace
cp starter/mcp_agent_starter.py my_agent.py
```

### 2. Configure Vocareum API

The code is pre-configured with a Vocareum API key. If you need to use your own:

```python
# Line 19 in the starter code
VOCAREUM_API_KEY = "voc-your-key-here"
```

### 3. Start MCP Servers

The exercise uses SQLite server by default:

```bash
# The agent will start this automatically, or run manually:
uvx mcp-server-sqlite --db-path ./test.db
```

### 4. Run Your Agent

```bash
python my_agent.py
```

## Exercise Components

### Part 1: Planning (30 points)
Implement goal analysis and task planning using Claude.

**Key Method:** `create_plan(goal: str) -> List[Task]`

### Part 2: Execution (30 points)
Execute tools and manage task lifecycle.

**Key Method:** `execute_task(task: Task) -> None`

### Part 3: Orchestration (25 points)
Coordinate task execution with dependency management.

**Key Method:** `run(goal: str) -> str`

### Part 4: Memory (15 points)
Implement context retention between operations.

**Key Class:** `AgentMemory`

## Example Goals to Test

### Simple Goals
```
"List all tables in the database"
"Create a table called products with id and name columns"
```

### Complex Goals
```
"Create a complete user management system with tables for users, roles, and permissions, then populate with sample data"
"Analyze the database schema and generate a report of all tables, their columns, and record counts"
```

### Error Testing
```
"Query a non-existent table and handle the error"
"Execute an invalid SQL command and recover"
```

## Key Concepts

### Chatbot vs Agent

| Aspect | Chatbot | Agent |
|--------|---------|--------|
| **Control** | User-driven | Goal-driven |
| **Execution** | Single tool/response | Multi-step plan |
| **Memory** | Conversation history | Task context & facts |
| **Error Handling** | Reports to user | Autonomous recovery |
| **Planning** | None | Creates execution strategy |

### Task Dependencies

Tasks can have dependencies that must be respected:

```python
Task(id=1, description="Create users table", dependencies=[])
Task(id=2, description="Add admin user", dependencies=[1])  # Depends on table creation
Task(id=3, description="Add regular user", dependencies=[1]) # Also depends on table
```

### Memory Management

The agent maintains memory to:
- Store facts learned from operations
- Track completed tasks
- Provide context for future planning

## Common Pitfalls & Solutions

### Issue: LLM Returns Invalid JSON
**Solution:** Use regex to extract JSON, provide clearer prompts

### Issue: Circular Dependencies
**Solution:** Implement cycle detection in planning

### Issue: Tool Not Found
**Solution:** Map tools to servers during initialization

### Issue: Infinite Loop
**Solution:** Use max_iterations limit

## Testing Your Solution

### Basic Test
```python
goal = "Create a table and add one record"
# Should create plan, execute both steps, report success
```

### Dependency Test
```python
goal = "Create related tables with foreign keys"
# Should respect creation order
```

### Error Recovery Test
```python
goal = "Perform invalid operation then continue"
# Should handle error and complete other tasks
```

## Evaluation Criteria

Your solution will be evaluated on:

1. **Correctness** - Does it create valid plans and execute them?
2. **Error Handling** - Does it handle failures gracefully?
3. **Dependency Management** - Are tasks executed in correct order?
4. **Memory Usage** - Does it learn from operations?
5. **Code Quality** - Is the code clean and well-documented?

## Advanced Challenges (Optional)

### 1. Parallel Execution
Modify the agent to execute independent tasks in parallel:
```python
async def execute_parallel_tasks(self, tasks: List[Task]) -> None:
    """Execute tasks without dependencies in parallel."""
    # Your implementation
```

### 2. Plan Adaptation
If a task fails, re-plan the remaining tasks:
```python
async def adapt_plan(self, failed_task: Task, remaining: List[Task]) -> List[Task]:
    """Create new plan when a task fails."""
    # Your implementation
```

### 3. Web Interface
Create a simple web interface to monitor agent progress:
- Display current plan
- Show task status in real-time
- Visualize dependencies

## Resources

### Documentation
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Asyncio Documentation](https://docs.python.org/3/library/asyncio.html)

### Related Examples
- `python-sdk-main/examples/clients/simple-chatbot/` - Base chatbot implementation
- `MCP-model-context-protocol-course-cd14712-main/mcp-project/client.py` - Advanced client patterns

## Solution Notes

The complete solution demonstrates:
- Structured planning with JSON responses
- Tool-to-server mapping for execution
- Dependency resolution algorithm
- Comprehensive error handling
- Rich progress reporting

Review the solution only after attempting the exercise yourself!

## Support

If you encounter issues:
1. Check the logs - extensive logging is built in
2. Verify server configuration in `servers_config.json`
3. Test with simple goals first
4. Review the instruction comments in starter code
5. Consult the solution for specific patterns

## Next Steps

After completing this exercise, you'll be ready to:
- Build production agent systems
- Implement complex orchestration patterns
- Create domain-specific agents
- Integrate agents into larger applications

---

**Good luck!** Remember, the journey from chatbot to agent is about adding autonomy, intelligence, and resilience to your MCP applications.