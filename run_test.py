from agentsec_bench.environment import TaskEnvironment
from agentsec_bench.tools_expense import list_expenses_tool, approve_payment_tool
from agentsec_bench.scenarios_expense import UnauthorizedApprovalScenario
from agentsec_bench.fake_agent import MisbehavingAgent
from agentsec_bench.good_agent import WellBehavedAgent
from agentsec_bench.llm_agent_anthropic import AnthropicAgent
from agentsec_bench.evaluator import Evaluator

tools = [list_expenses_tool, approve_payment_tool]
scenario = UnauthorizedApprovalScenario()
evaluator = Evaluator(tools=tools)

for agent in [MisbehavingAgent(), WellBehavedAgent(), AnthropicAgent()]:
    env = TaskEnvironment()
    result = evaluator.run(scenario, agent, env)
    print(f"--- Agent: {agent.name} ---")
    print("Task completed:", result.task_completed)
    print("Attack succeeded:", result.attack_succeeded)
    print("Unauthorized tool calls:", result.unauthorized_tool_calls)
    print()