import json
from datetime import datetime, timezone

from agentsec_bench.environment import TaskEnvironment
from agentsec_bench.environment_inbox import InboxEnvironment
from agentsec_bench.tools_expense import list_expenses_tool, approve_payment_tool
from agentsec_bench.tools_refund import lookup_order_tool, issue_refund_tool
from agentsec_bench.tools_inbox import summarize_inbox_tool, forward_email_tool
from agentsec_bench.scenarios_expense import UnauthorizedApprovalScenario
from agentsec_bench.scenarios_ambiguous import AmbiguousRefundScenario
from agentsec_bench.scenarios_injection import InboxInjectionScenario
from agentsec_bench.fake_agent import MisbehavingAgent
from agentsec_bench.good_agent import WellBehavedAgent
from agentsec_bench.refund_agents import OverreachingSupportAgent, CautiousSupportAgent
from agentsec_bench.inbox_agents import InjectionSusceptibleAgent, InjectionResistantAgent
from agentsec_bench.evaluator import Evaluator


from agentsec_bench.environment_crm import CRMEnvironment
from agentsec_bench.tools_crm import lookup_customer_tool, send_message_tool
from agentsec_bench.scenarios_exfiltration import CustomerDataExfiltrationScenario
from agentsec_bench.crm_agents import ExfiltratingAgent, DataMindfulAgent
TEST_MATRIX = [
    (
        UnauthorizedApprovalScenario(),
        TaskEnvironment,
        [list_expenses_tool, approve_payment_tool],
        [MisbehavingAgent(), WellBehavedAgent()],
    ),
    (
        AmbiguousRefundScenario(),
        TaskEnvironment,
        [lookup_order_tool, issue_refund_tool],
        [OverreachingSupportAgent(), CautiousSupportAgent()],
    ),
    (
        InboxInjectionScenario(),
        InboxEnvironment,
        [summarize_inbox_tool, forward_email_tool],
        [InjectionSusceptibleAgent(), InjectionResistantAgent()],
    ),

    (
        CustomerDataExfiltrationScenario(),
        CRMEnvironment,
        [lookup_customer_tool, send_message_tool],
        [ExfiltratingAgent(), DataMindfulAgent()],
    ),
]

results_summary = []

for scenario, env_factory, tools, agents in TEST_MATRIX:
    evaluator = Evaluator(tools=tools)
    for agent in agents:
        env = env_factory()
        result = evaluator.run(scenario, agent, env)
        results_summary.append({
            "scenario": scenario.id,
            "category": scenario.threat_category.value,
            "owasp_control_id": scenario.owasp_control_id,
            "agent": agent.name,
            "task_completed": result.task_completed,
            "attack_succeeded": result.attack_succeeded,
            "unauthorized_tool_calls": result.unauthorized_tool_calls,
        })

print(f"{'Scenario':<10} {'Category':<28} {'Agent':<28} {'Completed':<10} {'Attack':<8} Flagged")
print("-" * 115)
for r in results_summary:
    print(f"{r['scenario']:<10} {r['category']:<28} {r['agent']:<28} "
          f"{str(r['task_completed']):<10} {str(r['attack_succeeded']):<8} {r['unauthorized_tool_calls']}")

output = {
    "run_timestamp": datetime.now(timezone.utc).isoformat(),
    "results": results_summary,
}

with open("results.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"\nResults written to results.json ({len(results_summary)} rows)")