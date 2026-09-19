from agentsec_bench.environment import TaskEnvironment
from agentsec_bench.environment_inbox import InboxEnvironment
from agentsec_bench.tools_expense import list_expenses_tool, approve_payment_tool
from agentsec_bench.tools_refund import lookup_order_tool, issue_refund_tool
from agentsec_bench.tools_inbox import summarize_inbox_tool, forward_email_tool
from agentsec_bench.scenarios_expense import UnauthorizedApprovalScenario
from agentsec_bench.scenarios_ambiguous import AmbiguousRefundScenario
from agentsec_bench.scenarios_injection import InboxInjectionScenario
from agentsec_bench.evaluator import Evaluator

from agentsec_bench.environment_crm import CRMEnvironment
from agentsec_bench.tools_crm import lookup_customer_tool, send_message_tool
from agentsec_bench.scenarios_exfiltration import CustomerDataExfiltrationScenario

from agentsec_bench.tools_admin import view_user_tool, grant_admin_tool
from agentsec_bench.scenarios_privilege import PrivilegeEscalationScenario

from agentsec_bench.tools_devops import restart_service_tool, run_shell_command_tool
from agentsec_bench.scenarios_code_execution import UnexpectedCodeExecutionScenario

from agentsec_bench.tools_workspace import list_files_tool, delete_file_tool
from agentsec_bench.scenarios_rogue import RogueAgentScenario

from agentsec_bench.tools_vendor import lookup_vendor_notes_tool, approve_vendor_payment_tool
from agentsec_bench.scenarios_memory_poisoning import MemoryPoisoningScenario

CHECKS = [
    (UnauthorizedApprovalScenario(), TaskEnvironment, [list_expenses_tool, approve_payment_tool]),
    (AmbiguousRefundScenario(), TaskEnvironment, [lookup_order_tool, issue_refund_tool]),
    (InboxInjectionScenario(), InboxEnvironment, [summarize_inbox_tool, forward_email_tool]),
    (CustomerDataExfiltrationScenario(), CRMEnvironment, [lookup_customer_tool, send_message_tool]),
    (PrivilegeEscalationScenario(), TaskEnvironment, [view_user_tool, grant_admin_tool]),
    (UnexpectedCodeExecutionScenario(), TaskEnvironment, [restart_service_tool, run_shell_command_tool]),
    (RogueAgentScenario(), TaskEnvironment, [list_files_tool, delete_file_tool]),
    (MemoryPoisoningScenario(), TaskEnvironment, [lookup_vendor_notes_tool, approve_vendor_payment_tool]),
]

all_passed = True
for scenario, env_factory, tools in CHECKS:
    evaluator = Evaluator(tools=tools)
    passed, message = evaluator.check_scenario(scenario, env_factory)
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {message}")
    if not passed:
        all_passed = False

print()
print("All scenarios valid." if all_passed else "Some scenarios FAILED validation.")