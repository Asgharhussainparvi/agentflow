from agentflow import Agent, Workflow


def researcher(task, context):
    return f"Research completed for: {task}"


agent = Agent(
    name="researcher",
    handler=researcher,
)

workflow = Workflow(
    agents=[agent],
    retries=2,
    timeout=30,
)

result = workflow.run(
    "Research reliable multi-agent AI systems"
)

print(result.output)
print()

for event in workflow.events.events:
    print(
        event.timestamp.isoformat(),
        event.type,
        event.data,
    )
