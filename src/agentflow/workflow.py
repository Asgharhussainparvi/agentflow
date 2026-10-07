import asyncio
from typing import Any

from .agent import Agent
from .events import EventTracer
from .exceptions import WorkflowTimeoutError
from .reliability import retry_async


class Workflow:
    def __init__(
        self,
        agents: dict[str, Agent],
        tracer: EventTracer | None = None,
        timeout: float = 300.0,
        max_retries: int = 3,
    ) -> None:
        self.agents = agents
        self.tracer = tracer
        self.timeout = timeout
        self.max_retries = max_retries

    async def _run_agent(
        self,
        agent_name: str,
        prompt: str,
    ) -> str:
        if agent_name not in self.agents:
            raise KeyError(
                f"Agent '{agent_name}' is not registered."
            )

        agent = self.agents[agent_name]

        if self.tracer:
            self.tracer.record(
                "workflow_agent_started",
                agent=agent_name,
                prompt=prompt,
            )

        async def operation() -> str:
            return await agent.run(prompt)

        try:
            result = await retry_async(
                operation,
                retries=self.max_retries,
            )

            if self.tracer:
                self.tracer.record(
                    "workflow_agent_completed",
                    agent=agent_name,
                    result=result,
                )

            return result

        except Exception as exc:
            if self.tracer:
                self.tracer.record(
                    "workflow_agent_failed",
                    agent=agent_name,
                    error=str(exc),
                )

            raise

    async def _run(
        self,
        agent_name: str,
        prompt: str,
    ) -> str:
        if self.tracer:
            self.tracer.record(
                "workflow_started",
                agent=agent_name,
                prompt=prompt,
            )

        try:
            output = await self._run_agent(
                agent_name,
                prompt,
            )

            if self.tracer:
                self.tracer.record(
                    "workflow_completed",
                    agent=agent_name,
                    result=output,
                )

            return output

        except Exception as exc:
            if self.tracer:
                self.tracer.record(
                    "workflow_failed",
                    agent=agent_name,
                    error=str(exc),
                )

            raise

    async def run_async(
        self,
        agent_name: str,
        prompt: str,
    ) -> str:
        try:
            return await asyncio.wait_for(
                self._run(
                    agent_name,
                    prompt,
                ),
                timeout=self.timeout,
            )

        except asyncio.TimeoutError as exc:
            if self.tracer:
                self.tracer.record(
                    "workflow_timeout",
                    agent=agent_name,
                    timeout=self.timeout,
                )

            raise WorkflowTimeoutError(
                f"Workflow timed out after "
                f"{self.timeout} seconds."
            ) from exc

    def run(
        self,
        agent_name: str,
        prompt: str,
    ) -> str:
        return asyncio.run(
            self.run_async(
                agent_name,
                prompt,
            )
        )

    def get_trace(self) -> list[dict[str, Any]]:
        if self.tracer is None:
            return []

        return self.tracer.export()

    def print_trace(self) -> None:
        if self.tracer is None:
            print(
                "No EventTracer attached to this workflow."
            )
            return

        self.tracer.print_events()
