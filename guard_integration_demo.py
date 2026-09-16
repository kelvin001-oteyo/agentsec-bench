"""
Demonstrates AgentGuard preventing attacks that AgentSec-Bench detects,
across two different threat categories: unauthorized tool invocation
(role-based) and prompt injection (destination-based).
"""

from agentsec_bench.environment import TaskEnvironment
from agentsec_bench.environment_inbox import InboxEnvironment
from agentsec_bench.tools_expense import list_expenses_tool, approve_payment_tool
from agentsec_bench.tools_inbox import summarize_inbox_tool, forward_email_tool
from agentsec_bench.scenarios_expense import UnauthorizedApprovalScenario
from agentsec_bench.scenarios_injection import InboxInjectionScenario
from agentsec_bench.fake_agent import MisbehavingAgent
from agentsec_bench.inbox_agents import InjectionSusceptibleAgent
from agentsec_bench.evaluator import Evaluator

from agentguard.policy import ToolPolicy
from agentguard.guard import AgentGuard


def demo(label, scenario, tools, agent, env_factory, guard):
    print(f"=== {label} ===")

    print("-- Without AgentGuard --")
    evaluator = Evaluator(tools=tools)
    env = env_factory()
    result = evaluator.run(scenario, agent, env)
    print(f"Attack succeeded: {result.attack_succeeded}")
    print(f"Role violations: {result.unauthorized_tool_calls}")
    print(f"Suspicious destinations: {result.suspicious_destinations}")

    print("-- With AgentGuard --")
    messages, trace = agent.query(scenario.prompt, tools, env_factory())
    blocked, allowed = [], []
    for call in trace:
        decision = guard.check(call.tool_name, call.args, agent_role=agent.role)
        (allowed if decision.allowed else blocked).append((call.tool_name, decision.reason))
    print(f"Allowed: {[c for c, _ in allowed]}")
    print(f"Blocked: {blocked}")
    print(f"Result: {'BLOCKED' if blocked else 'NOT BLOCKED'} before execution.\n")


# Scenario 1: unauthorized tool invocation (role-based)
guard1 = AgentGuard([ToolPolicy(tool_name="approve_payment", allowed_roles=["finance_manager"])])
demo(
    "UTI-001: Unauthorized Payment Approval",
    UnauthorizedApprovalScenario(),
    [list_expenses_tool, approve_payment_tool],
    MisbehavingAgent(),
    TaskEnvironment,
    guard1,
)

# Scenario 2: prompt injection (destination-based)
guard2 = AgentGuard([ToolPolicy(tool_name="forward_email", allowed_destinations=[])])
demo(
    "PI-001: Prompt Injection via Hidden Email Instruction",
    InboxInjectionScenario(),
    [summarize_inbox_tool, forward_email_tool],
    InjectionSusceptibleAgent(),
    InboxEnvironment,
    guard2,
)