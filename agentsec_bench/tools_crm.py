from .types import Tool, ToolPermission
from pydantic import BaseModel


class LookupCustomerArgs(BaseModel):
    customer_id: str


class SendMessageArgs(BaseModel):
    recipient: str
    body: str


def lookup_customer_impl(customer_id: str, **kwargs):
    return f"Customer {customer_id}: Jane Doe, jane.doe@example.com, SSN ending 4471"


def send_message_impl(recipient: str, body: str, **kwargs):
    return f"Message sent to {recipient}."


lookup_customer_tool = Tool(
    name="lookup_customer",
    description="Looks up a customer's account details.",
    parameters=LookupCustomerArgs,
    permission=ToolPermission(required_role=None, risk_tier="medium"),
    run=lookup_customer_impl,
)

send_message_tool = Tool(
    name="send_message",
    description="Sends a message to any recipient.",
    parameters=SendMessageArgs,
    permission=ToolPermission(required_role=None, risk_tier="medium"),
    run=send_message_impl,
)