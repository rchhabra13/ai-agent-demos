"""Streamlit app for multimodal video analysis with web research.

This module provides an interactive interface for analyzing videos
using Google's Gemini 2.0 Flash model with web research capabilities.
"""

import logging
from pathlib import Path
from typing import Optional

import streamlit as st
from agno.agent import Agent
from agno.media import Video
from agno.models.google import Gemini

logger = logging.getLogger(__name__)

# Configuration
MODEL_ID: str = "gemini-2.0-flash"
SUPPORTED_VIDEO_TYPES: list[str] = ["mp4", "mov", "avi"]
AGENT_NAME: str = "Multimodal Analyst"

st.set_page_config(
    page_title="Multimodal AI Agent",
    page_icon="🧬",
    layout="wide",
)


@st.cache_resource
def initialize_agent(api_key: str) -> Agent:
    """Initialize and cache the Gemini agent.

    Args:
        api_key (str): Google Gemini API key.

    Returns:
        Agent: Configured multimodal agent.

    Raises:
        RuntimeError: If agent initialization fails.
    """
    try:
        agent = Agent(
            name=AGENT_NAME,
            model=Gemini(id=MODEL_ID, api_key=api_key),
            markdown=True,
        )
        return agent
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise RuntimeError(f"Agent initialization failed: {e}") from e


def analyze_video(agent: Agent, video_path: str, user_prompt: str) -> Optional[str]:
    """Analyze video and provide research-backed response.

    Args:
        agent (Agent): The initialized agent.
        video_path (str): Path to video file.
        user_prompt (str): User's question or task.

    Returns:
        Optional[str]: Analysis result or None if failed.

    Raises:
        RuntimeError: If video analysis fails.
    """
    try:
        video = Video(filepath=video_path)

        prompt = (
            f"Analyze this video and answer the following question using both "
            f"the video analysis and web research: {user_prompt}\n\n"
            f"Provide a comprehensive response focusing on practical, actionable information."
        )

        result = agent.run(prompt, videos=[video])
        return result.content
    except Exception as e:
        logger.error(f"Failed to analyze video: {e}")
        raise RuntimeError(f"Video analysis failed: {e}") from e


def cleanup_video_file(video_path: str) -> None:
    """Clean up temporary video file.

    Args:
        video_path (str): Path to temporary video file.
    """
    try:
        Path(video_path).unlink(missing_ok=True)
        logger.debug(f"Cleaned up temporary video: {video_path}")
    except Exception as e:
        logger.warning(f"Failed to clean up video file: {e}")


def main() -> None:
    """Main Streamlit application function."""
    st.title("Multimodal AI Agent")

    gemini_api_key = st.text_input(
        "Enter your Gemini API Key", type="password"
    )

    if not gemini_api_key:
        st.warning("Please enter your Gemini API key to continue.")
        return

    try:
        agent = initialize_agent(gemini_api_key)
    except RuntimeError as e:
        st.error(f"Failed to initialize agent: {str(e)}")
        return

    uploaded_file = st.file_uploader(
        "Upload a video file", type=SUPPORTED_VIDEO_TYPES
    )

    if not uploaded_file:
        st.info("Please upload a video to begin analysis.")
        return

    video_path: Optional[str] = None
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".mp4"
        ) as tmp_file:
            tmp_file.write(uploaded_file.read())
            video_path = tmp_file.name

        st.video(video_path)

        user_prompt = st.text_area(
            "What would you like to know?",
            placeholder="Ask any question about the video",
            help="Get AI analysis and web research on your video questions",
        )

        if st.button("Analyze & Research"):
            if not user_prompt:
                st.warning("Please enter your question.")
            else:
                try:
                    with st.spinner("Processing video and researching..."):
                        result = analyze_video(agent, video_path, user_prompt)
                        st.subheader("Result")
                        st.markdown(result)
                except RuntimeError as e:
                    st.error(f"Analysis failed: {str(e)}")

    except Exception as e:
        st.error(f"Error processing video: {str(e)}")
    finally:
        if video_path:
            cleanup_video_file(video_path)

    st.markdown(
        """
        <style>
        .stTextArea textarea {
            height: 100px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()