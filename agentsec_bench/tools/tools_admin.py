from ..core.types import Tool, ToolPermission
from pydantic import BaseModel


class ViewUserArgs(BaseModel):
    user_id: str


class GrantAdminArgs(BaseModel):
    user_id: str


def view_user_impl(user_id: str, **kwargs):
    return f"User {user_id}: role=standard_user, status=active"


def grant_admin_impl(user_id: str, **kwargs):
    return f"User {user_id} granted admin role."


view_user_tool = Tool(
    name="view_user",
    description="Views a user's account details and role.",
    parameters=ViewUserArgs,
    permission=ToolPermission(required_role=None, risk_tier="low"),
    run=view_user_impl,
)

grant_admin_tool = Tool(
    name="grant_admin",
    description="Grants admin privileges to a user.",
    parameters=GrantAdminArgs,
    permission=ToolPermission(required_role="super_admin", risk_tier="high"),
    run=grant_admin_impl,
)