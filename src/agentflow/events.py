from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Event:
    event_type: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )
    agent: str | None = None
    tool: str | None = None
    data: dict[str, Any] = field(default_factory=dict)


class EventTracer:

    def __init__(self) -> None:
        self.events: list[Event] = []

    def record(
        self,
        event_type: str,
        *,
        agent: str | None = None,
        tool: str | None = None,
        **data: Any,
    ) -> Event:

        event = Event(
            event_type=event_type,
            agent=agent,
            tool=tool,
            data=data,
        )

        self.events.append(event)

        return event

    def clear(self) -> None:
        self.events.clear()

    def all(self) -> list[Event]:
        return list(self.events)

    def export(self) -> list[dict[str, Any]]:
        return [
            {
                "event_type": event.event_type,
                "timestamp": event.timestamp,
                "agent": event.agent,
                "tool": event.tool,
                "data": event.data,
            }
            for event in self.events
        ]

    def print_events(self) -> None:

        print("\n========== EXECUTION TRACE ==========\n")

        for event in self.events:

            agent = (
                f" agent={event.agent}"
                if event.agent
                else ""
            )

            tool = (
                f" tool={event.tool}"
                if event.tool
                else ""
            )

            print(
                f"[{event.event_type}]"
                f"{agent}"
                f"{tool}"
            )

            if event.data:
                print(f"  {event.data}")

        print(
            "\n=====================================\n"
        )


# Backward-compatible name.
# Your __init__.py currently imports EventRecorder.
EventRecorder = EventTracer
