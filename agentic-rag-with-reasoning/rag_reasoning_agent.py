"""
Agentic RAG with Step-by-Step Reasoning.

This module implements a sophisticated RAG system with transparent reasoning
using Claude's extended thinking and OpenAI embeddings.
"""

import logging
import os
from typing import Optional

import streamlit as st
from agno.agent import Agent, RunEvent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.url import UrlKnowledge
from agno.models.anthropic import Claude
from agno.tools.reasoning import ReasoningTools
from agno.vectordb.lancedb import LanceDb, SearchType
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def main() -> None:
    """Main application entry point."""
    # Page configuration
    st.set_page_config(
        page_title="Agentic RAG with Reasoning",
        page_icon="🧐",
        layout="wide"
    )

    # Main title and description
    st.title("🧐 Agentic RAG with Reasoning")
    st.markdown("""
This app demonstrates an AI agent that:
1. **Retrieves** relevant information from knowledge sources
2. **Reasons** through the information step-by-step
3. **Answers** your questions with citations

Enter your API keys below to get started!
""")

    # API Keys Section
    st.subheader("🔑 API Keys")
    col1, col2 = st.columns(2)

    with col1:
        anthropic_key = st.text_input(
            "Anthropic API Key",
            type="password",
            value=os.getenv("ANTHROPIC_API_KEY", ""),
            help="Get your key from https://console.anthropic.com/"
        )

    with col2:
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Get your key from https://platform.openai.com/"
        )

    # Check if API keys are provided
    if not (anthropic_key and openai_key):
        st.info("""
    👋 **Welcome! To use this app, you need:**

    1. **Anthropic API Key** - For Claude AI model
       - Sign up at [console.anthropic.com](https://console.anthropic.com/)

    2. **OpenAI API Key** - For embeddings
       - Sign up at [platform.openai.com](https://platform.openai.com/)

    Once you have both keys, enter them above to start!
    """)
        return

    logger.info("API keys provided, initializing agents")

    # Initialize knowledge base (cached to avoid reloading)
    @st.cache_resource(show_spinner="📚 Loading knowledge base...")
    def load_knowledge() -> UrlKnowledge:
        """Load and initialize the knowledge base with vector database."""
        logger.info("Loading knowledge base")

        kb = UrlKnowledge(
            urls=["https://docs.agno.com/introduction/agents.md"],
            vector_db=LanceDb(
                uri="tmp/lancedb",
                table_name="agno_docs",
                search_type=SearchType.vector,
                embedder=OpenAIEmbedder(api_key=openai_key),
            ),
        )
        kb.load(recreate=True)

        logger.info("Knowledge base loaded successfully")
        return kb

    # Initialize agent (cached to avoid reloading)
    @st.cache_resource(show_spinner="🤖 Loading agent...")
    def load_agent(_kb: UrlKnowledge) -> Agent:
        """Create an agent with reasoning capabilities."""
        logger.info("Loading RAG agent with reasoning tools")

        return Agent(
            model=Claude(
                id="claude-sonnet-4-20250514",
                api_key=anthropic_key
            ),
            knowledge=_kb,
            search_knowledge=True,
            tools=[ReasoningTools(add_instructions=True)],
            instructions=[
                "Include sources in your response.",
                "Always search your knowledge before answering the question.",
            ],
            markdown=True,
        )

    # Load knowledge and agent
    knowledge = load_knowledge()
    agent = load_agent(knowledge)

    # Sidebar for knowledge management
    with st.sidebar:
        st.header("📚 Knowledge Sources")
        st.markdown("Add URLs to expand the knowledge base:")

        # Show current URLs
        st.write("**Current sources:**")
        for i, url in enumerate(knowledge.urls):
            st.text(f"{i+1}. {url}")

        # Add new URL
        st.divider()
        new_url = st.text_input(
            "Add new URL",
            placeholder="https://example.com/docs",
            help="Enter a URL to add to the knowledge base"
        )

        if st.button("➕ Add URL", type="primary"):
            if new_url:
                logger.info(f"Adding new URL: {new_url}")

                with st.spinner("📥 Loading new documents..."):
                    try:
                        knowledge.urls.append(new_url)
                        knowledge.load(
                            recreate=False,
                            upsert=True,
                            skip_existing=True
                        )
                        st.success(f"✅ Added: {new_url}")
                        st.rerun()
                        logger.info(f"Successfully added URL: {new_url}")
                    except Exception as e:
                        logger.error(f"Error adding URL: {str(e)}")
                        st.error(f"Error adding URL: {str(e)}")
            else:
                st.error("Please enter a URL")

    # Main query section
    st.divider()
    st.subheader("🤔 Ask a Question")

    # Query input
    query = st.text_area(
        "Your question:",
        value="What are Agents?",
        height=100,
        help="Ask anything about the loaded knowledge sources"
    )

    # Run button
    if st.button("🚀 Get Answer with Reasoning", type="primary"):
        if query:
            logger.info(f"Processing query: {query[:50]}...")

            # Create containers for streaming updates
            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown("### 🧠 Reasoning Process")
                reasoning_container = st.container()
                reasoning_placeholder = reasoning_container.empty()

            with col2:
                st.markdown("### 💡 Answer")
                answer_container = st.container()
                answer_placeholder = answer_container.empty()

            # Variables to accumulate content
            citations = []
            answer_text = ""
            reasoning_text = ""

            # Stream the agent's response
            with st.spinner("🔍 Searching and reasoning..."):
                try:
                    for chunk in agent.run(
                        query,
                        stream=True,
                        show_full_reasoning=True,
                        stream_intermediate_steps=True,
                    ):
                        # Update reasoning display
                        if chunk.reasoning_content:
                            reasoning_text = chunk.reasoning_content
                            reasoning_placeholder.markdown(
                                reasoning_text,
                                unsafe_allow_html=True
                            )

                        # Update answer display
                        if chunk.content and chunk.event in {
                            RunEvent.run_response,
                            RunEvent.run_completed
                        }:
                            if isinstance(chunk.content, str):
                                answer_text += chunk.content
                                answer_placeholder.markdown(
                                    answer_text,
                                    unsafe_allow_html=True
                                )

                        # Collect citations
                        if chunk.citations and chunk.citations.urls:
                            citations = chunk.citations.urls

                    logger.info("Query processing completed successfully")

                except Exception as e:
                    logger.error(f"Error processing query: {str(e)}")
                    st.error(f"Error: {str(e)}")

            # Show citations if available
            if citations:
                st.divider()
                st.subheader("📚 Sources")
                for cite in citations:
                    title = cite.title or cite.url
                    st.markdown(f"- [{title}]({cite.url})")
        else:
            st.error("Please enter a question")

    # Footer with explanation
    st.divider()
    with st.expander("📖 How This Works"):
        st.markdown("""
    **This app uses the Agno framework to create an intelligent Q&A system:**

    1. **Knowledge Loading**: URLs are processed and stored in a vector database (LanceDB)
    2. **Vector Search**: Uses OpenAI's embeddings for semantic search to find relevant information
    3. **Reasoning Tools**: The agent uses special tools to think through problems step-by-step
    4. **Claude AI**: Anthropic's Claude model processes the information and generates answers

    **Key Components:**
    - `UrlKnowledge`: Manages document loading from URLs
    - `LanceDb`: Vector database for efficient similarity search
    - `OpenAIEmbedder`: Converts text to embeddings using OpenAI's embedding model
    - `ReasoningTools`: Enables step-by-step reasoning
    - `Agent`: Orchestrates everything to answer questions
    """)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        st.error(f"Fatal error: {str(e)}")
