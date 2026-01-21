from httpx import stream
from mcp import ClientSession, StdioServerParameters, types
from mcp.client import stdio
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client

import asyncio


from pydantic import AnyUrl

# create server parameters for this particular stdio connection

server_params = StdioServerParameters(
    command="uv",
    args=["run", "mcp", "run", "server.py"]
)

# create a run function 
async def run():
    async with streamablehttp_client(url="http://localhost:8000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            # 1. initialized (create a new ClientSession)
            await session.initialize()

            # 2. list available prompts
            prompts = await session.list_prompts()
            print(f"Available prompts: {[p.name for p in prompts.prompts]}")

            # 3. retrieve a prompt based on the name
            if prompts.prompts:
                prompt = await session.get_prompt("summarize_notes", arguments={"name": "October12"})
                print(f"Prompt result: {prompt.messages[0].content}")

            # 4. list available resources
            resources = await session.list_resources()
            print(f"Available resources: {[r.uri for r in resources.resources]}")

            # 5. retrieve a resource based on the name
            resource_content = await session.read_resource(AnyUrl("resource://reference"))
            content_block = resource_content.contents[0]
            if isinstance(content_block, types.TextContent):
                print(f"Resource content: {content_block.text}")

            # 6. list available tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")

            # 7. call tool
            result = await session.call_tool("add_note", arguments={"name": "October13", "content": "Today is October 13th, 2025"})
            result_unstructured = result.content[0]
            if isinstance(result_unstructured, types.TextContent):
                print(f"Tool result: {result_unstructured.text}")
            result_structured = result.structuredContent
            print(f"Structured tool result: {result_structured}")

# main method 
def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()