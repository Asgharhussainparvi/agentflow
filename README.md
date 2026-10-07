AgentFlow

A lightweight Python runtime for reliable and observable AI agent workflows.

AgentFlow provides a small, provider-agnostic runtime for building AI agents that can execute models, call tools, retry failed operations, enforce workflow timeouts, and expose execution traces.

Features

🤖 Agent-based workflow execution

🔌 Provider-agnostic model interface

🛠️ Tool calling

⚡ Parallel tool execution

📦 Tool registry

🔁 Automatic retry support

⏱️ Workflow timeouts

📊 Execution tracing with EventTracer

🧪 Mock model support for testing

♊ Gemini provider support

🐍 Python 3.10+ support

📦 Standard Python wheel and source distribution

Installation

Install the latest published package:

pip install agentflow


For Gemini support:

pip install "agentflow[gemini]"

Quick Start

A model provider implements the ModelProvider interface.

from agentflow import Agent, Workflow, ModelResponse


class MyModel:
    async def generate(self, messages, tools=None):
        return ModelResponse(
            content="Hello from AgentFlow!"
        )


agent = Agent(
    name="assistant",
    model=MyModel(),
)

workflow = Workflow(
    agents={
        "assistant": agent,
    }
)

result = workflow.run(
    "assistant",
    "Say hello",
)

print(result)


Output:

Hello from AgentFlow!

Model Provider

AgentFlow separates the agent runtime from the model provider.

A provider only needs to implement an asynchronous generate() method.

from agentflow import ModelResponse


class MyModel:
    async def generate(self, messages, tools=None):
        return ModelResponse(
            content="Model response"
        )


This makes it possible to integrate different LLM providers without changing the workflow runtime.

Tools

Tools can be registered using ToolRegistry.

from agentflow import Tool, ToolRegistry


def add(a, b):
    return int(a) + int(b)


registry = ToolRegistry()

registry.register(
    Tool(
        name="add",
        function=add,
        description="Add two numbers",
    )
)


The registry can then be supplied to an agent:

agent = Agent(
    name="calculator",
    model=model,
    tools=registry,
)


Tools may also be asynchronous:

async def get_data(query):
    return f"Data for: {query}"


AgentFlow supports both synchronous and asynchronous tool functions.

Tool Decorator

A global tool registry is also available through the tool decorator.

from agentflow import tool


@tool
def greet(name):
    return f"Hello, {name}!"


You can provide a custom name and description:

@tool(
    name="calculator",
    description="Perform a calculation",
)
def calculate(expression):
    return eval(expression)

Parallel Tool Execution

When a model returns multiple tool calls, AgentFlow executes them concurrently.

Conceptually:

Model
  │
  ├── Tool A ──┐
  ├── Tool B ──┼──> Results
  └── Tool C ──┘
       │
       ▼
     Model


This allows independent tool calls to execute without unnecessarily waiting for each other.

Reliability

AgentFlow includes asynchronous retry support with exponential backoff.

from agentflow.reliability import retry_async


result = await retry_async(
    operation,
    retries=3,
    base_delay=0.5,
)


The workflow runtime can use retries around agent execution so temporary provider failures do not immediately terminate the workflow.

Workflow Timeout

Workflows can be protected with a timeout:

workflow = Workflow(
    agents={
        "assistant": agent,
    },
    timeout=30,
)


If the workflow exceeds the configured timeout, a WorkflowTimeoutError is raised.

Execution Tracing

Use EventTracer to observe execution.

from agentflow import EventTracer


tracer = EventTracer()

agent = Agent(
    name="assistant",
    model=model,
    tracer=tracer,
)

workflow = Workflow(
    agents={
        "assistant": agent,
    },
    tracer=tracer,
)


After execution:

workflow.print_trace()


You can also retrieve structured trace data:

trace = workflow.get_trace()

for event in trace:
    print(event)


Events can include:

workflow_started

workflow_completed

workflow_failed

workflow_agent_started

workflow_agent_completed

workflow_agent_failed

agent_started

agent_completed

agent_failed

model_response

tool_started

tool_completed

tool_failed

Gemini

AgentFlow includes a Gemini provider.

Install the optional dependency:

pip install "agentflow[gemini]"


Set your API key in PowerShell:

$env:GEMINI_API_KEY="YOUR_API_KEY"


Then use the Gemini provider from the package:

from agentflow import Agent, Workflow
from agentflow.providers.gemini import GeminiProvider


model = GeminiProvider(
    model="gemini-3.8-flash",
)

agent = Agent(
    name="assistant",
    model=model,
)

workflow = Workflow(
    agents={
        "assistant": agent,
    },
)

result = workflow.run(
    "assistant",
    "Explain what AgentFlow does.",
)

print(result)


Never commit API keys or other secrets to Git.

Testing

Clone the repository:

git clone https://github.com/Asgharhussainparvi/agentflow.git
cd agentflow


Create a virtual environment:

python -m venv .venv
.venv\Scripts\activate


Install development dependencies:

python -m pip install -e ".[dev]"


Run the test suite:

pytest -q


The project uses pytest and pytest-asyncio for testing.

Building the Package

Install the build tool:

python -m pip install build


Build the wheel and source distribution:

python -m build


The generated packages will appear in:

dist/


Example:

dist/
├── agentflow-0.1.0-py3-none-any.whl
└── agentflow-0.1.0.tar.gz

Project Structure
agentflow/
│
├── examples/
│   ├── basic.py
│   ├── gemini.py
│   ├── gemini_tool.py
│   ├── model_agent.py
│   ├── parallel_tool.py
│   ├── test_events.py
│   ├── test_integration.py
│   ├── tool.py
│   └── tool_calling.py
│
├── src/
│   └── agentflow/
│       ├── agent.py
│       ├── context.py
│       ├── events.py
│       ├── exceptions.py
│       ├── model.py
│       ├── reliability.py
│       ├── result.py
│       ├── tools.py
│       ├── workflow.py
│       │
│       └── providers/
│           ├── gemini.py
│           └── mock.py
│
├── tests/
│   └── test_core.py
│
├── pyproject.toml
└── README.md

Design Goals

AgentFlow is intentionally lightweight.

The main goals are:

Keep the runtime small and easy to understand.

Keep model providers separate from workflow logic.

Make tool execution composable.

Provide reliable retry and timeout behavior.

Make execution observable through structured events.

Keep testing possible without requiring a real LLM provider.

Current Status

AgentFlow is currently in the Alpha stage.

Version:

0.1.0


The API may evolve as the project develops.

Roadmap

Planned improvements include:

More model providers

Improved structured tool schemas

Better workflow composition

Streaming model responses

More comprehensive test coverage

Better documentation

CI/CD integration

Performance improvements

More advanced agent orchestration

Contributing

Contributions, bug reports, ideas, and improvements are welcome.

Before submitting changes:

pytest -q
python -m build


Please keep changes focused and avoid introducing unnecessary dependencies.

License

AgentFlow is released under the MIT License.

See the LICENSE file for the full license text.

Author

Asghar Hussain

GitHub:

https://github.com/Asgharhussainparvi

Repository

https://github.com/Asgharhussainparvi/agentflow