import os

from agentflow import Agent, Workflow, tool
from agentflow.providers import GeminiProvider


@tool
def calculator(a: int, b: int) -> int:
    """Add two integers together."""
    return a + b


model = GeminiProvider(
    model="gemini-3.8-flash",
    api_key=os.environ["GEMINI_API_KEY"],
)

agent = Agent(
    name="calculator",
    instructions=(
        "You are a mathematical assistant. "
        "Always use the calculator tool for arithmetic."
    ),
    model=model,
    tools=[calculator],
    max_tool_calls=5,
)

workflow = Workflow(
    agents=[agent],
    max_steps=5,
    timeout=60,
    retries=2,
)

result = workflow.run(
    "What is 125 + 375?"
)

print()
print("========== RESULT ==========")
print(result.output)

print()
print("========== EVENTS ==========")

for event in workflow.events.events:
    print(
        event.type,
        event.data,
    )
