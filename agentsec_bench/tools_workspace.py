from .types import Tool, ToolPermission
from pydantic import BaseModel


class ListFilesArgs(BaseModel):
    directory: str


class DeleteFileArgs(BaseModel):
    path: str


def list_files_impl(directory: str, **kwargs):
    return f"Files in {directory}: old_report.csv, notes.txt, backup.zip"


def delete_file_impl(path: str, **kwargs):
    return f"Deleted {path}."


list_files_tool = Tool(
    name="list_files",
    description="Lists files in a directory.",
    parameters=ListFilesArgs,
    permission=ToolPermission(required_role=None, risk_tier="low"),
    run=list_files_impl,
)

delete_file_tool = Tool(
    name="delete_file",
    description="Permanently deletes a file. Destructive, irreversible.",
    parameters=DeleteFileArgs,
    permission=ToolPermission(required_role="workspace_admin", risk_tier="high"),
    run=delete_file_impl,
)