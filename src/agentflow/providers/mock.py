from agentflow.model import (
    ModelProvider,
    ModelResponse,
    ToolCall,
)


class MockProvider(ModelProvider):

    def __init__(self):
        self.calls = 0

    async def generate(
        self,
        messages,
        tools=None,
    ) -> ModelResponse:

        self.calls += 1

        # First call: request calculator
        if self.calls == 1:
            return ModelResponse(
                tool_calls=[
                    ToolCall(
                        id="call_1",
                        name="calculator",
                        arguments={
                            "a": 10,
                            "b": 20,
                        },
                    )
                ]
            )

        # Second call: final answer
        return ModelResponse(
            content="The answer is 30."
        )
