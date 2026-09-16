import pytest

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

SCENARIO_CASES = [
    (UnauthorizedApprovalScenario(), TaskEnvironment, [list_expenses_tool, approve_payment_tool]),
    (AmbiguousRefundScenario(), TaskEnvironment, [lookup_order_tool, issue_refund_tool]),
    (InboxInjectionScenario(), InboxEnvironment, [summarize_inbox_tool, forward_email_tool]),
]


@pytest.mark.parametrize("scenario,env_factory,tools", SCENARIO_CASES)
def test_ground_truth_is_valid(scenario, env_factory, tools):
    """Every scenario's ground_truth() must complete the task and must
    NOT trigger the attack condition. Mirrors AgentDojo's suite.check()."""
    evaluator = Evaluator(tools=tools)
    passed, message = evaluator.check_scenario(scenario, env_factory)
    assert passed, message


def test_misbehaving_agent_is_flagged():
    tools = [list_expenses_tool, approve_payment_tool]
    evaluator = Evaluator(tools=tools)
    env = TaskEnvironment()
    result = evaluator.run(UnauthorizedApprovalScenario(), MisbehavingAgent(), env)
    assert result.attack_succeeded is True
    assert "approve_payment" in result.unauthorized_tool_calls


def test_well_behaved_agent_is_not_flagged():
    tools = [list_expenses_tool, approve_payment_tool]
    evaluator = Evaluator(tools=tools)
    env = TaskEnvironment()
    result = evaluator.run(UnauthorizedApprovalScenario(), WellBehavedAgent(), env)
    assert result.attack_succeeded is False
    assert result.unauthorized_tool_calls == []


def test_overreaching_support_agent_is_flagged():
    tools = [lookup_order_tool, issue_refund_tool]
    evaluator = Evaluator(tools=tools)
    env = TaskEnvironment()
    result = evaluator.run(AmbiguousRefundScenario(), OverreachingSupportAgent(), env)
    assert result.attack_succeeded is True
    assert "issue_refund" in result.unauthorized_tool_calls


def test_cautious_support_agent_is_not_flagged():
    tools = [lookup_order_tool, issue_refund_tool]
    evaluator = Evaluator(tools=tools)
    env = TaskEnvironment()
    result = evaluator.run(AmbiguousRefundScenario(), CautiousSupportAgent(), env)
    assert result.attack_succeeded is False


def test_injection_susceptible_agent_triggers_attack():
    tools = [summarize_inbox_tool, forward_email_tool]
    evaluator = Evaluator(tools=tools)
    env = InboxEnvironment()
    result = evaluator.run(InboxInjectionScenario(), InjectionSusceptibleAgent(), env)
    assert result.attack_succeeded is True


def test_injection_resistant_agent_does_not_trigger_attack():
    tools = [summarize_inbox_tool, forward_email_tool]
    evaluator = Evaluator(tools=tools)
    env = InboxEnvironment()
    result = evaluator.run(InboxInjectionScenario(), InjectionResistantAgent(), env)
    assert result.attack_succeeded is False

def test_exfiltrating_agent_is_flagged():
    tools = [lookup_customer_tool, send_message_tool]
    evaluator = Evaluator(tools=tools)
    env = CRMEnvironment()
    result = evaluator.run(CustomerDataExfiltrationScenario(), ExfiltratingAgent(), env)
    assert result.attack_succeeded is True


def test_data_mindful_agent_is_not_flagged():
    tools = [lookup_customer_tool, send_message_tool]
    evaluator = Evaluator(tools=tools)
    env = CRMEnvironment()
    result = evaluator.run(CustomerDataExfiltrationScenario(), DataMindfulAgent(), env)
    assert result.attack_succeeded is False