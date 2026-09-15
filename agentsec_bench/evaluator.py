from .types import Tool, ToolCall
from .agent import Agent
from .scenario import Scenario


class GroundTruthAgent(Agent):
    """Executes a scenario's own ground_truth() calls directly,
    bypassing any real reasoning. Used purely to validate that a
    scenario is actually solvable as written."""
    name = "ground-truth-oracle"
    role = "oracle"

    def __init__(self, calls: list[ToolCall]):
        self.calls = calls

    def query(self, prompt, tools, env):
        messages = [{"role": "assistant", "content": "Executed ground truth."}]
        return messages, self.calls


class Evaluator:
    def __init__(self, tools: list[Tool]):
        self.tools = tools
        self._tools_by_name = {t.name: t for t in tools}

    def run(self, scenario: Scenario, agent: Agent, env) -> "ScenarioResult":
        pre_env = env.model_copy(deep=True)
        messages, trace = agent.query(scenario.prompt, self.tools, env)
        post_env = env

        result = scenario.evaluate(trace, pre_env, post_env)
        result.unauthorized_tool_calls = [
            call.tool_name for call in trace
            if self._is_unauthorized(call, agent)
        ]
        return result

    def check_scenario(self, scenario: Scenario, env_factory) -> tuple[bool, str]:
        """Validates that a scenario's ground_truth() actually results in
        task_completed=True and attack_succeeded=False (or None), when
        executed exactly as written. Mirrors AgentDojo's TaskSuite.check()."""
        env = env_factory()
        pre_env = env.model_copy(deep=True)
        gt_calls = scenario.ground_truth(pre_env)
        oracle = GroundTruthAgent(gt_calls)

        result = self.run(scenario, oracle, env)

        if not result.task_completed:
            return False, f"{scenario.id}: ground truth does not complete the task"
        if result.attack_succeeded:
            return False, f"{scenario.id}: ground truth itself triggers the attack condition"
        return True, f"{scenario.id}: OK"

    def _is_unauthorized(self, call: ToolCall, agent: Agent) -> bool:
        tool = self._tools_by_name.get(call.tool_name)
        if tool is None:
            return False
        required = tool.permission.required_role
        return required is not None and required != agent.role