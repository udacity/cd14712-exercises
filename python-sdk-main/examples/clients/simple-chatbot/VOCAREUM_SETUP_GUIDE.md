# Vocareum Setup Guide for MCP Simple Chatbot

This guide will help you set up and run the MCP Simple Chatbot example using your Vocareum API key.

## What Changed?

This example has been **refactored for educational use** with the following modifications:

### Before (Original)
- ❌ Required `.env` file with API keys
- ❌ Used Groq API (different LLM provider)
- ❌ Required `python-dotenv` package
- ❌ Required manual environment setup

### After (Vocareum Edition)
- ✅ No `.env` file needed
- ✅ Uses Anthropic's Claude via Vocareum educational platform
- ✅ API key configured directly in code
- ✅ Simplified setup for students

## Quick Start

### Step 1: Get Your API Key

Your instructor will provide you with a Vocareum API key that looks like this:
```
voc-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 2: Configure the API Key

1. Open the file `mcp_simple_chatbot/main.py`
2. Find these lines near the top (around line 16-20):
   ```python
   # VOCAREUM CONFIGURATION
   # Students: Your instructor will provide you with a Vocareum API key
   # Replace the value below with your assigned key
   VOCAREUM_API_KEY = "voc-184494821118751213237176904c8dab622c9.37059815"
   ```
3. Replace the placeholder with **your assigned API key**

### Step 3: Install Dependencies

Navigate to the simple-chatbot directory and install requirements:

```bash
cd python-sdk-main/examples/clients/simple-chatbot
pip install -r mcp_simple_chatbot/requirements.txt
```

### Step 4: Test Your Configuration (Optional but Recommended)

Run the test script to verify your API key works:

```bash
python test_vocareum.py
```

You should see:
```
✅ SUCCESS: Claude responded with: Hello from Vocareum!
```

### Step 5: Run the Chatbot

```bash
cd mcp_simple_chatbot
python main.py
```

## What This Example Demonstrates

This chatbot showcases how to build an **MCP Client** that:

1. **Connects to multiple MCP servers** (SQLite and Puppeteer in the default config)
2. **Discovers tools automatically** from connected servers
3. **Uses Claude to intelligently select tools** based on user questions
4. **Executes tools** and returns results in natural language

## Example Interactions

Once the chatbot is running, try these commands:

### Using SQLite Tools
```
You: What tables are in the database?
```

### Using Puppeteer Tools
```
You: Take a screenshot of https://example.com
```

### General Conversation
```
You: What tools do you have available?
```

## Architecture Overview

```
┌─────────────────────┐
│   User (You)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   MCP Client        │
│   (main.py)         │
│                     │
│  ┌───────────────┐  │
│  │ LLMClient     │  │──────► Vocareum Claude API
│  │ (Claude)      │  │        (claude.vocareum.com)
│  └───────────────┘  │
│                     │
│  ┌───────────────┐  │
│  │ ChatSession   │  │
│  └───────────────┘  │
│                     │
│  ┌───────────────┐  │
│  │ Server Class  │  │
│  │ (MCP Protocol)│  │
│  └───────────────┘  │
└──────────┬──────────┘
           │
           ▼
    ┌─────────────┐         ┌─────────────┐
    │ SQLite      │         │ Puppeteer   │
    │ MCP Server  │         │ MCP Server  │
    └─────────────┘         └─────────────┘
```

## Key Classes

### `Configuration`
- Manages API key configuration
- Loads server configuration from `servers_config.json`

### `Server`
- Manages individual MCP server connections
- Handles tool discovery and execution
- Supports stdio transport (local processes)

### `Tool`
- Represents an individual tool
- Formats tool information for Claude

### `LLMClient`
- Communicates with Claude via Vocareum
- Handles message formatting
- Manages API requests/responses

### `ChatSession`
- Orchestrates the conversation flow
- Processes Claude's responses
- Executes tools when requested
- Returns natural language results

## Troubleshooting

### Problem: "VOCAREUM_API_KEY not configured"
**Solution:** Make sure you've updated the `VOCAREUM_API_KEY` in `main.py` with your assigned key.

### Problem: "Error getting Claude response"
**Solution:**
1. Verify your API key is correct
2. Check your internet connection
3. Ensure the Vocareum endpoint is accessible

### Problem: "Server X not initialized"
**Solution:** Check that the required MCP servers are installed:
- SQLite: `uvx mcp-server-sqlite`
- Puppeteer: `npx -y @modelcontextprotocol/server-puppeteer`

### Problem: Import errors
**Solution:** Reinstall dependencies:
```bash
pip install -r mcp_simple_chatbot/requirements.txt
```

## Technical Details

### API Configuration
- **Endpoint:** `https://claude.vocareum.com`
- **Model:** `claude-sonnet-4-5-20250929`
- **Max Tokens:** 4096
- **Authentication:** Vocareum API key (starts with `voc-`)

### Dependencies
- `anthropic>=0.40.0` - Anthropic Python SDK for Claude
- `mcp>=1.0.0` - Model Context Protocol SDK
- `uvicorn>=0.32.1` - ASGI server (used by some MCP servers)

### File Structure
```
simple-chatbot/
├── README.MD                      # Main documentation
├── VOCAREUM_SETUP_GUIDE.md       # This file
├── test_vocareum.py              # Test script
└── mcp_simple_chatbot/
    ├── main.py                   # Main chatbot implementation
    ├── requirements.txt          # Python dependencies
    └── servers_config.json       # MCP server configuration
```

## Learning Objectives

By working with this example, you'll learn:

1. ✅ How to build an MCP client from scratch
2. ✅ How to connect to multiple MCP servers
3. ✅ How to integrate an LLM (Claude) with MCP
4. ✅ How tools are discovered and executed
5. ✅ How to handle tool results and generate natural responses
6. ✅ Best practices for error handling and logging

## Next Steps

1. **Modify the system prompt** in `ChatSession.start()` to customize Claude's behavior
2. **Add more MCP servers** by editing `servers_config.json`
3. **Experiment with different tools** available from MCP servers
4. **Build your own MCP server** and connect it to this client

## Resources

- [MCP Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [Available MCP Servers](https://github.com/modelcontextprotocol/servers)
- [Anthropic Claude API Docs](https://docs.anthropic.com/)

## Support

If you encounter issues:
1. Check this troubleshooting guide
2. Review the error messages in the console
3. Ask your instructor for help
4. Check the course discussion forum

---

**Happy coding! 🚀**
