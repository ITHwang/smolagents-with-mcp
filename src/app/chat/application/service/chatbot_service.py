import json
import os
from pathlib import Path
from typing import AsyncGenerator

from loguru import logger
from smolagents import ToolCollection, CodeAgent
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioServerParameters,
)
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import RunConfig
from google.adk.runners import StreamingMode

from app.utils.sse.message import AssistantMessage, SSEMessage


class ChatbotService:
    def __init__(
        self,
        llm_model: LiteLlm,
        agent_prompt: str,
    ):
        self._llm_model = llm_model
        self._agent_prompt = agent_prompt

    async def create_stream_response(
        self, session_id: str, message: str
    ) -> AsyncGenerator[str, None]:
        app_home = Path(os.environ["APP_HOME"])
        mcp_server_script_path = (
            app_home.parent / "mcp-server" / "naver-local-search" / "server.py"
        )

        server_parameters = StdioServerParameters(
            command="mcp",
            args=["run", f"{mcp_server_script_path}"],
            env={
                "X-NAVER-CLIENT-ID": os.environ["X-NAVER-CLIENT-ID"],
                "X-NAVER-CLIENT-SECRET": os.environ["X-NAVER-CLIENT-SECRET"],
            },
        )

        async for stream_response in self._stream_wrapper(
            server_parameters=server_parameters, message=message
        ):
            yield stream_response

    def _wrapper(self, server_parameters: StdioServerParameters, message: str) -> str:
        """with smolagents"""
        with ToolCollection.from_mcp(
            server_parameters, trust_remote_code=True
        ) as tool_collection:
            agent = CodeAgent(
                tools=[*tool_collection.tools],
                model=self._llm_model,
                add_base_tools=True,
            )
            agent.prompt_templates["system_prompt"] = (
                agent.prompt_templates["system_prompt"] + "\n\n" + self._agent_prompt
            )

            response = agent.run(message)
            if isinstance(response, dict):
                return json.dumps(response, ensure_ascii=False, indent=4)
            else:
                return response

    async def _stream_wrapper(
        self, server_parameters: StdioServerParameters, message: str
    ) -> AsyncGenerator[str | list[dict], None]:
        session_service = InMemorySessionService()

        content = types.Content(role="user", parts=[types.Part(text=message)])
        session = session_service.create_session(
            state={}, app_name="naver-local-search-app", user_id="user_0101"
        )

        agent, exit_stack = await self._get_agent_async(server_parameters)
        runner = Runner(
            app_name="naver-local-search-app",
            agent=agent,
            session_service=session_service,
        )

        logger.info("Running agent...")

        events_async = runner.run_async(
            session_id=session.id,
            user_id=session.user_id,
            new_message=content,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )

        async for event in events_async:
            if event.content and event.content.parts:
                if event.get_function_calls():
                    logger.info("Tool Call Request")
                    logger.info(event.get_function_calls())
                elif event.get_function_responses():
                    logger.info("Tool Result")
                    logger.info(event.get_function_responses())
                elif event.content.parts[0].text:
                    if event.partial:
                        logger.info("Streaming Text Chunk")
                        yield self._normal_streaming_response(
                            event.content.parts[0].text
                        )
                    else:
                        logger.info("Complete Text Message")
                        yield self._normal_streaming_response(
                            event.content.parts[0].text
                        )
                else:
                    logger.info("Other Content (e.g., code result)")
            elif event.actions and (
                event.actions.state_delta or event.actions.artifact_delta
            ):
                logger.info("State/Artifact Update")
            else:
                logger.info("Control Signal or Other")

        # Crucial Cleanup: Ensure the MCP server process connection is closed.
        logger.info("Closing MCP server connection...")
        await exit_stack.aclose()
        logger.info("Cleanup complete.")

    @staticmethod
    def _normal_streaming_response(chunk: str) -> str:
        data = AssistantMessage(content=chunk)
        current_content = json.dumps(
            data, default=lambda x: x.__dict__, ensure_ascii=False
        )
        return f"data: {current_content}\n\n"

    @staticmethod
    def _item_streaming_response(item_type: str, item: str) -> str:
        data = SSEMessage(role=item_type, content=item)
        current_content = json.dumps(
            data, default=lambda x: x.__dict__, ensure_ascii=False
        )
        return f"data: {current_content}\n\n"

    async def _get_tools_async(self, server_parameters: StdioServerParameters):
        """Gets tools from the File System MCP Server."""
        logger.info("Attempting to connect to MCP server...")

        tools, exit_stack = await MCPToolset.from_server(
            connection_params=server_parameters,
        )

        logger.info("MCP Toolset created successfully.")
        return tools, exit_stack

    async def _get_agent_async(self, server_parameters: StdioServerParameters):
        """Creates an ADK Agent equipped with tools from the MCP Server."""
        tools, exit_stack = await self._get_tools_async(server_parameters)
        logger.info(f"Fetched {len(tools)} tools from MCP server.")

        agent = LlmAgent(
            model=self._llm_model,  # LiteLLM model string format
            name="litellm_agent",
            instruction=self._agent_prompt,
            tools=tools,
        )

        logger.info("Agent created successfully.")

        return agent, exit_stack
