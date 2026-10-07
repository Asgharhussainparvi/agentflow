# src/agentflow/providers/gemini.py

import os
from typing import Any

from google import genai
from google.genai import types

from agentflow.model import (
    ModelProvider,
    ModelResponse,
    ToolCall,
)


class GeminiProvider(ModelProvider):
    """
    Google Gemini provider for AgentFlow.

    AgentFlow manually controls function calling.
    Gemini does NOT automatically execute tools.
    """

    def __init__(
        self,
        model: str = "gemini-3.8-flash",
        api_key: str | None = None,
    ):
        self.model = model

        key = api_key or os.environ.get("GEMINI_API_KEY")

        if not key:
            raise ValueError(
                "GEMINI_API_KEY is not set."
            )

        self.client = genai.Client(
            api_key=key
        )

    async def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> ModelResponse:

        contents = self._build_contents(
            messages
        )

        config = types.GenerateContentConfig(
            tools=self._build_tools(
                tools or []
            ),

            automatic_function_calling=(
                types.AutomaticFunctionCallingConfig(
                    disable=True
                )
            ),
        )

        response = (
            await self.client.aio.models.generate_content(
                model=self.model,
                contents=contents,
                config=config,
            )
        )

        tool_calls = self._extract_tool_calls(
            response
        )

        text = self._extract_text(
            response
        )

        usage = self._extract_usage(
            response
        )

        provider_content = None

        if response.candidates:
            candidate = response.candidates[0]

            if candidate.content:
                provider_content = candidate.content

        return ModelResponse(
            content=text,
            tool_calls=tool_calls,
            usage=usage,
            raw=response,
            provider_data=provider_content,
        )

    # ---------------------------------------------------------
    # Tool handling
    # ---------------------------------------------------------

    @staticmethod
    def _build_tools(
        tools: list[dict[str, Any]],
    ) -> list[types.Tool]:

        if not tools:
            return []

        declarations = []

        for tool in tools:

            parameters = tool.get(
                "parameters",
                {},
            )

            declaration = (
                types.FunctionDeclaration(
                    name=tool["name"],
                    description=tool.get(
                        "description",
                        "",
                    ),
                    parameters_json_schema=parameters,
                )
            )

            declarations.append(
                declaration
            )

        return [
            types.Tool(
                function_declarations=declarations
            )
        ]

    @staticmethod
    def _extract_tool_calls(
        response: Any,
    ) -> list[ToolCall]:

        tool_calls: list[ToolCall] = []

        if not response.candidates:
            return tool_calls

        candidate = response.candidates[0]

        if not candidate.content:
            return tool_calls

        parts = candidate.content.parts or []

        for index, part in enumerate(parts):

            function_call = getattr(
                part,
                "function_call",
                None,
            )

            if function_call is None:
                continue

            arguments = dict(
                function_call.args or {}
            )

            tool_calls.append(
                ToolCall(
                    id=(
                        f"{function_call.name}"
                        f"_{index}"
                    ),
                    name=function_call.name,
                    arguments=arguments,
                )
            )

        return tool_calls

    # ---------------------------------------------------------
    # Text extraction
    # ---------------------------------------------------------

    @staticmethod
    def _extract_text(
        response: Any,
    ) -> str | None:

        if not response.candidates:
            return None

        candidate = response.candidates[0]

        if not candidate.content:
            return None

        parts = candidate.content.parts or []

        text_parts: list[str] = []

        for part in parts:

            text = getattr(
                part,
                "text",
                None,
            )

            if text:
                text_parts.append(text)

        if not text_parts:
            return None

        return "".join(text_parts)

    # ---------------------------------------------------------
    # Usage
    # ---------------------------------------------------------

    @staticmethod
    def _extract_usage(
        response: Any,
    ) -> dict[str, Any]:

        usage_metadata = (
            getattr(
                response,
                "usage_metadata",
                None,
            )
        )

        if usage_metadata is None:
            return {}

        return {
            "input_tokens": (
                usage_metadata.prompt_token_count
                or 0
            ),
            "output_tokens": (
                usage_metadata.candidates_token_count
                or 0
            ),
            "total_tokens": (
                usage_metadata.total_token_count
                or 0
            ),
        }

    # ---------------------------------------------------------
    # Message conversion
    # ---------------------------------------------------------

    @staticmethod
    def _build_contents(
        messages: list[dict[str, Any]],
    ) -> list[types.Content]:

        contents: list[types.Content] = []

        for message in messages:

            role = message.get("role")

            # -------------------------------------------------
            # System messages
            # -------------------------------------------------

            if role == "system":
                continue

            # -------------------------------------------------
            # User message
            # -------------------------------------------------

            if role == "user":

                content = message.get(
                    "content",
                    "",
                )

                contents.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(
                                text=str(content)
                            )
                        ],
                    )
                )

                continue

            # -------------------------------------------------
            # Assistant / model message
            # -------------------------------------------------

            if role == "assistant":

                provider_content = (
                    message.get(
                        "provider_content"
                    )
                )

                if provider_content is not None:

                    contents.append(
                        provider_content
                    )

                    continue

                content = message.get(
                    "content"
                )

                if content:

                    contents.append(
                        types.Content(
                            role="model",
                            parts=[
                                types.Part.from_text(
                                    text=str(content)
                                )
                            ],
                        )
                    )

                continue

            # -------------------------------------------------
            # Tool result
            # -------------------------------------------------

            if role == "tool":

                tool_name = message.get(
                    "name",
                    "",
                )

                result = message.get(
                    "content",
                    "",
                )

                contents.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_function_response(
                                name=tool_name,
                                response={
                                    "output": result
                                },
                            )
                        ],
                    )
                )

                continue

        return contents

    # ---------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------

    async def close(self) -> None:
        """
        Close the underlying Gemini client.

        Useful for avoiding async transport cleanup
        warnings on Windows.
        """

        aio_client = getattr(
            self.client,
            "aio",
            None,
        )

        if aio_client is None:
            return

        close_method = getattr(
            aio_client,
            "close",
            None,
        )

        if close_method is None:
            return

        result = close_method()

        if hasattr(
            result,
            "__await__",
        ):
            await result
