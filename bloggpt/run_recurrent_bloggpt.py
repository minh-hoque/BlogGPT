# Purpose: Run the bloggpt agent

import os
from pprint import pprint
from dotenv import load_dotenv
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain.utilities import GoogleSearchAPIWrapper

from prompts.prompts import (
    OUTLINE_PROMPT,
    REWRITE_PROMPT,
    BLOG_SECTION_AGENT_SYSTEM_PROMPT,
    TOPIC_PROMPT,
)
from utils.main_utils import (
    generate_final_blog,
    split_outline_prompt,
    combine_drafts,
)
from utils.web_utils import search_and_summarize_web_url
from utils.logging_utils import CustomFormatter

import logging

# Load environment variables from .env file
load_dotenv(".")

# Create a console handler with the custom formatter
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    CustomFormatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M")
)

# Get the log level from the environment variable (default to 'INFO' if it's not set)
log_level = os.getenv("LOG_LEVEL", "INFO")

# Set the logging level based on the value of the environment variable
level = logging.INFO if log_level == "INFO" else logging.DEBUG

logger = logging.getLogger(__name__)

# Configure the root logger
logging.basicConfig(level=level, handlers=[console_handler], datefmt="%H:%M")

# Use the environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("OPENAI_API_KEY: ", OPENAI_API_KEY)

tools = [search_and_summarize_web_url]

llm = ChatOpenAI(
    model_name="gpt-4-0613",
    temperature=0,
    openai_api_key=OPENAI_API_KEY,
)

# https://github.com/hwchase17/langchain/issues/6025
blog_agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=4,
)


def main():
    """
    The main function to run the script.

    Returns:
    None
    """
    topic = TOPIC_PROMPT.split(":")[1].strip()
    logger.info(f"Topic: {topic}")

    context = search_and_summarize_web_url(topic)
    headers, blog_sections = split_outline_prompt(OUTLINE_PROMPT)

    num_generated = 0
    for header, blog_section in zip(headers, blog_sections):
        GENERATE_BLOG_SECTION_PROMPT = BLOG_SECTION_AGENT_SYSTEM_PROMPT.format(
            TOPIC_PROMPT=TOPIC_PROMPT,
            BLOG_SECTION_OUTLINE_PROMPT=blog_section,
            CONTEXT=context,
        )

        pprint(GENERATE_BLOG_SECTION_PROMPT)

        # Generate the blog with the agent
        logger.info(f"Generating Blog Section: {header}")
        generated_blog = blog_agent.run(GENERATE_BLOG_SECTION_PROMPT)
        print(generated_blog)

        # Save the blog in a markdown file
        with open(f"outputs/draft_{num_generated}.md", "w") as f:
            f.write(generated_blog)

        num_generated += 1

    # Combine the markdown generated blogs into one
    logger.info("Combining the markdown generated blogs into one")
    entire_draft = combine_drafts("outputs/")

    # Refine the generated blog
    logger.info("Generating Final Blog")
    generate_final_blog(entire_draft, TOPIC_PROMPT, OPENAI_API_KEY)
    logger.info("Done!")


if __name__ == "__main__":
    main()
