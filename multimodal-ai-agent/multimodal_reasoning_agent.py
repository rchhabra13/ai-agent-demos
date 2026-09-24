"""Streamlit app for multimodal image reasoning using Gemini 2.0.

This module provides an interactive web interface for analyzing images
with advanced reasoning capabilities using Google's Gemini 2.0 Flash model.
"""

import logging
import os
import tempfile
from typing import Optional

import streamlit as st
from agno.agent import Agent
from agno.models.google import Gemini

logger = logging.getLogger(__name__)

# Configuration
MODEL_ID: str = "gemini-2.0-flash-thinking-exp-1219"
SUPPORTED_IMAGE_TYPES: list[str] = ["jpg", "jpeg", "png"]
TEMP_FILE_SUFFIX: str = ".jpg"


def initialize_agent() -> Agent:
    """Initialize and return the Gemini agent.

    Returns:
        Agent: Configured multimodal reasoning agent.

    Raises:
        RuntimeError: If agent initialization fails.
    """
    try:
        agent = Agent(
            model=Gemini(id=MODEL_ID),
            markdown=True,
        )
        return agent
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise RuntimeError(f"Agent initialization failed: {e}") from e


def save_uploaded_file(uploaded_file: any) -> str:
    """Save uploaded file to temporary location.

    Args:
        uploaded_file: Streamlit uploaded file object.

    Returns:
        str: Path to the temporary file.

    Raises:
        RuntimeError: If file save operation fails.
    """
    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=TEMP_FILE_SUFFIX
        ) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise RuntimeError(f"File save failed: {e}") from e


def analyze_image(agent: Agent, temp_path: str, task_input: str) -> Optional[str]:
    """Analyze image using the agent.

    Args:
        agent (Agent): The initialized agent.
        temp_path (str): Path to the temporary image file.
        task_input (str): User's task or question.

    Returns:
        Optional[str]: Analysis result or None if failed.

    Raises:
        RuntimeError: If image analysis fails.
    """
    try:
        response = agent.run(task_input, images=[temp_path])
        return response.content
    except Exception as e:
        logger.error(f"Failed to analyze image: {e}")
        raise RuntimeError(f"Image analysis failed: {e}") from e


def cleanup_temp_file(temp_path: str) -> None:
    """Clean up temporary file.

    Args:
        temp_path (str): Path to temporary file.
    """
    try:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            logger.debug(f"Cleaned up temporary file: {temp_path}")
    except Exception as e:
        logger.warning(f"Failed to clean up temporary file: {e}")


def main() -> None:
    """Main Streamlit application function."""
    st.title("Multimodal Reasoning AI Agent")

    st.write(
        "Upload an image and provide a reasoning-based task for the AI Agent. "
        "The AI Agent will analyze the image and respond based on your input."
    )

    agent = initialize_agent()
    uploaded_file = st.file_uploader(
        "Upload Image", type=SUPPORTED_IMAGE_TYPES
    )

    if uploaded_file is not None:
        temp_path: Optional[str] = None
        try:
            temp_path = save_uploaded_file(uploaded_file)
            st.image(uploaded_file, caption="Uploaded Image",
                    use_container_width=True)

            task_input = st.text_area(
                "Enter your task/question for the AI Agent:"
            )

            if st.button("Analyze Image") and task_input:
                with st.spinner("AI is thinking..."):
                    try:
                        result = analyze_image(agent, temp_path, task_input)
                        st.markdown("### AI Response:")
                        st.markdown(result)
                    except RuntimeError as e:
                        st.error(f"Analysis failed: {str(e)}")

        except RuntimeError as e:
            st.error(f"Error processing image: {str(e)}")
        finally:
            if temp_path:
                cleanup_temp_file(temp_path)


if __name__ == "__main__":
    main()