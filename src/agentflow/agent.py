import asyncio
import json
from typing import Any

from .events import EventTracer
from .tools import Tool, ToolRegistry


class Agent:
    def __init__(
        self,
        name: str,
        model: Any,
        system_prompt: str = "",
        tools: ToolRegistry | dict[str, Tool] | None = None,
        tracer: EventTracer | None = None,
    ) -> None:
        self.name = name
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools or {}
        self.tracer = tracer

    def _get_tool(self, name: str) -> Tool:
        if isinstance(self.tools, ToolRegistry):
            return self.tools.get(name)

        if isinstance(self.tools, dict):
            tool = self.tools.get(name)

            if tool is None:
                raise KeyError(
                    f"Tool '{name}' is not registered."
                )

            return tool

        raise TypeError(
            "tools must be a ToolRegistry or dictionary."
        )

    def _tool_schemas(self) -> list[dict[str, Any]]:
        if isinstance(self.tools, ToolRegistry):
            return self.tools.schemas()

        if isinstance(self.tools, dict):
            return [
                tool.schema()
                for tool in self.tools.values()
            ]

        return []

    async def _execute_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> Any:
        tool = self._get_tool(name)

        if self.tracer:
            self.tracer.record(
                "tool_started",
                agent=self.name,
                tool=name,
                arguments=arguments,
            )

        try:
            result = await tool.execute(**arguments)

            if self.tracer:
                self.tracer.record(
                    "tool_completed",
                    agent=self.name,
                    tool=name,
                    result=result,
                )

            return result

        except Exception as exc:
            if self.tracer:
                self.tracer.record(
                    "tool_failed",
                    agent=self.name,
                    tool=name,
                    error=str(exc),
                )

            raise

    async def run(self, prompt: str) -> str:
        if self.tracer:
            self.tracer.record(
                "agent_started",
                agent=self.name,
                prompt=prompt,
            )

        try:
            messages: list[dict[str, str]] = []

            if self.system_prompt:
                messages.append(
                    {
                        "role": "system",
                        "content": self.system_prompt,
                    }
                )

            messages.append(
                {
                    "role": "user",
                    "content": prompt,
                }
            )

            while True:
                response = await self.model.generate(
                    messages=messages,
                    tools=self._tool_schemas(),
                )

                if self.tracer:
                    self.tracer.record(
                        "model_response",
                        agent=self.name,
                    )

                tool_calls = getattr(
                    response,
                    "tool_calls",
                    None,
                )

                if not tool_calls:
                    result = self._extract_text(response)

                    if self.tracer:
                        self.tracer.record(
                            "agent_completed",
                            agent=self.name,
                            result=result,
                        )

                    return result

                tool_results = await asyncio.gather(
                    *[
                        self._execute_tool(
                            call["name"]
                            if isinstance(call, dict)
                            else call.name,
                            call.get("arguments", {})
                            if isinstance(call, dict)
                            else call.arguments,
                        )
                        for call in tool_calls
                    ]
                )

                for call, result in zip(
                    tool_calls,
                    tool_results,
                ):
                    if isinstance(call, dict):
                        call_name = call["name"]
                        call_arguments = call.get(
                            "arguments",
                            {},
                        )
                    else:
                        call_name = call.name
                        call_arguments = call.arguments

                    messages.append(
                        {
                            "role": "assistant",
                            "content": json.dumps(
                                {
                                    "tool_call": {
                                        "name": call_name,
                                        "arguments": call_arguments,
                                    }
                                }
                            ),
                        }
                    )

                    messages.append(
                        {
                            "role": "tool",
                            "content": json.dumps(
                                {
                                    "name": call_name,
                                    "result": result,
                                }
                            ),
                        }
                    )

        except Exception as exc:
            if self.tracer:
                self.tracer.record(
                    "agent_failed",
                    agent=self.name,
                    error=str(exc),
                )

            raise

    @staticmethod
    def _extract_text(response: Any) -> str:
        if isinstance(response, str):
            return response

        if isinstance(response, dict):
            text = response.get("text")

            if text is not None:
                return str(text)

            content = response.get("content")

            if content is not None:
                return str(content)

        text = getattr(response, "text", None)

        if text is not None:
            return str(text)

        content = getattr(response, "content", None)

        if content is not None:
            return str(content)

        return str(response)
