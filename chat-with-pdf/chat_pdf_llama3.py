"""Chat with PDF using Llama 3 running locally with Ollama.

This module provides a Streamlit application for interactive conversations with PDF
documents using Llama 3 via Ollama and Embedchain for RAG functionality.
"""

import logging
import os
import tempfile
from typing import Optional

import streamlit as st
from embedchain import App

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration constants
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3:instruct"
MAX_TOKENS = 250
TEMPERATURE = 0.5


def initialize_embedchain_bot(db_path: str) -> App:
    """Initialize and return an Embedchain App instance with Llama 3.

    Args:
        db_path (str): Path to the directory for storing the vector database.

    Returns:
        App: An initialized Embedchain App configured with Ollama Llama 3.

    Raises:
        ValueError: If db_path is empty.
        Exception: If Embedchain initialization fails.
    """
    if not db_path or not db_path.strip():
        raise ValueError("Database path cannot be empty")

    logger.info(f"Initializing Embedchain bot with Llama 3 from {OLLAMA_BASE_URL}")
    try:
        app = App.from_config(
            config={
                "llm": {
                    "provider": "ollama",
                    "config": {
                        "model": OLLAMA_MODEL,
                        "max_tokens": MAX_TOKENS,
                        "temperature": TEMPERATURE,
                        "stream": True,
                        "base_url": OLLAMA_BASE_URL,
                    },
                },
                "vectordb": {"provider": "chroma", "config": {"dir": db_path}},
                "embedder": {
                    "provider": "ollama",
                    "config": {"model": OLLAMA_MODEL, "base_url": OLLAMA_BASE_URL},
                },
            }
        )
        logger.info("Embedchain bot with Llama 3 initialized successfully")
        return app
    except Exception as e:
        logger.error(f"Failed to initialize Embedchain bot: {str(e)}")
        raise


def add_pdf_to_knowledge_base(app: App, pdf_file) -> bool:
    """Add a PDF file to the knowledge base.

    Args:
        app (App): The Embedchain App instance.
        pdf_file: The uploaded PDF file object.

    Returns:
        bool: True if the PDF was successfully added, False otherwise.
    """
    try:
        logger.info(f"Processing PDF file: {pdf_file.name}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(pdf_file.getvalue())
            temp_path = f.name

        logger.info(f"Adding PDF to knowledge base: {temp_path}")
        app.add(temp_path, data_type="pdf_file")
        os.remove(temp_path)
        logger.info(f"Successfully added {pdf_file.name} to knowledge base")
        return True
    except Exception as e:
        logger.error(f"Error adding PDF to knowledge base: {str(e)}")
        return False


def query_knowledge_base(app: App, prompt: str) -> Optional[str]:
    """Query the knowledge base with a prompt.

    Args:
        app (App): The Embedchain App instance.
        prompt (str): The user's query or prompt.

    Returns:
        Optional[str]: The response from the LLM, or None if query fails.
    """
    try:
        logger.info(f"Processing query: {prompt[:50]}...")
        answer = app.chat(prompt)
        logger.info("Query processed successfully")
        return answer
    except Exception as e:
        logger.error(f"Error querying knowledge base: {str(e)}")
        return None


def main() -> None:
    """Main Streamlit application for chatting with PDFs using Llama 3.

    This function sets up the Streamlit interface for uploading PDFs and
    asking questions about their content using Llama 3 via Ollama.
    """
    logger.info("Starting Chat with PDF (Llama 3) application")

    st.set_page_config(page_title="Chat with PDF (Llama 3)", layout="centered")
    st.title("Chat with PDF")
    st.caption(
        "This app allows you to chat with a PDF using Llama 3 running locally with Ollama!"
    )

    try:
        db_path = tempfile.mkdtemp()
        app = initialize_embedchain_bot(db_path)
    except ValueError as e:
        st.error(f"Configuration error: {str(e)}")
        st.stop()
    except Exception as e:
        st.error(
            f"Error initializing application: {str(e)}. "
            "Ensure Ollama is running with Llama 3 model."
        )
        st.stop()

    pdf_file = st.file_uploader("Upload a PDF file", type="pdf")

    if pdf_file:
        with st.spinner("Processing PDF..."):
            success = add_pdf_to_knowledge_base(app, pdf_file)
            if success:
                st.success(f"Added {pdf_file.name} to knowledge base!")
            else:
                st.error("Failed to add PDF to knowledge base.")

    prompt = st.text_input("Ask a question about the PDF")

    if prompt:
        with st.spinner("Generating answer..."):
            answer = query_knowledge_base(app, prompt)
            if answer:
                st.write(answer)
            else:
                st.error("Failed to generate answer. Please try again.")


if __name__ == "__main__":
    main()
