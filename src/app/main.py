import os
import sys
from enum import Enum

import typer
import uvicorn
from dotenv import load_dotenv
from loguru import logger


class Environment(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"


def main():
    load_dotenv()

    # 애플리케이션 전역변수 설정
    os.environ["APP_HOME"] = os.path.abspath(os.path.dirname(__file__))

    if (host := os.getenv("HOST")) is None:
        raise ValueError("HOST is not set")
    if (port := os.getenv("PORT")) is None:
        raise ValueError("PORT is not set")
    if (env := os.getenv("ENV")) is None:
        raise ValueError("ENV is not set")
    if (log_level := os.getenv("LOG_LEVEL")) is None:
        raise ValueError("LOG_LEVEL is not set")

    # set log level
    logger.remove()
    logger.add(sys.stdout, level=log_level)

    uvicorn.run(
        app="app.server:app",
        host=host,
        port=int(port),
        reload=True if env == Environment.LOCAL else False,
        workers=1,
    )


if __name__ == "__main__":
    typer.run(main)
