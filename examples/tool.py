from agentflow import Agent, Workflow, tool
from agentflow.providers import MockProvider


@tool
def calculator(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


model = MockProvider(
    response="The calculation is complete."
)

agent = Agent(
    name="calculator-agent",
    model=model,
    tools=[calculator],
)

workflow = Workflow(
    agents=[agent],
)

result = workflow.run(
    "Calculate 10 + 20"
)

print(result.output)
