import os

from agentflow import Agent, Workflow
from agentflow.providers import GeminiProvider


model = GeminiProvider(
    model="gemini-3.8-flash",
    api_key=os.environ["GEMINI_API_KEY"],
)

agent = Agent(
    name="researcher",
    instructions="You are a helpful AI research assistant.",
    model=model,
)

workflow = Workflow(
    agents=[agent],
    timeout=60,
    retries=2,
)

result = workflow.run(
    "Explain multi-agent AI systems in simple words."
)

print("Answer:")
print(result.output)
