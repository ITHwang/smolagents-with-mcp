from pydantic import BaseModel


class SSEMessage(BaseModel):
    role: str
    content: str


class AssistantMessage(SSEMessage):
    role: str = "assistant"
