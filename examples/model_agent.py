from agentflow import Agent, Workflow
from agentflow.providers import MockProvider


model = MockProvider(
    response="AgentFlow successfully executed the task."
)

agent = Agent(
    name="researcher",
    instructions="You are a research assistant.",
    model=model,
)

workflow = Workflow(
    agents=[agent],
    max_steps=5,
)

result = workflow.run(
    "Explain multi-agent AI systems."
)

print("Answer:")
print(result.output)

print()
print("Model calls:", model.calls)
