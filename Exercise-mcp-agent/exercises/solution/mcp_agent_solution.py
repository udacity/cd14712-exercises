"""
MCP Agent - Solution Code
=========================

This is the complete solution for the MCP Agent exercise.
The agent can autonomously plan and execute multi-step tasks
using available MCP tools.

Features:
- Goal analysis and task planning
- Sequential and parallel task execution
- Error handling and recovery
- Memory and context management
- Progress tracking and reporting
"""

import asyncio
import json
import logging
import os
import shutil
import re
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

    def get_relevant_facts(self, query: str, max_facts: int = 5) -> List[str]:
        """
        Retrieve facts relevant to the current query.

        For this implementation, we return the most recent facts.
        In a production system, you might implement semantic similarity.
        """
        # Return the most recent facts that might be relevant
        relevant_facts = []
        query_lower = query.lower()

        # First try to find facts containing words from the query
        for fact in reversed(self.facts):
            if any(word in fact.lower() for word in query_lower.split()):
                relevant_facts.append(fact)
                if len(relevant_facts) >= max_facts:
                    break

        # If we don't have enough, add recent facts
        if len(relevant_facts) < max_facts:
            for fact in reversed(self.facts):
                if fact not in relevant_facts:
                    relevant_facts.append(fact)
                    if len(relevant_facts) >= max_facts:
                        break

        return relevant_facts

    def get_summary(self) -> str:
        """Get a summary of the agent's memory state."""
        completed_tasks = [t for t in self.task_history if t.status == TaskStatus.COMPLETED]
        failed_tasks = [t for t in self.task_history if t.status == TaskStatus.FAILED]
        return f"Memory: {len(self.facts)} facts, {len(completed_tasks)} completed tasks, {len(failed_tasks)} failed tasks"


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
                logging.info(f"Executing {tool_name} with args: {arguments}")
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
    """

    def __init__(self, servers: List[Server], llm_client: LLMClient):
        self.servers = servers
        self.llm_client = llm_client
        self.memory = AgentMemory()
        self.max_iterations = 10
        self.available_tools = []
        self.tool_to_server = {}  # Map tool names to servers

    async def initialize(self) -> None:
        """Initialize all servers and discover available tools."""
        for server in self.servers:
            try:
                await server.initialize()
                tools = await server.list_tools()
                self.available_tools.extend(tools)

                # Map tools to servers
                for tool in tools:
                    self.tool_to_server[tool.name] = server

                logging.info(f"Initialized server {server.name} with {len(tools)} tools")
            except Exception as e:
                logging.error(f"Failed to initialize server {server.name}: {e}")

    async def create_plan(self, goal: str) -> List[Task]:
        """
        Create an execution plan for the given goal.
        """
        tools_description = "\n".join([tool.format_for_llm() for tool in self.available_tools])

        # Get relevant facts from memory
        relevant_facts = self.memory.get_relevant_facts(goal)
        facts_context = ""
        if relevant_facts:
            facts_context = "\n\nRelevant context from previous operations:\n"
            facts_context += "\n".join(f"- {fact}" for fact in relevant_facts)

        system_prompt = f"""You are an AI agent that creates execution plans.

Available tools:
{tools_description}
{facts_context}

Create a detailed plan to achieve the user's goal.
Return ONLY a JSON array of tasks with the following structure:
[
  {{
    "id": 1,
    "description": "task description",
    "tool_name": "exact_tool_name",
    "tool_args": {{"arg_name": "value"}},
    "dependencies": []
  }},
  {{
    "id": 2,
    "description": "another task",
    "tool_name": "another_tool",
    "tool_args": {{"arg": "value"}},
    "dependencies": [1]
  }}
]

Important:
- Each task should use exactly one tool
- Use the exact tool names provided
- Include dependencies (task IDs that must complete first)
- Be specific about tool arguments
- Tasks with no dependencies can run in parallel
- Return ONLY the JSON array, no explanations"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Goal: {goal}"}
        ]

        response = self.llm_client.get_response(messages)

        # Clean the response to extract JSON
        response = response.strip()

        # Try to find JSON array in the response
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            response = json_match.group(0)

        try:
            plan_data = json.loads(response)

            # Convert to Task objects
            tasks = []
            for task_data in plan_data:
                task = Task(
                    id=task_data["id"],
                    description=task_data["description"],
                    tool_name=task_data.get("tool_name"),
                    tool_args=task_data.get("tool_args", {}),
                    dependencies=task_data.get("dependencies", [])
                )
                tasks.append(task)

            logging.info(f"Created plan with {len(tasks)} tasks")
            return tasks

        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse plan JSON: {e}")
            logging.error(f"Response was: {response}")

            # Return a simple fallback plan
            return [
                Task(
                    id=1,
                    description="Unable to create detailed plan - will attempt basic exploration",
                    tool_name=None,
                    tool_args={},
                    dependencies=[]
                )
            ]

    async def execute_task(self, task: Task) -> None:
        """
        Execute a single task and update its status.
        """
        task.status = TaskStatus.IN_PROGRESS
        logging.info(f"Executing task {task.id}: {task.description}")

        try:
            if not task.tool_name:
                # This is an informational task
                task.status = TaskStatus.COMPLETED
                task.result = "Informational task completed"
                return

            # Find which server has this tool
            server_with_tool = self.tool_to_server.get(task.tool_name)

            if server_with_tool:
                # Execute the tool
                result = await server_with_tool.execute_tool(
                    task.tool_name,
                    task.tool_args or {}
                )

                task.result = result
                task.status = TaskStatus.COMPLETED

                # Extract and store facts from the result
                if result:
                    fact = f"Task '{task.description}' completed with result: {str(result)[:100]}"
                    self.memory.add_fact(fact)

                    # If the result contains useful information, store it
                    if isinstance(result, dict):
                        for key, value in result.items():
                            if value:
                                self.memory.add_fact(f"{key}: {str(value)[:100]}")

                logging.info(f"Task {task.id} completed successfully")
            else:
                task.status = TaskStatus.FAILED
                task.error = f"Tool {task.tool_name} not found"
                logging.error(f"Tool {task.tool_name} not found in available servers")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            logging.error(f"Task {task.id} failed: {e}")

        finally:
            self.memory.add_task_result(task)

    def can_execute_task(self, task: Task, completed_tasks: set) -> bool:
        """Check if a task's dependencies are satisfied."""
        return all(dep_id in completed_tasks for dep_id in task.dependencies)

    async def run(self, goal: str) -> str:
        """
        Main execution loop for the agent.
        """
        logging.info(f"Agent starting with goal: {goal}")
        print(f"\n🎯 Goal: {goal}\n")

        # Initialize servers
        print("🔧 Initializing MCP servers...")
        await self.initialize()

        if not self.available_tools:
            return "No tools available. Please check server configuration."

        print(f"✅ Found {len(self.available_tools)} available tools\n")

        # Create the execution plan
        print("📝 Creating execution plan...")
        plan = await self.create_plan(goal)

        if not plan:
            return "Failed to create execution plan"

        print(f"✅ Created plan with {len(plan)} tasks\n")

        # Display the plan
        print("📋 Execution Plan:")
        for task in plan:
            deps = f" (depends on: {task.dependencies})" if task.dependencies else ""
            print(f"  {task.id}. {task.description}{deps}")
        print()

        # Execute tasks respecting dependencies
        completed_tasks = set()
        iterations = 0

        while len(completed_tasks) < len(plan) and iterations < self.max_iterations:
            iterations += 1
            made_progress = False

            for task in plan:
                if task.id in completed_tasks:
                    continue

                if task.status == TaskStatus.FAILED:
                    completed_tasks.add(task.id)  # Mark failed tasks as "done"
                    continue

                if self.can_execute_task(task, completed_tasks):
                    print(f"🔄 Executing task {task.id}: {task.description}")
                    await self.execute_task(task)

                    if task.status == TaskStatus.COMPLETED:
                        print(f"✅ Task {task.id} completed")
                        completed_tasks.add(task.id)
                        made_progress = True
                    elif task.status == TaskStatus.FAILED:
                        print(f"❌ Task {task.id} failed: {task.error}")
                        completed_tasks.add(task.id)

                        # Decide whether to continue
                        critical_task = "critical" in task.description.lower()
                        if critical_task:
                            print("⚠️ Critical task failed, stopping execution")
                            break

            if not made_progress:
                logging.warning("No progress made in this iteration")
                break

        # Generate summary
        print("\n" + "="*50)
        summary = self.generate_summary(plan, goal)
        return summary

    def generate_summary(self, plan: List[Task], goal: str) -> str:
        """Generate a human-readable summary of the execution."""
        completed = [t for t in plan if t.status == TaskStatus.COMPLETED]
        failed = [t for t in plan if t.status == TaskStatus.FAILED]
        pending = [t for t in plan if t.status == TaskStatus.PENDING]

        summary = f"📊 Execution Summary\n"
        summary += f"{'='*50}\n\n"
        summary += f"Goal: {goal}\n\n"
        summary += f"Tasks:\n"
        summary += f"  ✅ Completed: {len(completed)}/{len(plan)}\n"
        summary += f"  ❌ Failed: {len(failed)}\n"
        summary += f"  ⏳ Pending: {len(pending)}\n\n"

        if completed:
            summary += "Completed Tasks:\n"
            for task in completed:
                summary += f"  • {task.description}\n"
                if task.result:
                    result_str = str(task.result)[:200]
                    if len(str(task.result)) > 200:
                        result_str += "..."
                    summary += f"    Result: {result_str}\n"

        if failed:
            summary += "\nFailed Tasks:\n"
            for task in failed:
                summary += f"  • {task.description}\n"
                summary += f"    Error: {task.error}\n"

        summary += f"\n{self.memory.get_summary()}\n"

        # Add key learnings
        if self.memory.facts:
            summary += "\nKey Learnings:\n"
            for fact in self.memory.facts[-5:]:  # Last 5 facts
                summary += f"  • {fact}\n"

        return summary

    async def cleanup(self) -> None:
        """Clean up all server connections."""
        for server in reversed(self.servers):
            try:
                await server.cleanup()
            except Exception as e:
                logging.warning(f"Error cleaning up server {server.name}: {e}")


async def main():
    """Main entry point for the MCP Agent."""

    print("=" * 50)
    print("MCP Autonomous Agent")
    print("=" * 50)
    print("\nThis agent can autonomously plan and execute")
    print("multi-step tasks using available MCP tools.\n")

    # Load configuration
    config = Configuration()

    # Load server configuration
    try:
        server_config = config.load_config("servers_config.json")
    except FileNotFoundError:
        print("⚠️ servers_config.json not found. Using default configuration.")
        server_config = {
            "mcpServers": {
                "sqlite": {
                    "command": "uvx",
                    "args": ["mcp-server-sqlite", "--db-path", "./test.db"]
                }
            }
        }

    # Create servers from configuration
    servers = [
        Server(name, srv_config)
        for name, srv_config in server_config["mcpServers"].items()
    ]

    # Create LLM client
    llm_client = LLMClient(config.llm_api_key)

    # Create the agent
    agent = MCPAgent(servers, llm_client)

    try:
        # Get goal from user or use example
        print("Example goals:")
        print("  1. Create a database table for users and add 3 sample users")
        print("  2. List all tables in the database and describe their structure")
        print("  3. Search for information about Python and SQLite")
        print()

        goal = input("Enter your goal (or press Enter for example): ").strip()

        if not goal:
            goal = "Create a database table called 'tasks' with columns for id, title, description, and completed status. Then add 3 sample tasks."

        # Run the agent
        result = await agent.run(goal)

        # Display results
        print("\n" + "="*50)
        print("Final Results:")
        print("="*50)
        print(result)

    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logging.error(f"Fatal error: {e}", exc_info=True)
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        await agent.cleanup()
        print("✅ Done!")


if __name__ == "__main__":
    asyncio.run(main())