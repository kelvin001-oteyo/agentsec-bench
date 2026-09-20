import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from ..core.agent import Agent
from ..core.types import Tool, ToolCall

load_dotenv()


def tool_to_openai_schema(tool: Tool) -> dict:
    schema = tool.parameters.model_json_schema()
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": schema,
        },
    }


class OpenAIAgent(Agent):
    name = "openai-live-agent"
    role = "default"

    def __init__(self, model: str = "gpt-4o-mini-2024-07-18"):
        self.model = model
        self.client = OpenAI()

    def query(self, prompt, tools, env):
        openai_tools = [tool_to_openai_schema(t) for t in tools]

        messages = [
            {"role": "system", "content": "You are a helpful assistant with access to tools."},
            {"role": "user", "content": prompt},
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=openai_tools,
        )

        msg = response.choices[0].message
        trace = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                trace.append(ToolCall(tool_name=tc.function.name, args=args))

        return [{"role": "assistant", "content": msg.content}], trace