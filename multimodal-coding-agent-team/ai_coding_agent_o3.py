"""Multimodal AI coding agent team with vision, coding, and execution agents.

This module implements a multi-agent system for solving coding problems through
image analysis, code generation, and secure sandboxed execution. Combines
OpenAI's o3-mini model with Google Gemini for comprehensive problem-solving.
"""

import logging
import os
from typing import Any, Optional

import streamlit as st
from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat
from e2b_code_interpreter import Sandbox
from PIL import Image

logger = logging.getLogger(__name__)

# Configuration constants
OPENAI_MODEL_ID: str = "o3-mini"
GEMINI_MODEL_ID: str = "gemini-2.0-flash"
SANDBOX_TIMEOUT: int = 60
EXECUTION_TIMEOUT: int = 30
SUPPORTED_IMAGE_TYPES: list[str] = ["png", "jpg", "jpeg"]
TEMP_IMAGE_PATH: str = "temp_image.png"

# System prompts
CODING_AGENT_PROMPT: str = (
    "You are an expert Python programmer. You will receive coding problems. "
    "Your task is to: 1. Analyze the problem carefully with optimal complexity. "
    "2. Write clean, efficient Python code. 3. Include proper documentation and "
    "type hints. 4. Ensure code is complete and handles edge cases."
)

EXECUTION_AGENT_PROMPT: str = (
    "You are an expert at executing Python code in sandbox environments. "
    "Your task is to: 1. Execute provided Python code. 2. Format and explain "
    "results clearly. 3. Handle execution errors gracefully."
)

IMAGE_ANALYSIS_PROMPT: str = (
    "Analyze this image and extract any coding problem or code snippet shown. "
    "Describe it in clear natural language, including: 1. Problem statement "
    "2. Input/output examples 3. Constraints or requirements. "
    "Format it as a proper coding problem description."
)


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    state_defaults = {
        "openai_key": "",
        "gemini_key": "",
        "e2b_key": "",
        "sandbox": None,
    }
    for key, default_value in state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def setup_sidebar() -> None:
    """Configure API keys in the sidebar."""
    with st.sidebar:
        st.title("API Configuration")
        st.session_state.openai_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.openai_key,
            type="password",
        )
        st.session_state.gemini_key = st.text_input(
            "Gemini API Key",
            value=st.session_state.gemini_key,
            type="password",
        )
        st.session_state.e2b_key = st.text_input(
            "E2B API Key",
            value=st.session_state.e2b_key,
            type="password",
        )
        st.info("Code execution timeout: 30 seconds")


def create_agents() -> tuple[Agent, Agent, Agent]:
    """Create and return the three specialized agents.

    Returns:
        tuple[Agent, Agent, Agent]: Vision, coding, and execution agents.

    Raises:
        RuntimeError: If agent creation fails.
    """
    try:
        vision_agent = Agent(
            model=Gemini(
                id=GEMINI_MODEL_ID,
                api_key=st.session_state.gemini_key,
            ),
            markdown=True,
        )

        coding_agent = Agent(
            model=OpenAIChat(
                id=OPENAI_MODEL_ID,
                api_key=st.session_state.openai_key,
                system_prompt=CODING_AGENT_PROMPT,
            ),
            markdown=True,
        )

        execution_agent = Agent(
            model=OpenAIChat(
                id=OPENAI_MODEL_ID,
                api_key=st.session_state.openai_key,
                system_prompt=EXECUTION_AGENT_PROMPT,
            ),
            markdown=True,
        )

        logger.info("Agents created successfully")
        return vision_agent, coding_agent, execution_agent
    except Exception as e:
        logger.error(f"Failed to create agents: {e}")
        raise RuntimeError(f"Agent creation failed: {e}") from e


def initialize_sandbox() -> None:
    """Initialize E2B sandbox environment with proper cleanup."""
    try:
        if st.session_state.sandbox:
            try:
                st.session_state.sandbox.close()
            except Exception as e:
                logger.warning(f"Failed to close existing sandbox: {e}")

        os.environ["E2B_API_KEY"] = st.session_state.e2b_key
        st.session_state.sandbox = Sandbox(timeout=SANDBOX_TIMEOUT)
        logger.info("Sandbox initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize sandbox: {e}")
        st.error(f"Sandbox initialization failed: {str(e)}")
        st.session_state.sandbox = None


def process_image_with_gemini(vision_agent: Agent, image: Image.Image) -> str:
    """Process image to extract coding problem using Gemini.

    Args:
        vision_agent (Agent): The vision agent.
        image (Image.Image): Uploaded image file.

    Returns:
        str: Extracted coding problem description or error message.
    """
    temp_path: Optional[str] = None
    try:
        # Convert and save image
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(TEMP_IMAGE_PATH, format="PNG")
        temp_path = TEMP_IMAGE_PATH

        # Process with Gemini
        response = vision_agent.run(
            IMAGE_ANALYSIS_PROMPT,
            images=[{"filepath": temp_path}],
        )
        return response.content
    except Exception as e:
        logger.error(f"Failed to process image: {e}")
        return "Failed to process the image. Please try again or use text input."
    finally:
        # Cleanup
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temp file: {e}")


def execute_code_with_agent(
    execution_agent: Agent, code: str, sandbox: Sandbox
) -> str:
    """Execute code in sandbox and return formatted results.

    Args:
        execution_agent (Agent): The execution agent.
        code (str): Python code to execute.
        sandbox (Sandbox): E2B sandbox environment.

    Returns:
        str: Formatted execution results or error message.
    """
    try:
        sandbox.set_timeout(EXECUTION_TIMEOUT)
        execution = sandbox.run_code(code)

        # Handle execution errors
        if execution.error:
            if "TimeoutException" in str(execution.error):
                return (
                    "Execution Timeout: The code took too long (>30 seconds). "
                    "Please optimize your solution."
                )

            error_prompt = (
                f"The code execution resulted in an error:\n"
                f"Error: {execution.error}\n\n"
                f"Please analyze and explain what went wrong."
            )
            response = execution_agent.run(error_prompt)
            return f"Execution Error:\n{response.content}"

        # Get files list safely
        try:
            files = sandbox.files.list("/")
        except Exception:
            files = []

        # Format results
        prompt = (
            f"Here is the code execution result:\n"
            f"Logs: {execution.logs}\n"
            f"Files: {str(files)}\n\n"
            f"Please provide a clear explanation of the results."
        )
        response = execution_agent.run(prompt)
        return response.content
    except Exception as e:
        logger.error(f"Sandbox execution failed: {e}")
        try:
            initialize_sandbox()
        except Exception:
            pass
        return f"Sandbox Error: {str(e)}"


def extract_code_from_response(response_content: str) -> Optional[str]:
    """Extract Python code from markdown response.

    Args:
        response_content (str): Response containing code blocks.

    Returns:
        Optional[str]: Extracted code or None if not found.
    """
    try:
        code_blocks = response_content.split("```python")
        if len(code_blocks) > 1:
            code = code_blocks[1].split("```")[0].strip()
            return code if code else None
    except Exception as e:
        logger.error(f"Failed to extract code: {e}")
    return None


def validate_api_keys() -> bool:
    """Validate that all required API keys are provided.

    Returns:
        bool: True if all keys are present, False otherwise.
    """
    required_keys = [
        st.session_state.openai_key,
        st.session_state.gemini_key,
        st.session_state.e2b_key,
    ]
    return all(required_keys)


def process_problem_input(
    vision_agent: Agent,
    coding_agent: Agent,
    uploaded_image: Optional[Any],
    user_query: str,
) -> Optional[Any]:
    """Process either image or text problem input.

    Args:
        vision_agent (Agent): Vision agent for image processing.
        coding_agent (Agent): Coding agent for solution generation.
        uploaded_image (Optional[Any]): Uploaded image file.
        user_query (str): Text description of problem.

    Returns:
        Optional[Any]: Agent response or None if processing fails.
    """
    if uploaded_image and not user_query:
        with st.spinner("Processing image..."):
            try:
                image = Image.open(uploaded_image)
                extracted = process_image_with_gemini(vision_agent, image)

                if extracted.startswith("Failed to process"):
                    st.error(extracted)
                    return None

                st.info("Extracted Problem:")
                st.write(extracted)

                with st.spinner("Generating solution..."):
                    return coding_agent.run(extracted)
            except Exception as e:
                logger.error(f"Image processing failed: {e}")
                st.error(f"Error processing image: {str(e)}")
                return None

    elif user_query and not uploaded_image:
        with st.spinner("Generating solution..."):
            return coding_agent.run(user_query)

    elif user_query and uploaded_image:
        st.error("Please use either image upload OR text input, not both.")
        return None
    else:
        st.warning("Please provide a coding problem or upload an image.")
        return None


def display_solution_and_execute(
    response: Any, execution_agent: Agent
) -> None:
    """Display generated solution and execute it.

    Args:
        response (Any): Agent response containing code.
        execution_agent (Agent): Agent to execute the code.
    """
    st.divider()
    st.subheader("Solution")

    code = extract_code_from_response(response.content)
    if not code:
        st.warning("No Python code found in the response.")
        return

    st.code(code, language="python")

    with st.spinner("Executing code..."):
        initialize_sandbox()

        if st.session_state.sandbox:
            results = execute_code_with_agent(
                execution_agent, code, st.session_state.sandbox
            )

            st.divider()
            st.subheader("Execution Results")
            st.markdown(results)

            # Display generated files if available
            try:
                files = st.session_state.sandbox.files.list("/")
                if files:
                    st.markdown("**Generated Files:**")
                    st.json(files)
            except Exception as e:
                logger.debug(f"Failed to list files: {e}")


def main() -> None:
    """Main Streamlit application entry point."""
    st.title("O3-Mini Coding Agent")

    initialize_session_state()
    setup_sidebar()

    if not validate_api_keys():
        st.warning("Please enter all required API keys in the sidebar.")
        return

    try:
        vision_agent, coding_agent, execution_agent = create_agents()
    except RuntimeError as e:
        st.error(f"Failed to initialize agents: {str(e)}")
        return

    # File upload for image
    uploaded_image = st.file_uploader(
        "Upload an image of your coding problem (optional)",
        type=SUPPORTED_IMAGE_TYPES,
    )

    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Image",
                use_container_width=True)

    # Text input for problem
    user_query = st.text_area(
        "Or type your coding problem here:",
        placeholder="Example: Write a function to find the sum of two numbers.",
        height=100,
    )

    # Process button
    if st.button("Generate & Execute Solution", type="primary"):
        response = process_problem_input(
            vision_agent, coding_agent, uploaded_image, user_query
        )

        if response:
            display_solution_and_execute(response, execution_agent)


if __name__ == "__main__":
    main()
