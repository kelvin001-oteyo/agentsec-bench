from agentsec_bench.environment import TaskEnvironment
from agentsec_bench.tools_expense import list_expenses_tool, approve_payment_tool
from agentsec_bench.tools_refund import lookup_order_tool, issue_refund_tool
from agentsec_bench.scenarios_expense import UnauthorizedApprovalScenario
from agentsec_bench.scenarios_ambiguous import AmbiguousRefundScenario
from agentsec_bench.fake_agent import MisbehavingAgent
from agentsec_bench.good_agent import WellBehavedAgent
from agentsec_bench.refund_agents import OverreachingSupportAgent, CautiousSupportAgent
from agentsec_bench.evaluator import Evaluator

# Each entry: (scenario, tools for that scenario, agents that make sense for it)
TEST_MATRIX = [
    (
        UnauthorizedApprovalScenario(),
        [list_expenses_tool, approve_payment_tool],
        [MisbehavingAgent(), WellBehavedAgent()],
    ),
    (
        AmbiguousRefundScenario(),
        [lookup_order_tool, issue_refund_tool],
        [OverreachingSupportAgent(), CautiousSupportAgent()],
    ),
]

results_summary = []

for scenario, tools, agents in TEST_MATRIX:
    evaluator = Evaluator(tools=tools)
    for agent in agents:
        env = TaskEnvironment()
        result = evaluator.run(scenario, agent, env)
        results_summary.append({
            "scenario": scenario.id,
            "agent": agent.name,
            "task_completed": result.task_completed,
            "attack_succeeded": result.attack_succeeded,
            "unauthorized_tool_calls": result.unauthorized_tool_calls,
        })

print(f"{'Scenario':<10} {'Agent':<28} {'Completed':<10} {'Attack':<8} Unauthorized")
print("-" * 85)
for r in results_summary:
    print(f"{r['scenario']:<10} {r['agent']:<28} {str(r['task_completed']):<10} "
          f"{str(r['attack_succeeded']):<8} {r['unauthorized_tool_calls']}")