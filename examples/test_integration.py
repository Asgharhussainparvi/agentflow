import asyncio

from agentflow import (
    Agent,
    EventTracer,
    Tool,
    Workflow,
)


# --------------------------------------------------
# Fake model
# --------------------------------------------------

class FakeModel:

    async def generate(
        self,
        messages,
        tools=None,
    ):
        """
        Local fake model.

        No Gemini API is used.
        """

        user_message = messages[-1]["content"]

        if tools:
            return {
                "tool_calls": [
                    {
                        "name": "researcher_a",
                        "arguments": {
                            "topic": user_message,
                        },
                    },
                    {
                        "name": "researcher_b",
                        "arguments": {
                            "topic": user_message,
                        },
                    },
                ]
            }

        return {
            "text": "Local AgentFlow test completed."
        }


# --------------------------------------------------
# Tool functions
# --------------------------------------------------

async def researcher_a(topic: str) -> str:
    """
    Simulates research source A.
    """

    await asyncio.sleep(1)

    return f"Researcher A found information about: {topic}"


async def researcher_b(topic: str) -> str:
    """
    Simulates research source B.
    """

    await asyncio.sleep(1)

    return f"Researcher B found information about: {topic}"


# --------------------------------------------------
# Main
# --------------------------------------------------

async def main():

    print()
    print("========================================")
    print("       AgentFlow Integration Test")
    print("========================================")
    print()

    # ----------------------------------------------
    # Create tools
    # ----------------------------------------------

    tools = {
        "researcher_a": Tool(
            name="researcher_a",
            function=researcher_a,
            description="Research using source A.",
        ),

        "researcher_b": Tool(
            name="researcher_b",
            function=researcher_b,
            description="Research using source B.",
        ),
    }

    print(
        f"Registered tools: {len(tools)}"
    )

    # ----------------------------------------------
    # Event tracer
    # ----------------------------------------------

    tracer = EventTracer()

    # ----------------------------------------------
    # Fake model
    # ----------------------------------------------

    model = FakeModel()

    # ----------------------------------------------
    # Agent
    # ----------------------------------------------

    agent = Agent(
        name="research_agent",
        model=model,
        system_prompt="You are a research agent.",
        tools=tools,
        tracer=tracer,
    )

    # ----------------------------------------------
    # Workflow
    # ----------------------------------------------

    workflow = Workflow(
        agents={
            "research_agent": agent,
        },
        tracer=tracer,
    )

    # ----------------------------------------------
    # Execute
    # ----------------------------------------------

    print()
    print("Running workflow...")
    print()

    result = await workflow.run_async(
        agent_name="research_agent",
        prompt="multi-agent AI systems",
    )

    # ----------------------------------------------
    # Result
    # ----------------------------------------------

    print()
    print("========== FINAL RESULT ==========")
    print()

    print(result)

    # ----------------------------------------------
    # Trace
    # ----------------------------------------------

    print()
    print("========== EXECUTION TRACE ==========")
    print()

    workflow.print_trace()

    # ----------------------------------------------
    # Validation
    # ----------------------------------------------

    print()
    print("========== VALIDATION ==========")
    print()

    events = tracer.all()

    event_types = [
        event.event_type
        for event in events
    ]

    required_events = [
        "workflow_started",
        "workflow_agent_started",
        "agent_started",
        "tool_started",
        "tool_completed",
        "agent_completed",
        "workflow_agent_completed",
        "workflow_completed",
    ]

    passed = True

    for event_type in required_events:

        if event_type in event_types:
            print(f"[PASS] {event_type}")
        else:
            print(f"[FAIL] {event_type}")
            passed = False

    tool_completed_count = event_types.count(
        "tool_completed"
    )

    print()

    if tool_completed_count == 2:
        print("[PASS] Both tools completed.")
    else:
        print(
            "[FAIL] Expected 2 completed tools, "
            f"got {tool_completed_count}."
        )
        passed = False

    print()

    if passed:
        print("========================================")
        print("       INTEGRATION TEST PASSED")
        print("========================================")
    else:
        print("========================================")
        print("       INTEGRATION TEST FAILED")
        print("========================================")


if __name__ == "__main__":
    asyncio.run(main())
