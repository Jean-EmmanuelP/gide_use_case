# uv run test.agent
# load dotenv
from dotenv import load_dotenv
import os
from smolagents import CodeAgent

# Charge the .env file
load_dotenv()
groq_api_key=os.getenv("GROQ_API_KEY")

## Use a model provider
# Run: export ANTHROPIC_API_KEY=rojgoregkk
from smolagents import LiteLLMModel
model = LiteLLMModel("groq/llama3-8b-8192", api_key=groq_api_key)

# Use the HuggingFace Api, for free (rated limited)
# from smolagents import HfApiModel
# model = HfApiModel()

# It's safest to modify the system prompt than to replace it, especially since it's includes imports.
# from smolagents.prompts import CODE_SYSTEM_PROMPT
# modified_system_prompt = CODE_SYSTEM_PROMPT + "\\nBe funny."
# You can either run a custom model from the hub or take your own from LiteLLMModel

agent = CodeAgent(
    tools=[],
    model=model,
    add_base_tools=False ## include web search -> by default it is duckduckgo search ,
    # verbosity_level=2, # to include the thoughts
    # system_prompt=modified_system_prompt
)

# Steps

# 1 : take the pdf and transform to .md pymupdf
# 2 : take the pdf and transform to .toc
# 3 : say to the agent to use only the files provided by the user

# { key: value } * 10 -> Bailleur -> Qui est le Bailleur ?

agent.run("What is the result of 2 power 3.7384 ?")




