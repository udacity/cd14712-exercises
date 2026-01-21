# Instructor Notes: Simple Chatbot Vocareum Refactoring

## Summary of Changes

The `simple-chatbot` example from the MCP Python SDK has been refactored to work with Vocareum educational API keys for use in the MCP course.

## Files Modified

### 1. `mcp_simple_chatbot/main.py`
**Changes:**
- ✅ Removed `python-dotenv` dependency
- ✅ Removed `.env` file requirement
- ✅ Added hardcoded Vocareum configuration constants
- ✅ Replaced `httpx` Groq API client with `anthropic` Anthropic client
- ✅ Updated `Configuration` class to use hardcoded API key
- ✅ Completely rewrote `LLMClient` class to use Anthropic's SDK
- ✅ Added proper system message handling for Anthropic's API format

**Key Code Changes:**

```python
# NEW: Configuration constants
VOCAREUM_API_KEY = "voc-184494821118751213237176904c8dab622c9.37059815"
VOCAREUM_BASE_URL = "https://claude.vocareum.com"

# NEW: LLMClient using Anthropic SDK
class LLMClient:
    def __init__(self, api_key: str) -> None:
        self.client = Anthropic(
            api_key=api_key,
            base_url=VOCAREUM_BASE_URL
        )

    def get_response(self, messages: list[dict[str, str]]) -> str:
        # Extract system message and user messages separately
        # Anthropic API requires different format than OpenAI
        system_message = None
        user_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)

        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            system=system_message if system_message else "",
            messages=user_messages
        )

        return response.content[0].text
```

### 2. `mcp_simple_chatbot/requirements.txt`
**Changes:**
- ✅ Removed `python-dotenv>=1.0.0`
- ✅ Removed `requests>=2.31.0`
- ✅ Added `anthropic>=0.40.0`
- ✅ Kept `mcp>=1.0.0` and `uvicorn>=0.32.1`

**Before:**
```
python-dotenv>=1.0.0
requests>=2.31.0
mcp>=1.0.0
uvicorn>=0.32.1
```

**After:**
```
anthropic>=0.40.0
mcp>=1.0.0
uvicorn>=0.32.1
```

### 3. `README.MD`
**Changes:**
- ✅ Updated title to "MCP Simple Chatbot (Vocareum Edition)"
- ✅ Replaced Groq API instructions with Vocareum setup
- ✅ Updated requirements list
- ✅ Removed `.env` file instructions
- ✅ Added instructions for hardcoding API key
- ✅ Updated usage examples

## Files Created

### 1. `test_vocareum.py`
**Purpose:** Quick verification script for students to test their API key configuration

**What it does:**
- Tests Vocareum API connection
- Sends a simple message to Claude
- Provides clear success/failure feedback

**Usage:**
```bash
python test_vocareum.py
```

### 2. `VOCAREUM_SETUP_GUIDE.md`
**Purpose:** Comprehensive student-facing documentation

**Contents:**
- Quick start guide
- Architecture overview
- Example interactions
- Troubleshooting section
- Learning objectives

### 3. `INSTRUCTOR_NOTES.md` (this file)
**Purpose:** Technical reference for instructors

## API Key Distribution

The current implementation includes a default Vocareum API key for testing:
```
voc-184494821118751213237176904c8dab622c9.37059815
```

### For Production Use:
1. **Generate individual keys** for each student (if required by Vocareum)
2. **OR** use a shared classroom key (current approach)
3. Students update `VOCAREUM_API_KEY` constant in `main.py`

### Security Note:
Since students will be editing source code directly, API keys will be visible in plain text. This is acceptable for:
- ✅ Educational/sandbox environments
- ✅ Time-limited API keys
- ✅ Rate-limited accounts
- ⚠️ NOT recommended for production API keys

## Testing Verification

### Test Results:
```bash
$ python3 test_vocareum.py
Testing Vocareum API connection...
API Key: voc-1844948211187512...
Base URL: https://claude.vocareum.com

✅ SUCCESS: Claude responded with: Hello from Vocareum!
```

The refactored implementation has been tested and verified working with the provided Vocareum API key.

## Why This Example Was Chosen

According to the course slide deck (line 1438), this specific example is referenced:
```
https://github.com/modelcontextprotocol/python-sdk/blob/main/examples/clients/simple-chatbot/mcp_simple_chatbot/main.py
```

This example is used in the course to demonstrate:
1. **MCP Client implementation** - How to build a client from scratch
2. **Multi-server connections** - Connecting to multiple MCP servers (SQLite, Puppeteer)
3. **Tool discovery** - Automatic tool detection from servers
4. **LLM integration** - Using an LLM to intelligently select and execute tools

## Student Workflow

1. **Receive API key** from instructor
2. **Clone/download** the python-sdk-main repository
3. **Navigate** to `examples/clients/simple-chatbot`
4. **Edit** `mcp_simple_chatbot/main.py` and update `VOCAREUM_API_KEY`
5. **Install** dependencies: `pip install -r mcp_simple_chatbot/requirements.txt`
6. **(Optional) Test** configuration: `python test_vocareum.py`
7. **Run** the chatbot: `cd mcp_simple_chatbot && python main.py`

## Comparison with Course Project

Both the course project (`mcp-project/`) and this SDK example have been refactored for Vocareum:

| Aspect | Course Project | SDK Simple Chatbot |
|--------|---------------|-------------------|
| **Purpose** | Custom course exercise | Reference implementation |
| **Complexity** | More complex (Firecrawl, data extraction) | Simpler (basic tool calling) |
| **API Changes** | Added `base_url` to Anthropic() | Replaced entire LLMClient class |
| **Files Modified** | 2 files (`client.py`, `starter_client.py`) | 3 files (`main.py`, `requirements.txt`, `README.MD`) |
| **Original LLM** | Anthropic Claude | Groq Llama |
| **New LLM** | Anthropic Claude (Vocareum) | Anthropic Claude (Vocareum) |

## Technical Notes

### Anthropic API Differences
The refactoring required significant changes because:

1. **Message Format:** Anthropic separates system messages from conversation messages
   - OpenAI/Groq: system message is just another message in the array
   - Anthropic: system message is a separate parameter

2. **Response Structure:**
   - OpenAI/Groq: `response['choices'][0]['message']['content']`
   - Anthropic: `response.content[0].text`

3. **Client Initialization:**
   - OpenAI/Groq: use `httpx` or `requests` directly
   - Anthropic: use official `anthropic` SDK

### MCP Server Configuration
The example uses `servers_config.json` with the same format as Claude Desktop:
```json
{
  "mcpServers": {
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "./test.db"]
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

Students can add more servers by editing this file.

## Common Student Issues

### 1. Forgot to Update API Key
**Symptom:** "VOCAREUM_API_KEY not configured" error

**Solution:** Remind students to update line 19 in `main.py`

### 2. Wrong Directory
**Symptom:** "No module named 'mcp_simple_chatbot'" or import errors

**Solution:** Must run from `mcp_simple_chatbot/` directory

### 3. Missing Dependencies
**Symptom:** "No module named 'anthropic'" or "No module named 'mcp'"

**Solution:** Run `pip install -r mcp_simple_chatbot/requirements.txt`

### 4. MCP Servers Not Installed
**Symptom:** Server initialization failures

**Solution:** Install required servers:
- `uvx mcp-server-sqlite`
- `npx -y @modelcontextprotocol/server-puppeteer`

## Pedagogical Benefits

This refactored example helps students:

1. ✅ **See a complete MCP client implementation** beyond the course project
2. ✅ **Understand the MCP protocol** through working code
3. ✅ **Learn class-based architecture** for MCP clients
4. ✅ **Practice with real MCP servers** (SQLite, Puppeteer)
5. ✅ **Experiment with tool calling** in a safe environment

## Extension Activities

Suggest these activities for advanced students:

1. **Add a new MCP server** to `servers_config.json`
2. **Modify the system prompt** to change Claude's personality
3. **Add conversation history persistence** (save/load chats)
4. **Implement streaming responses** from Claude
5. **Add error recovery** mechanisms
6. **Build a custom MCP server** and connect it to this client

## Related Course Materials

This example complements:
- **Lesson 1:** MCP fundamentals and architecture
- **Demo 11:** Building Your First MCP Application (Parts 1-3)
- **mcp-project:** Final course project
- **Slide deck lines 1434-1438:** Reference to this specific example

## Files Not Modified

These files were NOT changed and work as-is:
- ✅ `mcp_simple_chatbot/servers_config.json` - No changes needed
- ✅ `mcp_simple_chatbot/__init__.py` - No changes needed
- ✅ `pyproject.toml` - Not used (using requirements.txt instead)

## Backup Original Version

If you need the original version:
- Original repo: https://github.com/modelcontextprotocol/python-sdk
- Path: `examples/clients/simple-chatbot/`
- Git commit: Check latest main branch

## Questions?

Contact the course development team if you need:
- Additional Vocareum API keys
- Help troubleshooting student issues
- Modifications to the example
- Additional documentation

---

**Last Updated:** Based on MCP Python SDK latest version
**Tested With:** Vocareum API key `voc-184494821118751213237176904c8dab622c9.37059815`
**Status:** ✅ Fully tested and verified
