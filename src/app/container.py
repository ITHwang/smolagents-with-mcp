from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Configuration, Singleton
from smolagents import LiteLLMModel
from google.adk.models.lite_llm import LiteLlm

from app.chat.application.service.chatbot_service import ChatbotService
from app.utils.init_config import init_config


class AppContainer(DeclarativeContainer):
    """의존성 주입을 관리하는 DI 컨테이너

    1. 설정값 주입
    - 환경 변수: 환경변수를 읽고 관리하는 `app.config.env_config.Config` 클래스로부터 주입받습니다.
    - 다른 변수: 개발 환경에 따른 yaml 파일을 읽어서 주입받습니다.
    - 애플리케이션 구동, 실행에 필요한 모든 설정값은 DI Container에서 주입받고 관리합니다.
    - 설정 클래스를 제외한 모든 클래스는 DI Container에서 생성됩니다.
    """

    # router 연동
    # TODO: AppContainer를 전역 container로 두고 chat_container도 정의
    wiring_config = WiringConfiguration(packages=["app"])

    # 설정값 주입
    config = Configuration()
    init_config(config)

    # connection
    # TODO: LiteLLM 활용하여 정의할 LiteLLMFactory 클래스로 주입하기
    model = config.llm_tasks.chat.config_list.chat_gpt4o.model()
    params = config.llm_tasks.chat.config_list.chat_gpt4o.params()

    # smolagents
    # litellm_model = Singleton(
    #     LiteLLMModel,
    #     model_id=model,
    #     api_key=config.openai.api_key,
    #     **params,
    # )

    # google adk
    litellm_model = Singleton(
        LiteLlm,
        model=model,
        api_key=config.openai.api_key,
        **params,
    )

    agent_prompt = config.llm_tasks.chat.config_list.chat_gpt4o.prompt()

    chatbot_service = Singleton(
        ChatbotService,
        llm_model=litellm_model,
        agent_prompt=agent_prompt,
    )
