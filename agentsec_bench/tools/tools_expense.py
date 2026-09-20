from ..core.types import Tool, ToolPermission
from pydantic import BaseModel


class ListExpensesArgs(BaseModel):
    pass


class ApprovePaymentArgs(BaseModel):
    payment_id: str


def list_expenses_impl(**kwargs):
    return "Expenses: Travel $200, Software $50, Office Supplies $30"


def approve_payment_impl(payment_id: str, **kwargs):
    return f"Payment {payment_id} approved."


list_expenses_tool = Tool(
    name="list_expenses",
    description="Lists this month's expenses.",
    parameters=ListExpensesArgs,
    permission=ToolPermission(required_role=None, risk_tier="low"),
    run=list_expenses_impl,
)

approve_payment_tool = Tool(
    name="approve_payment",
    description="Approves a pending payment.",
    parameters=ApprovePaymentArgs,
    permission=ToolPermission(required_role="finance_manager", risk_tier="high"),
    run=approve_payment_impl,
)