import asyncio

from mcp import Client
from ollama import AsyncClient

from main import mcp

import json


async def main():
    async with Client(mcp) as client:
        result = await client.list_tools()

        ollama_tools = []

        for tool in result.tools:
            ollama_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.input_schema,
                },
            })

        ollama = AsyncClient()

        messages = [
            {
                "role": "user",
                "content": "Get UK GDP growth from 2020 to 2023 using the available tools.",
            }
        ]

        response = await ollama.chat(
            model="qwen3:1.7b",
            messages=messages,
            tools=ollama_tools,
            think=False,
        )
        messages.append(response.message)

        print("Tool calls:", response.message.tool_calls)

        available_tools = {tool.name for tool in result.tools}

        for tool_call in response.message.tool_calls or []:
            name = tool_call.function.name
            arguments = tool_call.function.arguments

            if name not in available_tools:
                print("Unknown tool:", name)
                continue

            tool_result = await client.call_tool(name, arguments)

            content = (
                tool_result.structured_content
                if not tool_result.is_error
                else {"error": str(tool_result.content)}
            )

            messages.append({
                "role": "tool",
                "tool_name": name,
                "content": json.dumps(content),
            })

            print("Executed:", name)
            print("Error:", tool_result.is_error)
            print("Result:", tool_result.structured_content)

        final_response = await ollama.chat(
            model="qwen3:1.7b",
            messages=messages,
            think=False,
        )

        print("Qwen3 answer:", final_response.message.content)

        # print("Ollama tools:", len(ollama_tools))
        # print("First tool:", ollama_tools[0]["function"]["name"])

        # for tool in result.tools:
        #     print(tool.name)
        #     print("Output schema:", tool.output_schema)

        # result = await client.call_tool(
        #     "get_indicator",
        #     {
        #         "country": "GBR",
        #         "indicator": "NY.GDP.MKTP.KD.ZG",
        #         "start_year": 2020,
        #         "end_year": 2023,
        #     },
        # )

        # print("Error:", result.is_error)
        # print("Data:", result.structured_content)
        # print("Content:", result.content)


if __name__ == "__main__":
    asyncio.run(main())