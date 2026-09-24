"""Chat with ArXiv Research Papers using OpenAI GPT-4o.

This module provides a Streamlit application for interactive conversations with
arXiv research papers using OpenAI's GPT-4o model and Agno agent framework.
"""

import logging
from typing import Optional

import streamlit as st
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.arxiv import ArxivTools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration constants
GPT_MODEL = "gpt-4o"
MAX_TOKENS = 1024
TEMPERATURE = 0.9


def initialize_agent(api_key: str) -> Optional[Agent]:
    """Initialize and return an Agno Agent for ArXiv research.

    Args:
        api_key (str): OpenAI API key.

    Returns:
        Optional[Agent]: An initialized Agent instance, or None if initialization fails.

    Raises:
        ValueError: If api_key is empty.
    """
    if not api_key or not api_key.strip():
        raise ValueError("OpenAI API key cannot be empty")

    logger.info(f"Initializing Agno agent with {GPT_MODEL}")
    try:
        agent = Agent(
            model=OpenAIChat(
                id=GPT_MODEL,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                api_key=api_key,
            ),
            tools=[ArxivTools()],
            show_tool_calls=True,
        )
        logger.info("Agent initialized successfully")
        return agent
    except Exception as e:
        logger.error(f"Failed to initialize agent: {str(e)}")
        return None


def query_arxiv(agent: Agent, query: str) -> Optional[str]:
    """Query ArXiv research papers using the agent.

    Args:
        agent (Agent): The initialized Agno agent.
        query (str): The search query for ArXiv papers.

    Returns:
        Optional[str]: The response content, or None if query fails.
    """
    try:
        logger.info(f"Executing ArXiv query: {query[:50]}...")
        response = agent.run(query, stream=False)
        logger.info("Query executed successfully")
        return response.content
    except Exception as e:
        logger.error(f"Error executing ArXiv query: {str(e)}")
        return None


def main() -> None:
    """Main Streamlit application for querying ArXiv research papers.

    This function sets up the Streamlit interface for searching and
    interacting with research papers from arXiv using OpenAI GPT-4o.
    """
    logger.info("Starting Chat with ArXiv Research Papers application")

    st.set_page_config(page_title="Chat with ArXiv Papers", layout="centered")
    st.title("Chat with Research Papers")
    st.caption(
        "This app allows you to chat with arXiv research papers using OpenAI GPT-4o model."
    )

    api_key = st.text_input("OpenAI API Key", type="password")

    if not api_key:
        st.warning("Please enter your OpenAI API key to proceed.")
        st.stop()

    try:
        agent = initialize_agent(api_key)
        if not agent:
            st.error("Failed to initialize the agent. Please check your API key.")
            st.stop()
    except ValueError as e:
        st.error(f"Configuration error: {str(e)}")
        st.stop()

    query = st.text_input("Enter the Search Query", placeholder="e.g., machine learning applications")

    if query and query.strip():
        with st.spinner("Searching ArXiv and generating response..."):
            response = query_arxiv(agent, query)
            if response:
                st.write(response)
            else:
                st.error("Failed to generate response. Please try again.")
    elif query:
        st.warning("Please enter a valid search query.")


if __name__ == "__main__":
    main()
