from agentflow import EventTracer


tracer = EventTracer()


tracer.record(
    "workflow_started",
    agent="manager",
    input="Research multi-agent AI",
)

tracer.record(
    "agent_started",
    agent="researcher_a",
)

tracer.record(
    "tool_started",
    agent="researcher_a",
    tool="web_search",
    query="multi-agent AI",
)

tracer.record(
    "tool_completed",
    agent="researcher_a",
    tool="web_search",
    result_count=5,
)

tracer.record(
    "agent_completed",
    agent="researcher_a",
)

tracer.record(
    "workflow_completed",
    agent="manager",
)


tracer.print_events()
