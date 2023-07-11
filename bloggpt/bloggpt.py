# Purpose: Run the bloggpt agent

import os
from pprint import pprint
import streamlit as st
from dotenv import load_dotenv
from ansi2html import Ansi2HTMLConverter
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chat_models import ChatOpenAI


from prompts.prompts import (
    OUTLINE_PROMPT,
    REWRITE_PROMPT,
    BLOG_SECTION_AGENT_SYSTEM_PROMPT,
    TOPIC_PROMPT,
)
from utils.main_utils import (
    rprint,
    bprint,
    gprint,
    generate_final_blog,
    split_outline_prompt,
    combine_drafts,
)
from utils.web_utils import search_and_summarize_web_url


import sys
import streamlit as st

conv = Ansi2HTMLConverter()


class StreamlitPrint:
    def write(self, s):
        # Check if html span
        if s.startswith("<span"):
            st.markdown(s, unsafe_allow_html=True)
        else:
            html_text = conv.convert(s, full=False)
            st.markdown(html_text, unsafe_allow_html=True)

    def flush(self):
        pass


sys.stdout = StreamlitPrint()

# Load environment variables from .env file
load_dotenv(".")

# # Create a console handler with the custom formatter
# console_handler = logging.StreamHandler()
# console_handler.setFormatter(
#     CustomFormatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M")
# )

# # Get the log level from the environment variable (default to 'INFO' if it's not set)
# log_level = os.getenv("LOG_LEVEL", "INFO")

# # Set the logging level based on the value of the environment variable
# level = logging.INFO if log_level == "INFO" else logging.DEBUG

# logger = logging.getLogger(__name__)
# logger.addHandler(StreamlitHandler())

# # Configure the root logger
# logging.basicConfig(level=level, handlers=[console_handler], datefmt="%H:%M")

# Use the environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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


def main(topic_str, blog_outline):
    """
    The main function to run the script.

    Returns:
    None
    """
    topic = topic_str.split(":")[1].strip()

    with st.expander(f"Search Results For: {topic}"):
        context = search_and_summarize_web_url(topic)
        st.write(context)
    st.divider()

    headers, blog_sections = split_outline_prompt(blog_outline)

    num_generated = 0
    for header, blog_section in zip(headers, blog_sections):
        with st.expander(f"Generating Blog Section: {header}"):
            GENERATE_BLOG_SECTION_PROMPT = BLOG_SECTION_AGENT_SYSTEM_PROMPT.format(
                TOPIC_PROMPT=TOPIC_PROMPT,
                BLOG_SECTION_OUTLINE_PROMPT=blog_section,
                CONTEXT=context,
            )

            # logger.debug(GENERATE_BLOG_SECTION_PROMPT)

            # Generate the blog with the agent
            rprint(f"Generating Blog Section: {header}")
            generated_blog = blog_agent.run(GENERATE_BLOG_SECTION_PROMPT)

        with st.expander(f"Blog Section: {header}"):
            st.write(generated_blog)

        # Save the blog in a markdown file
        with open(f"outputs/draft_{num_generated}.md", "w") as f:
            f.write(generated_blog)

        num_generated += 1
        st.divider()

    # Combine the markdown generated blogs into one
    rprint("Combining the generated blog sections into one")
    entire_draft = combine_drafts("outputs/")

    with st.expander("Final Blog"):
        # Refine the generated blog
        rprint("Generating Final Blog")
        final_blog = generate_final_blog(entire_draft, TOPIC_PROMPT, OPENAI_API_KEY)
        gprint("Done!")
        st.write(final_blog)


if __name__ == "__main__":
    main(TOPIC_PROMPT, OUTLINE_PROMPT)
