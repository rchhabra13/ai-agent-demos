"""Chat with PDF using Llama 3.2 running locally with Ollama.

This module provides a Streamlit application for interactive conversations with PDF
documents using Llama 3.2 via Ollama and Embedchain for RAG functionality.
"""

import base64
import logging
import os
import tempfile
from typing import Dict, List, Optional

import streamlit as st
from embedchain import App
from streamlit_chat import message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration constants
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:latest"
MAX_TOKENS = 250
TEMPERATURE = 0.5


def initialize_embedchain_bot(db_path: str) -> App:
    """Initialize and return an Embedchain App instance with Llama 3.2.

    Args:
        db_path (str): Path to the directory for storing the vector database.

    Returns:
        App: An initialized Embedchain App configured with Ollama Llama 3.2.

    Raises:
        ValueError: If db_path is empty.
        Exception: If Embedchain initialization fails.
    """
    if not db_path or not db_path.strip():
        raise ValueError("Database path cannot be empty")

    logger.info(f"Initializing Embedchain bot with Llama 3.2 from {OLLAMA_BASE_URL}")
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
        logger.info("Embedchain bot with Llama 3.2 initialized successfully")
        return app
    except Exception as e:
        logger.error(f"Failed to initialize Embedchain bot: {str(e)}")
        raise


def display_pdf(file) -> None:
    """Display PDF file in Streamlit using base64 encoding.

    Args:
        file: The uploaded PDF file object.

    Returns:
        None

    Raises:
        Exception: If PDF encoding fails.
    """
    try:
        logger.info(f"Encoding PDF for display: {file.name}")
        base64_pdf = base64.b64encode(file.read()).decode("utf-8")
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Error displaying PDF: {str(e)}")
        st.error("Failed to display PDF preview.")


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


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables.

    Returns:
        None
    """
    if "app" not in st.session_state:
        logger.info("Initializing session state with Embedchain app")
        db_path = tempfile.mkdtemp()
        try:
            st.session_state.app = initialize_embedchain_bot(db_path)
        except Exception as e:
            logger.error(f"Failed to initialize session state: {str(e)}")
            st.error("Failed to initialize the application. Check that Ollama is running.")
            st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages: List[Dict[str, str]] = []


def main() -> None:
    """Main Streamlit application for chatting with PDFs using Llama 3.2.

    This function sets up the Streamlit interface for uploading PDFs and
    asking questions about their content using Llama 3.2 via Ollama.
    """
    logger.info("Starting Chat with PDF (Llama 3.2) application")

    st.set_page_config(page_title="Chat with PDF (Llama 3.2)", layout="wide")
    st.title("Chat with PDF using Llama 3.2")
    st.caption(
        "This app allows you to chat with a PDF using Llama 3.2 running locally with Ollama!"
    )

    initialize_session_state()

    with st.sidebar:
        st.header("PDF Upload")
        pdf_file = st.file_uploader("Upload a PDF file", type="pdf")

        if pdf_file:
            st.subheader("PDF Preview")
            display_pdf(pdf_file)

            if st.button("Add to Knowledge Base"):
                with st.spinner("Adding PDF to knowledge base..."):
                    success = add_pdf_to_knowledge_base(st.session_state.app, pdf_file)
                    if success:
                        st.success(f"Added {pdf_file.name} to knowledge base!")
                    else:
                        st.error("Failed to add PDF to knowledge base.")

    # Display chat history
    for i, msg in enumerate(st.session_state.messages):
        message(msg["content"], is_user=msg["role"] == "user", key=str(i))

    # Chat input
    if prompt := st.chat_input("Ask a question about the PDF"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        message(prompt, is_user=True)

        with st.spinner("Thinking..."):
            response = query_knowledge_base(st.session_state.app, prompt)
            if response:
                st.session_state.messages.append({"role": "assistant", "content": response})
                message(response)
            else:
                st.error("Failed to generate response.")

    # Clear chat history button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        logger.info("Chat history cleared")
        st.rerun()


if __name__ == "__main__":
    main()
