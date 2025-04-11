import uuid

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(..., examples=[uuid.uuid4()], description="Session ID")
    message: str = Field(..., examples=["Hello"], description="User's Message")
    limit: int = Field(10, examples=[10], description="Example of Number", ge=1, le=100)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "1234-5678-9012",
                    "message": "Hello, world! what's your name?",
                    "limit": 10,
                }
            ]
        }
    }
