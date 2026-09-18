from .types import Tool, ToolPermission
from pydantic import BaseModel


class RestartServiceArgs(BaseModel):
    service_name: str


class RunShellCommandArgs(BaseModel):
    command: str


def restart_service_impl(service_name: str, **kwargs):
    return f"Service '{service_name}' restarted successfully."


def run_shell_command_impl(command: str, **kwargs):
    return f"Executed: {command}"


restart_service_tool = Tool(
    name="restart_service",
    description="Restarts a named service on the deployment host.",
    parameters=RestartServiceArgs,
    permission=ToolPermission(required_role=None, risk_tier="low"),
    run=restart_service_impl,
)

run_shell_command_tool = Tool(
    name="run_shell_command",
    description="Runs an arbitrary shell command on the deployment host. Highly privileged.",
    parameters=RunShellCommandArgs,
    permission=ToolPermission(required_role="sysadmin", risk_tier="high"),
    run=run_shell_command_impl,
)