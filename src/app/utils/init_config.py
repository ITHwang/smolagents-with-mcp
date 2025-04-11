from __future__ import annotations

import json
import os

import boto3
from dependency_injector.providers import Configuration
from loguru import logger

from app.config.env_config import EnvConfig


def init_config(config: Configuration) -> None:
    # yaml 설정값 주입
    init_yaml_config(config)

    # 환경변수 설정값 주입
    init_env_config(config)


def init_yaml_config(config: Configuration) -> None:
    yaml_path = os.path.join(
        os.environ.get("APP_HOME", "app"),
        "config",
        f"{os.environ.get('ENV', 'local')}.yaml",
    )
    config.from_yaml(yaml_path)

    logger.info(f"Loaded configs from yaml file: {yaml_path}")


def init_env_config(config: Configuration) -> None:
    # 환경변수 설정값 주입
    is_asm_available = True
    aws_region = os.getenv("AWS_REGION")
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_secret_manager_name = os.getenv("AWS_SECRET_MANAGER_NAME")

    if aws_region is None:
        logger.info("AWS_REGION is not set.")
        is_asm_available = False
    if aws_access_key_id is None:
        logger.info("AWS_ACCESS_KEY_ID is not set.")
        is_asm_available = False
    if aws_secret_access_key is None:
        logger.info("AWS_SECRET_ACCESS_KEY is not set.")
        is_asm_available = False
    if aws_secret_manager_name is None:
        logger.info("AWS_SECRET_MANAGER_NAME is not set.")
        is_asm_available = False

    if is_asm_available:
        client = boto3.client(
            "secretsmanager",
            region_name=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        response = client.get_secret_value(SecretId=aws_secret_manager_name)

        # Secret의 JSON 문자열을 Python 딕셔너리로 변환
        if "SecretString" in response:
            secrets = json.loads(response["SecretString"])
        else:
            secrets = json.loads(response["SecretBinary"].decode("utf-8"))

        # save as environment variables
        for key, value in secrets.items():
            os.environ[key] = value

        logger.info("Loaded configs from AWS Secret Manager.")
    else:
        logger.warning(
            "It's not ready to use AWS Secret Manager. Force to use .env file."
        )

    config.from_pydantic(EnvConfig())
