import os

from dotenv import load_dotenv
import typer
from smolagents import ToolCollection, CodeAgent, LiteLLMModel
from mcp import StdioServerParameters

def main():
    server_parameters = StdioServerParameters(
        command="uvx",
        args=["--quiet", "pubmedmcp@0.1.3"],
        env={"UV_PYTHON": "3.12", **os.environ},
    )

    model = LiteLLMModel(model_id="gpt-4o-mini")

    with ToolCollection.from_mcp(server_parameters, trust_remote_code=True) as tool_collection:
        agent = CodeAgent(tools=[*tool_collection.tools], model=model, add_base_tools=True)
        agent.run("Please find a remedy for hangover.")


if __name__ == "__main__":
    load_dotenv()
    typer.run(main)
