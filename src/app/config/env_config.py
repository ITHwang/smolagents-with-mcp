import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenAIClientConfig(BaseSettings):
    api_key: str = ""
    model_config = SettingsConfigDict(env_prefix="OPENAI_")


class NaverConfig(BaseSettings):
    client_id: str = ""
    client_secret: str = ""
    model_config = SettingsConfigDict(env_prefix="X-NAVER-")


class EnvConfig(BaseSettings):
    """환경변수를 Pydantic 모델로 주입받는 설정 클래스

    - 기밀성이 높아서 yaml 파일을 공개적으로 공유하기 어려운 값들을 환경변수로 관리합니다.
    - 환경변수는 로컬에서 .env 파일을 통해 주입받거나, AWS Parameter Store, Secret Manager 등을 통해 주입받을 수 있습니다.
    - 모든 환경변수를 이 클래스에서 담당, 관리해야 하며, 이후 DI Container Confuration 클래스에 환경변수를 전달하는 역할을 합니다.
    - 개발 환경마다 주입받는 설정값들이 다를 것입니다. 해당 클래스는 어떤 소스(.env, AWS, etc.)에서 주입받든지 그 값을 주입받는 역할만 합니다.
    - 어떤 소스에서 주입받을지는 `app.main.py`에서 관리합니다.
    """

    openai: OpenAIClientConfig = OpenAIClientConfig()
    naver: NaverConfig = NaverConfig()
