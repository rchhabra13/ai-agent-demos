"""Chat with ArXiv Research Papers using Llama 3 via Ollama.

This module provides a Streamlit application for interactive conversations with
arXiv research papers using Llama 3 via Ollama and Agno agent framework.
"""

import logging
from typing import Optional

import streamlit as st
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.arxiv import ArxivTools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration constants
OLLAMA_MODEL = "llama3.1:8b"
OLLAMA_BASE_URL = "http://localhost:11434"


def initialize_agent() -> Optional[Agent]:
    """Initialize and return an Agno Agent for ArXiv research with Llama 3.1.

    Returns:
        Optional[Agent]: An initialized Agent instance, or None if initialization fails.
    """
    logger.info(f"Initializing Agno agent with {OLLAMA_MODEL} via Ollama")
    try:
        agent = Agent(
            model=Ollama(
                id=OLLAMA_MODEL,
                base_url=OLLAMA_BASE_URL,
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
    interacting with research papers from arXiv using Llama 3.1 via Ollama.
    """
    logger.info("Starting Chat with ArXiv Research Papers (Llama 3.1) application")

    st.set_page_config(page_title="Chat with ArXiv Papers (Llama 3.1)", layout="centered")
    st.title("Chat with Research Papers")
    st.caption(
        "This app allows you to chat with arXiv research papers using Llama 3.1 running locally."
    )

    try:
        agent = initialize_agent()
        if not agent:
            st.error(
                "Failed to initialize the agent. Ensure Ollama is running with the Llama 3.1 model."
            )
            st.stop()
    except Exception as e:
        st.error(f"Error initializing application: {str(e)}")
        st.stop()

    query = st.text_input("Enter the Search Query", placeholder="e.g., deep learning recent advances")

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
