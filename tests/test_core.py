import asyncio

import pytest

from agentflow import Agent, ModelResponse, Workflow
from agentflow.exceptions import WorkflowTimeoutError


class FakeModel:
    def __init__(self, responses=None, delay=0):
        self.responses = list(responses or ["success"])
        self.delay = delay
        self.calls = 0

    async def generate(self, messages, tools=None):
        self.calls += 1

        if self.delay:
            await asyncio.sleep(self.delay)

        response = self.responses[
            min(self.calls - 1, len(self.responses) - 1)
        ]

        return ModelResponse(content=response)


def test_basic_workflow():
    model = FakeModel(
        responses=["Processed: Hello"]
    )

    agent = Agent(
        name="processor",
        model=model,
    )

    workflow = Workflow(
        agents={
            "processor": agent,
        }
    )

    result = workflow.run(
        "processor",
        "Hello",
    )

    assert result == "Processed: Hello"


def test_multiple_agents():
    first_model = FakeModel(
        responses=["first result"]
    )

    second_model = FakeModel(
        responses=["second result"]
    )

    workflow = Workflow(
        agents={
            "first": Agent(
                name="first",
                model=first_model,
            ),
            "second": Agent(
                name="second",
                model=second_model,
            ),
        }
    )

    first = workflow.run(
        "first",
        "start",
    )

    second = workflow.run(
        "second",
        first,
    )

    assert first == "first result"
    assert second == "second result"


def test_retry():
    class UnstableModel:
        def __init__(self):
            self.calls = 0

        async def generate(self, messages, tools=None):
            self.calls += 1

            if self.calls < 3:
                raise RuntimeError("Temporary failure")

            return ModelResponse(
                content="success"
            )

    model = UnstableModel()

    agent = Agent(
        name="unstable",
        model=model,
    )

    workflow = Workflow(
        agents={
            "unstable": agent,
        },
        max_retries=2,
    )

    result = workflow.run(
        "unstable",
        "test",
    )

    assert result == "success"
    assert model.calls == 3


@pytest.mark.asyncio
async def test_timeout():
    model = FakeModel(
        responses=["done"],
        delay=1,
    )

    agent = Agent(
        name="slow",
        model=model,
    )

    workflow = Workflow(
        agents={
            "slow": agent,
        },
        timeout=0.01,
    )

    with pytest.raises(WorkflowTimeoutError):
        await workflow.run_async(
            "slow",
            "test",
        )


def test_events():
    from agentflow import EventTracer

    tracer = EventTracer()

    model = FakeModel(
        responses=["done"]
    )

    agent = Agent(
        name="test-agent",
        model=model,
        tracer=tracer,
    )

    workflow = Workflow(
        agents={
            "test-agent": agent,
        },
        tracer=tracer,
    )

    result = workflow.run(
        "test-agent",
        "hello",
    )

    assert result == "done"

    event_types = [
        event["event_type"]
        for event in tracer.export()
    ]

    assert "workflow_started" in event_types
    assert "workflow_agent_started" in event_types
    assert "agent_started" in event_types
    assert "agent_completed" in event_types
    assert "workflow_agent_completed" in event_types
    assert "workflow_completed" in event_types
