import inspect
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Tool:
    name: str
    function: Callable[..., Any]
    description: str = ""

    def schema(self) -> dict[str, Any]:
        signature = inspect.signature(self.function)

        properties: dict[str, Any] = {}
        required: list[str] = []

        for name, parameter in signature.parameters.items():
            properties[name] = {
                "type": "string",
            }

            if parameter.default is inspect.Parameter.empty:
                required.append(name)

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    async def execute(
        self,
        **kwargs: Any,
    ) -> Any:
        try:
            result = self.function(**kwargs)

            if inspect.isawaitable(result):
                return await result

            return result

        except Exception as exc:
            raise RuntimeError(
                f"Tool '{self.name}' failed: {exc}"
            ) from exc


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> Tool:
        self._tools[tool.name] = tool
        return tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(
                f"Tool '{name}' is not registered."
            )

        return self._tools[name]

    def remove(self, name: str) -> None:
        self._tools.pop(name, None)

    def clear(self) -> None:
        self._tools.clear()

    def all(self) -> dict[str, Tool]:
        return dict(self._tools)

    def schemas(self) -> list[dict[str, Any]]:
        return [
            registered_tool.schema()
            for registered_tool in self._tools.values()
        ]

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __len__(self) -> int:
        return len(self._tools)


# Global tool registry
tools = ToolRegistry()


def tool(
    function: Callable[..., Any] | None = None,
    *,
    name: str | None = None,
    description: str = "",
):
    def decorator(func: Callable[..., Any]) -> Tool:
        registered_tool = Tool(
            name=name or func.__name__,
            function=func,
            description=description or (
                func.__doc__ or ""
            ).strip(),
        )

        tools.register(registered_tool)

        return registered_tool

    if function is not None:
        return decorator(function)

    return decorator
