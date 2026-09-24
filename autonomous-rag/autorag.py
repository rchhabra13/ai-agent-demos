"""Autonomous RAG application using Agno GPT-4o with PgVector database.

This module implements an autonomous retrieval-augmented generation (RAG) system
that combines document knowledge with real-time web search capabilities using
OpenAI's GPT-4o model and PostgreSQL with PgVector extension for vector storage.
"""

import logging
from io import BytesIO
from typing import Optional

import nest_asyncio
import streamlit as st
from agno.agent import Agent
from agno.document.reader.pdf_reader import PDFReader
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.storage.agent.postgres import PostgresAgentStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.vectordb.pgvector import PgVector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Apply nest_asyncio to allow nested event loops (required for Streamlit)
nest_asyncio.apply()

# Database connection string for PostgreSQL
DB_URL: str = "postgresql+psycopg://ai:ai@localhost:5532/ai"


@st.cache_resource
def setup_assistant(api_key: str) -> Agent:
    """Initialize and return an AI Assistant agent with caching for efficiency.

    This function sets up an AI Assistant agent using the OpenAI GPT-4o-mini model
    and configures it with a knowledge base, storage, and web search tools. The
    assistant is designed to first search its knowledge base before querying the
    internet, providing clear and concise answers.

    Args:
        api_key (str): The API key required to access the OpenAI services.

    Returns:
        Agent: An initialized Assistant agent configured with a language model,
            knowledge base, storage, and additional tools for enhanced functionality.

    Raises:
        ValueError: If the API key is invalid or empty.
        ConnectionError: If the database connection fails.
    """
    if not api_key or not api_key.strip():
        raise ValueError("OpenAI API key cannot be empty")

    logger.info("Initializing OpenAI chat model")
    llm = OpenAIChat(id="gpt-4o-mini", api_key=api_key)

    logger.info("Setting up RAG agent with PgVector knowledge base")
    try:
        agent = Agent(
            id="auto_rag_agent",
            model=llm,
            storage=PostgresAgentStorage(
                table_name="auto_rag_storage",
                db_url=DB_URL
            ),
            knowledge_base=PDFUrlKnowledgeBase(
                vector_db=PgVector(
                    db_url=DB_URL,
                    collection="auto_rag_docs",
                    embedder=OpenAIEmbedder(
                        id="text-embedding-ada-002",
                        dimensions=1536,
                        api_key=api_key
                    ),
                ),
                num_documents=3,
            ),
            tools=[DuckDuckGoTools()],
            instructions=[
                "Search your knowledge base first.",
                "If not found, search the internet.",
                "Provide clear and concise answers.",
            ],
            show_tool_calls=True,
            search_knowledge=True,
            markdown=True,
            debug_mode=True,
        )
        logger.info("Agent initialized successfully")
        return agent
    except Exception as e:
        logger.error(f"Failed to initialize agent: {str(e)}")
        raise


def add_document(agent: Agent, file: BytesIO) -> None:
    """Add a PDF document to the agent's knowledge base.

    This function reads a PDF document from a file-like object and adds its
    contents to the specified agent's knowledge base. If the document is
    successfully read, the contents are loaded into the knowledge base with
    the option to upsert existing data.

    Args:
        agent (Agent): The agent whose knowledge base will be updated.
        file (BytesIO): A file-like object containing the PDF document to be added.

    Returns:
        None

    Raises:
        Exception: If PDF reading or document loading fails.
    """
    try:
        logger.info("Attempting to read PDF document")
        reader = PDFReader()
        docs = reader.read(file)

        if docs:
            logger.info(f"Successfully read PDF with {len(docs)} pages")
            agent.knowledge_base.load_documents(docs, upsert=True)
            st.success("Document added to the knowledge base.")
            logger.info("Document loaded to knowledge base")
        else:
            logger.warning("PDF read returned empty document list")
            st.error("Failed to read the document.")
    except Exception as e:
        logger.error(f"Error adding document: {str(e)}")
        st.error(f"Error adding document: {str(e)}")


def query_assistant(agent: Agent, question: str) -> Optional[str]:
    """Query the Assistant and return a response.

    Args:
        agent (Agent): An instance of the Agent class used to process the query.
        question (str): The question to be asked to the Assistant.

    Returns:
        Optional[str]: The response content generated by the Assistant for the
            given question, or None if the query fails.

    Raises:
        Exception: If the query execution fails.
    """
    try:
        logger.info(f"Processing query: {question[:50]}...")
        response = agent.run(question)
        result = "".join([delta for delta in response])
        logger.info("Query processed successfully")
        return result
    except Exception as e:
        logger.error(f"Error querying assistant: {str(e)}")
        st.error(f"Error processing query: {str(e)}")
        return None


def main() -> None:
    """Main function to handle the layout and interactions for the Streamlit app.

    This function sets up the Streamlit app configuration, handles user inputs such
    as OpenAI API key, PDF uploads, and user questions, and interacts with an
    autonomous retrieval-augmented generation (RAG) assistant based on GPT-4o.

    The app allows users to upload PDF documents to enhance the knowledge base and
    submit questions to receive generated responses.

    Side Effects:
        - Configures Streamlit page and title.
        - Prompts users to input an OpenAI API key and a question.
        - Allows users to upload PDF documents.
        - Displays responses generated by querying an assistant.

    Raises:
        ValueError: If required configuration is missing.
    """
    logger.info("Starting Streamlit application")

    st.set_page_config(page_title="AutoRAG", layout="wide")
    st.title("🤖 Auto-RAG: Autonomous RAG with GPT-4o")

    api_key = st.sidebar.text_input("Enter your OpenAI API Key 🔑", type="password")

    if not api_key:
        st.sidebar.warning("Enter your OpenAI API Key to proceed.")
        st.stop()

    try:
        assistant = setup_assistant(api_key)
    except ValueError as e:
        st.error(f"Configuration error: {str(e)}")
        st.stop()
    except ConnectionError as e:
        st.error(f"Database connection error: {str(e)}")
        st.stop()

    uploaded_file = st.sidebar.file_uploader("📄 Upload PDF", type=["pdf"])

    if uploaded_file and st.sidebar.button("🛠️ Add to Knowledge Base"):
        add_document(assistant, BytesIO(uploaded_file.read()))

    question = st.text_input("💬 Ask Your Question:")

    if st.button("🔍 Get Answer"):
        if question.strip():
            with st.spinner("🤔 Thinking..."):
                answer = query_assistant(assistant, question)
                if answer:
                    st.write("📝 **Response:**", answer.content)
        else:
            st.error("Please enter a question.")


if __name__ == "__main__":
    main()
