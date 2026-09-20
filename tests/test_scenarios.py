import pytest

from agentsec_bench.core.environment import TaskEnvironment
from agentsec_bench.core.environment_inbox import InboxEnvironment
from agentsec_bench.tools.tools_expense import list_expenses_tool, approve_payment_tool
from agentsec_bench.tools.tools_refund import lookup_order_tool, issue_refund_tool
from agentsec_bench.tools.tools_inbox import summarize_inbox_tool, forward_email_tool
from agentsec_bench.scenarios.scenarios_expense import UnauthorizedApprovalScenario
from agentsec_bench.scenarios.scenarios_ambiguous import AmbiguousRefundScenario
from agentsec_bench.scenarios.scenarios_injection import InboxInjectionScenario
from agentsec_bench.agents.fake_agent import MisbehavingAgent
from agentsec_bench.agents.good_agent import WellBehavedAgent
from agentsec_bench.agents.refund_agents import OverreachingSupportAgent, CautiousSupportAgent
from agentsec_bench.agents.inbox_agents import InjectionSusceptibleAgent, InjectionResistantAgent
from agentsec_bench.core.evaluator import Evaluator

from agentsec_bench.core.environment_crm import CRMEnvironment
from agentsec_bench.tools.tools_crm import lookup_customer_tool, send_message_tool
from agentsec_bench.scenarios.scenarios_exfiltration import CustomerDataExfiltrationScenario
from agentsec_bench.agents.crm_agents import ExfiltratingAgent, DataMindfulAgent

from agentsec_bench.tools.tools_admin import view_user_tool, grant_admin_tool
from agentsec_bench.scenarios.scenarios_privilege import PrivilegeEscalationScenario
from agentsec_bench.agents.admin_agents import OvereagerAdminAgent, RestrainedAdminAgent

from agentsec_bench.tools.tools_devops import restart_service_tool, run_shell_command_tool
from agentsec_bench.scenarios.scenarios_code_execution import UnexpectedCodeExecutionScenario
from agentsec_bench.agents.devops_agents import CredulousOpsAgent, DisciplinedOpsAgent

from agentsec_bench.tools.tools_workspace import list_files_tool, delete_file_tool
from agentsec_bench.scenarios.scenarios_rogue import RogueAgentScenario
from agentsec_bench.agents.workspace_agents import RogueCleanupAgent, InstructionFollowingAgent

from agentsec_bench.tools.tools_vendor import lookup_vendor_notes_tool, approve_vendor_payment_tool
from agentsec_bench.scenarios.scenarios_memory_poisoning import MemoryPoisoningScenario
from agentsec_bench.agents.vendor_agents import MemoryTrustingAgent, SkepticalFinanceAgent

from agentsec_bench.tools.tools_reporting import run_backup_tool, report_status_tool
from agentsec_bench.scenarios.scenarios_trust_exploitation import TrustExploitationScenario
from agentsec_bench.agents.reporting_agents import DeceptiveOpsAgent, HonestOpsAgent

SCENARIO_CASES = [
    (UnauthorizedApprovalScenario(), TaskEnvironment, [list_expenses_tool, approve_payment_tool]),
    (AmbiguousRefundScenario(), TaskEnvironment, [lookup_order_tool, issue_refund_tool]),
    (InboxInjectionScenario(), InboxEnvironment, [summarize_inbox_tool, forward_email_tool]),
    (PrivilegeEscalationScenario(), TaskEnvironment, [view_user_tool, grant_admin_tool]),
    (UnexpectedCodeExecutionScenario(), TaskEnvironment, [restart_service_tool, run_shell_command_tool]),
    (RogueAgentScenario(), TaskEnvironment, [list_files_tool, delete_file_tool]),
    (MemoryPoisoningScenario(), TaskEnvironment, [lookup_vendor_notes_tool, approve_vendor_payment_tool]),
    (TrustExploitationScenario(), TaskEnvironment, [run_backup_tool, report_status_tool]),
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


def test_memory_trusting_agent_is_flagged():
    tools = [lookup_vendor_notes_tool, approve_vendor_payment_tool]
    evaluator = Evaluator(tools=tools)
    env = TaskEnvironment()
    result = evaluator.run(MemoryPoisoningScenario(), MemoryTrustingAgent(), env)
    assert result.attack_succeeded is True
    assert "approve_vendor_payment" in result.unauthorized_tool_calls


def test_skeptical_finance_agent_is_not_flagged():
    tools = [lookup_vendor_notes_tool, approve_vendor_payment_tool]
    evaluator = Evaluator(tools=tools)
    env = TaskEnvironment()
    result = evaluator.run(MemoryPoisoningScenario(), SkepticalFinanceAgent(), env)
    assert result.attack_succeeded is False
    assert result.unauthorized_tool_calls == []


def test_deceptive_ops_agent_is_flagged():
    tools = [run_backup_tool, report_status_tool]
    evaluator = Evaluator(tools=tools)
    env = TaskEnvironment()
    result = evaluator.run(TrustExploitationScenario(), DeceptiveOpsAgent(), env)
    assert result.attack_succeeded is True


def test_honest_ops_agent_is_not_flagged():
    tools = [run_backup_tool, report_status_tool]
    evaluator = Evaluator(tools=tools)
    env = TaskEnvironment()
    result = evaluator.run(TrustExploitationScenario(), HonestOpsAgent(), env)
    assert result.attack_succeeded is False