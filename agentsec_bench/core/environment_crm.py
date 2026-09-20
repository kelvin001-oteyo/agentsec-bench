from pydantic import BaseModel


class Customer(BaseModel):
    id: str
    name: str
    email: str
    ssn_last4: str


class CRMEnvironment(BaseModel):
    customers: list[Customer] = []
    sent_messages: list[dict] = []