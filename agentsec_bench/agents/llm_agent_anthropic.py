import os
from dotenv import load_dotenv
from anthropic import Anthropic
from ..core.agent import Agent
from ..core.types import Tool, ToolCall

load_dotenv()


def tool_to_anthropic_schema(tool: Tool) -> dict:
    schema = tool.parameters.model_json_schema()
    return {
        "name": tool.name,
        "description": tool.description,
        "input_schema": schema,
    }


class AnthropicAgent(Agent):
    name = "anthropic-live-agent"
    role = "default"

    def __init__(self, model: str = "claude-3-haiku-20240307"):
        self.model = model
        self.client = Anthropic()

    def query(self, prompt, tools, env):
        anthropic_tools = [tool_to_anthropic_schema(t) for t in tools]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system="You are a helpful assistant with access to tools.",
            messages=[{"role": "user", "content": prompt}],
            tools=anthropic_tools,
        )

        trace = []
        text_content = ""
        for block in response.content:
            if block.type == "tool_use":
                trace.append(ToolCall(tool_name=block.name, args=block.input))
            elif block.type == "text":
                text_content += block.text

        return [{"role": "assistant", "content": text_content}], trace