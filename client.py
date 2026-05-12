import asyncio
import ollama
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 1. Define how to start your server

server_params = StdioServerParameters(
    command=sys.executable,
    args=["server.py"], 
    env=None
)
async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            tools_result = await session.list_tools()
            ollama_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                }
                for tool in tools_result.tools
            ]

            # Maintain conversation history
            messages = [{
        "role": "system", 
        "content": (
            "You are a strict file system assistant. "
            "ONLY report the files returned by the tools. "
            "Do not assume other files exist. "
            "If the tool returns an error or a limited list, report exactly that."
        )
    }]
# ... (initialization code above stays the same)
            messages = [{"role": "system", "content": "You are a helpful assistant. Use tools when needed. ONLY report files returned by tools."}]

            while True:
                user_input = input("\nAsk something (or 'quit'): ")
                if user_input.lower() == 'quit':
                    break

                messages.append({"role": "user", "content": user_input})

                response = ollama.chat(
                    model="llama3.2:latest",
                    messages=messages,
                    tools=ollama_tools
                )

                # Add model's response to history
                messages.append(response.message)

                if response.message.tool_calls:
                    for tool_call in response.message.tool_calls:
                        name = tool_call.function.name
                        args = tool_call.function.arguments
                        
                        # 🛠️ FIX: Clean up nested dictionaries (fixes the Pydantic error)
                        if isinstance(args, dict):
                            for key, value in args.items():
                                if isinstance(value, dict) and "value" in value:
                                    args[key] = value["value"]
                        
                        print(f"🔧 Calling tool: {name} with {args}")
                        
                        try:
                            # Call the tool through the MCP session
                            result = await session.call_tool(name, args)
                            # Extract the text content
                            tool_output = result.content[0].text 
                        except Exception as e:
                            tool_output = f"Error: {str(e)}"
                        
                        print(f" Tool Result: {tool_output}")

                        # 🛠️ FIX: 'tool_output' is now guaranteed to be defined here
                        messages.append({
                            "role": "tool",
                            "content": tool_output,
                        })

                #     # Final pass to let the LLM see the results
                #     final_response = ollama.chat(
                #         model="llama3.2:latest",
                #         messages=messages
                #     )
                #     print(f" Assistant: {final_response.message.content}")
                #     messages.append(final_response.message)
                # else:
                #     print(f" Assistant: {response.message.content}")

                    # Second LLM call: Send the tool results back to get final answer
                    final_response = ollama.chat(
                        model="llama3.2:latest",
                        messages=messages
                    )
                    print(f" Assistant: {final_response.message.content}")
                    messages.append(final_response.message)
                else:
                    print(f" Assistant: {response.message.content}")

if __name__ == "__main__":
    asyncio.run(main())
