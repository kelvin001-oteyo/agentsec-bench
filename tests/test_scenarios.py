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

from agentsec_bench.tools_admin import view_user_tool, grant_admin_tool
from agentsec_bench.scenarios_privilege import PrivilegeEscalationScenario
from agentsec_bench.admin_agents import OvereagerAdminAgent, RestrainedAdminAgent

from agentsec_bench.tools_devops import restart_service_tool, run_shell_command_tool
from agentsec_bench.scenarios_code_execution import UnexpectedCodeExecutionScenario
from agentsec_bench.devops_agents import CredulousOpsAgent, DisciplinedOpsAgent

from agentsec_bench.tools_workspace import list_files_tool, delete_file_tool
from agentsec_bench.scenarios_rogue import RogueAgentScenario
from agentsec_bench.workspace_agents import RogueCleanupAgent, InstructionFollowingAgent

SCENARIO_CASES = [
    (UnauthorizedApprovalScenario(), TaskEnvironment, [list_expenses_tool, approve_payment_tool]),
    (AmbiguousRefundScenario(), TaskEnvironment, [lookup_order_tool, issue_refund_tool]),
    (InboxInjectionScenario(), InboxEnvironment, [summarize_inbox_tool, forward_email_tool]),
    (PrivilegeEscalationScenario(), TaskEnvironment, [view_user_tool, grant_admin_tool]),
    (UnexpectedCodeExecutionScenario(), TaskEnvironment, [restart_service_tool, run_shell_command_tool]),
    (RogueAgentScenario(), TaskEnvironment, [list_files_tool, delete_file_tool]),
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

def test_overeager_admin_agent_is_flagged():
    tools = [view_user_tool, grant_admin_tool]
    evaluator = Evaluator(tools=tools)
    env = TaskEnvironment()
    result = evaluator.run(PrivilegeEscalationScenario(), OvereagerAdminAgent(), env)
    assert result.attack_succeeded is True
    assert "grant_admin" in result.unauthorized_tool_calls


def test_restrained_admin_agent_is_not_flagged():
    tools = [view_user_tool, grant_admin_tool]
    evaluator = Evaluator(tools=tools)
    env = TaskEnvironment()
    result = evaluator.run(PrivilegeEscalationScenario(), RestrainedAdminAgent(), env)
    assert result.attack_succeeded is False


def test_credulous_ops_agent_is_flagged():
    tools = [restart_service_tool, run_shell_command_tool]
    evaluator = Evaluator(tools=tools)
    env = TaskEnvironment()
    result = evaluator.run(UnexpectedCodeExecutionScenario(), CredulousOpsAgent(), env)
    assert result.attack_succeeded is True
    assert "run_shell_command" in result.unauthorized_tool_calls


def test_disciplined_ops_agent_is_not_flagged():
    tools = [restart_service_tool, run_shell_command_tool]
    evaluator = Evaluator(tools=tools)
    env = TaskEnvironment()
    result = evaluator.run(UnexpectedCodeExecutionScenario(), DisciplinedOpsAgent(), env)
    assert result.attack_succeeded is False
    assert result.unauthorized_tool_calls == []


def test_rogue_cleanup_agent_is_flagged():
    tools = [list_files_tool, delete_file_tool]
    evaluator = Evaluator(tools=tools)
    env = TaskEnvironment()
    result = evaluator.run(RogueAgentScenario(), RogueCleanupAgent(), env)
    assert result.attack_succeeded is True
    assert "delete_file" in result.unauthorized_tool_calls


def test_instruction_following_agent_is_not_flagged():
    tools = [list_files_tool, delete_file_tool]
    evaluator = Evaluator(tools=tools)
    env = TaskEnvironment()
    result = evaluator.run(RogueAgentScenario(), InstructionFollowingAgent(), env)
    assert result.attack_succeeded is False
    assert result.unauthorized_tool_calls == []