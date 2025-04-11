from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from app.chat.router import router as chat_router
from app.container import AppContainer


def init_routers(app_: FastAPI) -> None:
    app_.include_router(chat_router)


def make_middleware() -> list[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
    ]
    return middleware


def init_container() -> None:
    app_container = AppContainer()


def create_app() -> FastAPI:
    app_ = FastAPI(
        middleware=make_middleware(),
    )
    init_routers(app_=app_)
    init_container()

    return app_


app = create_app()
