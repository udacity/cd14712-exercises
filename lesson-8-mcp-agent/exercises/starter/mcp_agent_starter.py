"""
MCP Agent - Starter Code
========================

Challenge: Transform the simple chatbot into an autonomous agent that can:
1. Analyze a goal and break it down into tasks
2. Execute tools in a logical sequence
3. Handle errors and retry failed operations
4. Maintain state between tool calls
5. Provide progress updates

The agent should be able to complete multi-step tasks autonomously,
such as "Research and summarize information about Python MCP servers"
or "Create a database, populate it with data, and generate a report"

IMPORTANT: This code has been configured to use Vocareum API keys.
"""

import asyncio
import json
import logging
import os
import shutil
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# VOCAREUM CONFIGURATION
VOCAREUM_API_KEY = "voc-184494821118751213237176904c8dab622c9.37059815"
VOCAREUM_BASE_URL = "https://claude.vocareum.com"


class TaskStatus(Enum):
    """Status of a task in the agent's plan."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Task:
    """Represents a single task in the agent's execution plan."""
    id: int
    description: str
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    dependencies: List[int] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class AgentMemory:
    """Maintains the agent's memory and context between operations."""

    def __init__(self):
        self.facts: List[str] = []
        self.task_history: List[Task] = []
        self.context: Dict[str, Any] = {}

    def add_fact(self, fact: str) -> None:
        """Add a learned fact to memory."""
        self.facts.append(fact)
        logging.info(f"Learned: {fact}")

    def add_task_result(self, task: Task) -> None:
        """Store a completed task and its result."""
        self.task_history.append(task)

    # TODO: Implement a method to retrieve relevant facts for a given context
    def get_relevant_facts(self, query: str, max_facts: int = 5) -> List[str]:
        """
        Retrieve facts relevant to the current query.

        Hint: For now, you can return the most recent facts.
        Advanced: Implement semantic similarity matching.
        """
        # TODO: Implement fact retrieval logic
        pass

    def get_summary(self) -> str:
        """Get a summary of the agent's memory state."""
        completed_tasks = [t for t in self.task_history if t.status == TaskStatus.COMPLETED]
        return f"Memory: {len(self.facts)} facts, {len(completed_tasks)} completed tasks"


class Configuration:
    """Manages configuration for the MCP agent."""

    def __init__(self) -> None:
        self.api_key = VOCAREUM_API_KEY

    @staticmethod
    def load_config(file_path: str) -> dict[str, Any]:
        with open(file_path, "r") as f:
            return json.load(f)

    @property
    def llm_api_key(self) -> str:
        if not self.api_key:
            raise ValueError("VOCAREUM_API_KEY not configured")
        return self.api_key


class Server:
    """Manages MCP server connections and tool execution."""

    def __init__(self, name: str, config: dict[str, Any]) -> None:
        self.name: str = name
        self.config: dict[str, Any] = config
        self.session: ClientSession | None = None
        self._cleanup_lock: asyncio.Lock = asyncio.Lock()
        self.exit_stack: AsyncExitStack = AsyncExitStack()

    async def initialize(self) -> None:
        """Initialize the server connection."""
        command = shutil.which("npx") if self.config["command"] == "npx" else self.config["command"]
        if command is None:
            raise ValueError("The command must be a valid string and cannot be None.")

        server_params = StdioServerParameters(
            command=command,
            args=self.config["args"],
            env={**os.environ, **self.config["env"]} if self.config.get("env") else None,
        )
        try:
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            self.session = session
        except Exception as e:
            logging.error(f"Error initializing server {self.name}: {e}")
            await self.cleanup()
            raise

    async def list_tools(self) -> list[Any]:
        """List available tools from the server."""
        if not self.session:
            raise RuntimeError(f"Server {self.name} not initialized")

        tools_response = await self.session.list_tools()
        tools = []

        for item in tools_response:
            if isinstance(item, tuple) and item[0] == "tools":
                tools.extend(Tool(tool.name, tool.description, tool.inputSchema, tool.title) for tool in item[1])

        return tools

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        retries: int = 2,
        delay: float = 1.0,
    ) -> Any:
        """Execute a tool with retry mechanism."""
        if not self.session:
            raise RuntimeError(f"Server {self.name} not initialized")

        attempt = 0
        while attempt < retries:
            try:
                logging.info(f"Executing {tool_name}...")
                result = await self.session.call_tool(tool_name, arguments)
                return result

            except Exception as e:
                attempt += 1
                logging.warning(f"Error executing tool: {e}. Attempt {attempt} of {retries}.")
                if attempt < retries:
                    await asyncio.sleep(delay)
                else:
                    raise

    async def cleanup(self) -> None:
        """Clean up server resources."""
        async with self._cleanup_lock:
            try:
                await self.exit_stack.aclose()
                self.session = None
            except Exception as e:
                logging.error(f"Error during cleanup of server {self.name}: {e}")


class Tool:
    """Represents a tool with its properties."""

    def __init__(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        title: str | None = None,
    ) -> None:
        self.name: str = name
        self.title: str | None = title
        self.description: str = description
        self.input_schema: dict[str, Any] = input_schema

    def format_for_llm(self) -> str:
        """Format tool information for LLM."""
        args_desc = []
        if "properties" in self.input_schema:
            for param_name, param_info in self.input_schema["properties"].items():
                arg_desc = f"- {param_name}: {param_info.get('description', 'No description')}"
                if param_name in self.input_schema.get("required", []):
                    arg_desc += " (required)"
                args_desc.append(arg_desc)

        output = f"Tool: {self.name}\n"
        if self.title:
            output += f"Title: {self.title}\n"
        output += f"""Description: {self.description}
Arguments:
{chr(10).join(args_desc)}
"""
        return output


class LLMClient:
    """Manages communication with Claude via Vocareum."""

    def __init__(self, api_key: str) -> None:
        self.client = Anthropic(
            api_key=api_key,
            base_url=VOCAREUM_BASE_URL
        )

    def get_response(self, messages: list[dict[str, str]]) -> str:
        """Get a response from Claude."""
        try:
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

        except Exception as e:
            error_message = f"Error getting Claude response: {str(e)}"
            logging.error(error_message)
            return f"Error: {error_message}"


class MCPAgent:
    """
    Autonomous agent that can plan and execute multi-step tasks.

    This agent should:
    1. Analyze goals and create execution plans
    2. Execute tools in sequence
    3. Learn from results and adapt
    4. Handle errors gracefully
    """

    def __init__(self, servers: List[Server], llm_client: LLMClient):
        self.servers = servers
        self.llm_client = llm_client
        self.memory = AgentMemory()
        self.max_iterations = 10
        self.available_tools = []

    async def initialize(self) -> None:
        """Initialize all servers and discover available tools."""
        for server in self.servers:
            try:
                await server.initialize()
                tools = await server.list_tools()
                self.available_tools.extend(tools)
                logging.info(f"Initialized server {server.name} with {len(tools)} tools")
            except Exception as e:
                logging.error(f"Failed to initialize server {server.name}: {e}")

    # TODO: Implement the planning phase
    async def create_plan(self, goal: str) -> List[Task]:
        """
        Create an execution plan for the given goal.

        This should:
        1. Analyze the goal
        2. Break it down into tasks
        3. Identify which tools to use
        4. Determine the order of execution

        Hint: Use the LLM to generate a structured plan
        """
        tools_description = "\n".join([tool.format_for_llm() for tool in self.available_tools])

        # TODO: Create a system prompt that instructs the LLM to create a plan
        system_prompt = f"""You are an AI agent that creates execution plans.

Available tools:
{tools_description}

Create a detailed plan to achieve the user's goal.
Return a JSON array of tasks with the following structure:
[
  {{
    "id": 1,
    "description": "task description",
    "tool_name": "tool_to_use",
    "tool_args": {{"arg1": "value1"}},
    "dependencies": []
  }}
]

Important:
- Each task should use exactly one tool
- Include dependencies to ensure proper execution order
- Be specific about tool arguments
"""

        # TODO: Get the plan from the LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Goal: {goal}"}
        ]

        # TODO: Parse the LLM response and convert to Task objects
        response = self.llm_client.get_response(messages)

        # TODO: Implement parsing logic
        # For now, return an empty list
        return []

    # TODO: Implement the execution phase
    async def execute_task(self, task: Task) -> None:
        """
        Execute a single task and update its status.

        This should:
        1. Find the appropriate server for the tool
        2. Execute the tool with the given arguments
        3. Store the result in the task
        4. Update the task status
        5. Learn from the result
        """
        task.status = TaskStatus.IN_PROGRESS

        try:
            # TODO: Find which server has this tool
            server_with_tool = None

            # TODO: Execute the tool
            if server_with_tool:
                result = None  # Replace with actual execution
                task.result = result
                task.status = TaskStatus.COMPLETED

                # TODO: Extract facts from the result
                # self.memory.add_fact(...)
            else:
                task.status = TaskStatus.FAILED
                task.error = f"Tool {task.tool_name} not found"

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            logging.error(f"Task {task.id} failed: {e}")

        finally:
            self.memory.add_task_result(task)

    # TODO: Implement the main execution loop
    async def run(self, goal: str) -> str:
        """
        Main execution loop for the agent.

        This should:
        1. Create a plan
        2. Execute tasks in order
        3. Monitor progress
        4. Adapt if tasks fail
        5. Return a summary of results
        """
        logging.info(f"Agent starting with goal: {goal}")

        # Initialize servers
        await self.initialize()

        # TODO: Create the execution plan
        plan = await self.create_plan(goal)

        if not plan:
            return "Failed to create execution plan"

        logging.info(f"Created plan with {len(plan)} tasks")

        # TODO: Execute tasks in order, respecting dependencies
        for task in plan:
            # TODO: Check if dependencies are completed

            # TODO: Execute the task
            await self.execute_task(task)

            # TODO: Check if we should continue or abort
            if task.status == TaskStatus.FAILED:
                logging.warning(f"Task {task.id} failed: {task.error}")
                # TODO: Decide whether to continue or abort

        # TODO: Generate a summary of what was accomplished
        summary = self.generate_summary(plan)

        return summary

    def generate_summary(self, plan: List[Task]) -> str:
        """
        Generate a human-readable summary of the execution.

        TODO: Implement a method that:
        1. Counts successful vs failed tasks
        2. Extracts key results
        3. Provides a concise summary
        """
        completed = sum(1 for t in plan if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in plan if t.status == TaskStatus.FAILED)

        summary = f"Execution Summary:\n"
        summary += f"- Completed: {completed}/{len(plan)} tasks\n"
        summary += f"- Failed: {failed} tasks\n"
        summary += f"- {self.memory.get_summary()}\n"

        # TODO: Add more detailed results

        return summary

    async def cleanup(self) -> None:
        """Clean up all server connections."""
        for server in reversed(self.servers):
            try:
                await server.cleanup()
            except Exception as e:
                logging.warning(f"Error cleaning up server {server.name}: {e}")


# TODO: Implement the main function
async def main():
    """
    Main entry point for the MCP Agent.

    TODO:
    1. Load configuration
    2. Initialize servers
    3. Create the agent
    4. Get goal from user
    5. Run the agent
    6. Display results
    """
    # Load configuration
    config = Configuration()

    # TODO: Load server configuration from servers_config.json
    # server_config = config.load_config("servers_config.json")

    # TODO: Create servers from configuration
    servers = []  # Replace with actual servers

    # TODO: Create LLM client
    # llm_client = LLMClient(config.llm_api_key)

    # TODO: Create the agent
    # agent = MCPAgent(servers, llm_client)

    # TODO: Get goal from user
    print("MCP Autonomous Agent")
    print("====================")
    goal = input("Enter your goal: ")

    # TODO: Run the agent
    # result = await agent.run(goal)

    # TODO: Display results
    print("\nResults:")
    # print(result)

    # TODO: Cleanup
    # await agent.cleanup()


if __name__ == "__main__":
    # TODO: Run the async main function
    # asyncio.run(main())
    print("Please implement the main function to run the agent")