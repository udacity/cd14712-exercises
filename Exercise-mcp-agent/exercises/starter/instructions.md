# MCP Autonomous Agent Exercise

## From Chatbot to Agent: Building Autonomous Tool Execution

### Introduction

In the previous lesson, you worked with the simple chatbot from `python-sdk-main/examples/clients/simple-chatbot/`. That chatbot waits for user input, responds to questions, and executes tools when asked. But what if we want something more autonomous?

In this exercise, you'll transform the reactive chatbot into a **proactive agent** that can:
- Analyze complex goals
- Create multi-step execution plans
- Execute tools in the correct sequence
- Learn from results and adapt
- Handle failures gracefully

### The Difference: Chatbot vs Agent

| Chatbot | Agent |
|---------|-------|
| Waits for user input | Takes a goal and runs autonomously |
| Executes one tool per request | Plans and executes multiple tools |
| No memory between requests | Maintains context and learns |
| User drives the conversation | Agent drives the execution |
| Reactive | Proactive |

### Learning Objectives

By completing this exercise, you'll learn:
1. **Planning with LLMs** - How to use Claude to decompose goals into tasks
2. **Task orchestration** - Managing dependencies and execution order
3. **State management** - Maintaining memory and context across operations
4. **Error recovery** - Handling failures without human intervention
5. **Progress tracking** - Providing visibility into autonomous execution

---

## Your Challenge

Transform the provided starter code (`mcp_agent_starter.py`) into a fully functional autonomous agent. The starter code has the structure in place, but key methods are incomplete with `# TODO` markers.

### Part 1: Planning Phase (30 points)

Implement the `create_plan()` method to:
1. Send the goal to Claude with available tools
2. Get back a structured plan (JSON array of tasks)
3. Parse the response into Task objects
4. Handle dependencies between tasks

**Hints:**
- Look at how the simple chatbot formats tools for the LLM
- Claude can return structured JSON if you ask clearly
- Use regex to extract JSON from the response if needed

### Part 2: Execution Phase (30 points)

Implement the `execute_task()` method to:
1. Find the correct server for each tool
2. Execute the tool with proper arguments
3. Store results and update task status
4. Extract "facts" from results for memory

**Hints:**
- Create a mapping of tool names to servers
- Consider what makes a good "fact" to remember
- Handle both successful and failed executions

### Part 3: Main Loop (25 points)

Implement the `run()` method to:
1. Initialize all servers
2. Create an execution plan
3. Execute tasks respecting dependencies
4. Monitor progress and handle failures
5. Generate a final summary

**Hints:**
- Tasks without dependencies can run first
- Use a set to track completed task IDs
- Implement a maximum iteration limit to prevent infinite loops

### Part 4: Memory Management (15 points)

Complete the `AgentMemory` class:
1. Implement `get_relevant_facts()` to retrieve context
2. Store and retrieve task results
3. Provide useful context for future planning

**Hints:**
- Simple keyword matching works for basic relevance
- Recent facts are often most relevant
- Consider task success/failure in memory

---

## Testing Your Agent

### Test Scenario 1: Database Operations
```
Goal: "Create a users table with id, name, and email columns. Add 3 sample users."
```

Expected behavior:
1. Agent plans database operations
2. Creates table first
3. Then inserts records
4. Reports success

### Test Scenario 2: Information Gathering
```
Goal: "List all tables in the database and count the records in each."
```

Expected behavior:
1. Agent discovers available tables
2. Queries each table
3. Aggregates results
4. Provides summary

### Test Scenario 3: Error Recovery
```
Goal: "Query a table that doesn't exist and handle the error gracefully."
```

Expected behavior:
1. Agent attempts query
2. Recognizes failure
3. Adapts plan or reports issue
4. Doesn't crash

---

## Configuration Files

### servers_config.json
Create this file in the same directory as your agent:

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "./test.db"]
    }
  }
}
```

You can add more servers as needed:
- Puppeteer for web automation
- Filesystem for file operations
- Custom servers you've built

---

## Implementation Tips

### 1. Start Simple
- Get basic planning working first
- Test with single-task goals
- Add complexity gradually

### 2. Use Logging
- The starter code includes logging setup
- Add your own log messages for debugging
- Track task execution flow

### 3. Handle Edge Cases
- What if no tools are available?
- What if the LLM returns invalid JSON?
- What if all tasks fail?

### 4. Think About Dependencies
- Some tasks must happen in order (create table → insert data)
- Some tasks can happen in parallel (query different tables)
- The agent should understand both patterns

---

## Grading Rubric

| Component | Points | Criteria |
|-----------|--------|----------|
| Planning | 30 | Creates valid plans from goals, handles JSON parsing, manages dependencies |
| Execution | 30 | Executes tools correctly, handles errors, updates task status |
| Main Loop | 25 | Respects dependencies, monitors progress, generates summaries |
| Memory | 15 | Stores facts, retrieves relevant context, maintains state |
| **Total** | **100** | |

### Bonus Points (+10)
- Implement parallel task execution for independent tasks
- Add retry logic with exponential backoff
- Create a web interface for monitoring agent progress

---

## Submission Requirements

1. **Completed agent code** - Your modified `mcp_agent_starter.py`
2. **Test results** - Output from running the three test scenarios
3. **Reflection** - A brief (200 words) reflection on:
   - What was challenging about autonomous execution?
   - How does this differ from the chatbot approach?
   - What improvements would you make?

---

## Resources

- Review the simple chatbot code for tool execution patterns
- Reference the MCP SDK documentation for server methods
- Use Claude Desktop to understand tool formatting

---

## Getting Started

1. Copy `mcp_agent_starter.py` to your workspace
2. Create `servers_config.json` with at least SQLite server
3. Start with the `create_plan()` method
4. Test frequently with simple goals
5. Build complexity incrementally

Good luck! Remember, the goal is not just to make it work, but to understand how autonomous agents differ from reactive chatbots.