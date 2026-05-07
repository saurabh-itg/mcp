import asyncio
import ollama
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 1. Define how to start your server
# Replace "server.py" with the actual filename of your FastMCP server
server_params = StdioServerParameters(
    command=sys.executable,
    args=["server.py"], 
    env=None
)

async def main():
    # 2. Establish the connection via stdio
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # Fetch tools from the server
            # Note: MCP returns a 'tools' object with a .tools list
            tools_result = await session.list_tools()
            mcp_tools = tools_result.tools

            # Convert MCP tools to Ollama's expected format
            ollama_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                }
                for tool in mcp_tools
            ]

            while True:
                user_input = input("\nAsk something (or 'quit'): ")
                if user_input.lower() == 'quit':
                    break

                # Ask the LLM
                response = ollama.chat(
                    model="llama3.2:latest",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant. Use tools when needed."},
                        {"role": "user", "content": user_input}
                    ],
                    tools=ollama_tools
                )

                # Handle tool calls
                if response.message.tool_calls:
                    for tool_call in response.message.tool_calls:
                        name = tool_call.function.name
                        args = tool_call.function.arguments
                        
                        print(f"🔧 Calling tool: {name} with {args}")
                        
                        # Call the tool through the MCP session
                        result = await session.call_tool(name, args)
                        print(f"🧠 Tool Result: {result.content[0].text}")
                else:
                    print(f"🧠 Assistant: {response.message.content}")

if __name__ == "__main__":
    asyncio.run(main())
