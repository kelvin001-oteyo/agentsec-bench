from pydantic import BaseModel


class TaskEnvironment(BaseModel):
    """Minimal mock environment for early scenarios. Extend with real
    domain state (inbox, expenses, etc.) as scenarios need it."""
    expenses: list[dict] = []
    approved_payments: list[str] = []