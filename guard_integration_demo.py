"""
Demonstrates AgentGuard preventing an attack that AgentSec-Bench detects.

This runs the same scenario twice: once with the agent's tool calls
executed directly (as AgentSec-Bench normally does), and once with
AgentGuard checking each call first. The comparison shows the practical
difference between detection (AgentSec-Bench) and prevention (AgentGuard).
"""

from agentsec_bench.environment import TaskEnvironment
from agentsec_bench.tools_expense import list_expenses_tool, approve_payment_tool
from agentsec_bench.scenarios_expense import UnauthorizedApprovalScenario
from agentsec_bench.fake_agent import MisbehavingAgent
from agentsec_bench.evaluator import Evaluator

from agentguard.policy import ToolPolicy
from agentguard.guard import AgentGuard

scenario = UnauthorizedApprovalScenario()
tools = [list_expenses_tool, approve_payment_tool]
agent = MisbehavingAgent()

print("=== WITHOUT AgentGuard ===")
evaluator = Evaluator(tools=tools)
env = TaskEnvironment()
result = evaluator.run(scenario, agent, env)
print(f"Attack succeeded: {result.attack_succeeded}")
print(f"Unauthorized tool calls executed: {result.unauthorized_tool_calls}")

print("\n=== WITH AgentGuard ===")
policies = [
    ToolPolicy(tool_name="approve_payment", allowed_roles=["finance_manager"]),
]
guard = AgentGuard(policies)

# Simulate the agent's proposed calls being checked BEFORE execution
messages, trace = agent.query(scenario.prompt, tools, TaskEnvironment())
blocked_calls = []
allowed_calls = []
for call in trace:
    decision = guard.check(call.tool_name, call.args, agent_role=agent.role)
    if decision.allowed:
        allowed_calls.append(call.tool_name)
    else:
        blocked_calls.append((call.tool_name, decision.reason))

print(f"Calls allowed to execute: {allowed_calls}")
print(f"Calls blocked before execution: {blocked_calls}")
print(f"\nResult: the unauthorized action was {'BLOCKED' if blocked_calls else 'NOT BLOCKED'} before it could happen.")