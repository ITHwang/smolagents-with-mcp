from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.chat.application.service.chatbot_service import ChatbotService
from app.chat.domain.request import ChatRequest
from app.chat.domain.response import ChatResponse
from app.container import AppContainer

router = APIRouter()


@router.post("/api/v1/chat")
@inject
async def test(
    request: ChatRequest,
    chatbot: ChatbotService = Depends(Provide[AppContainer.chatbot_service]),
) -> StreamingResponse:
    return StreamingResponse(
        chatbot.create_stream_response(request.session_id, request.message),
        media_type="text/event-stream",
    )


# @router.post("/api/v1/chat")
# @inject
# async def test(
#     request: ChatRequest,
#     chatbot: ChatbotService = Depends(Provide[AppContainer.chatbot_service]),
# ) -> ChatResponse:
#     response = await chatbot.create_stream_response(request.session_id, request.message)
#     return ChatResponse(session_id=request.session_id, message=response)
