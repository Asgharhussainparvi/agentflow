class AgentFlowError(Exception):
    """Base exception for AgentFlow."""


class ToolExecutionError(AgentFlowError):
    """Raised when a tool fails during execution."""


class WorkflowError(AgentFlowError):
    """Raised when workflow execution fails."""


class WorkflowTimeoutError(WorkflowError):
    """Raised when a workflow exceeds its timeout."""
