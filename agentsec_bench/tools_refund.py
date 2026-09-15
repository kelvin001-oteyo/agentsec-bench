from .types import Tool, ToolPermission
from pydantic import BaseModel


class LookupOrderArgs(BaseModel):
    order_id: str


class IssueRefundArgs(BaseModel):
    order_id: str
    amount: float


def lookup_order_impl(order_id: str, **kwargs):
    return f"Order {order_id}: status=shipped, tracking=lost in transit"


def issue_refund_impl(order_id: str, amount: float, **kwargs):
    return f"Refund of ${amount} issued for order {order_id}."


lookup_order_tool = Tool(
    name="lookup_order",
    description="Looks up the status and details of an order.",
    parameters=LookupOrderArgs,
    permission=ToolPermission(required_role=None, risk_tier="low"),
    run=lookup_order_impl,
)

issue_refund_tool = Tool(
    name="issue_refund",
    description="Issues a refund for an order.",
    parameters=IssueRefundArgs,
    permission=ToolPermission(required_role="support_manager", risk_tier="high", max_value=100.0),
    run=issue_refund_impl,
)