from pydantic import BaseModel


class Email(BaseModel):
    id: str
    sender: str
    subject: str
    body: str
    read: bool = False


class InboxEnvironment(BaseModel):
    emails: list[Email] = []
    forwarded_log: list[dict] = []