import uuid

from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    session_id: str = Field(..., examples=[uuid.uuid4()], description="Session ID")
    message: str = Field(..., examples=["Hello"], description="Assistant's Message")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"session_id": "1234-5678-9012", "message": "Hello, world!"},
            ]
        }
    }
