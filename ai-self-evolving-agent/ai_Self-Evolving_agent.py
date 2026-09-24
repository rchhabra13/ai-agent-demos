"""
AI Self-Evolving Agent using EvoAgentX.

This module implements a self-evolving agent that automatically learns,
adapts, and improves through workflow generation and code evolution.
"""

import logging
import os
from typing import Optional

from dotenv import load_dotenv
from evoagentx.actions.code_extraction import CodeExtraction
from evoagentx.actions.code_verification import CodeVerification
from evoagentx.agents import AgentManager
from evoagentx.core.module_utils import extract_code_blocks
from evoagentx.models import LiteLLMConfig, LiteLLM, OpenAILLMConfig, OpenAILLM
from evoagentx.workflow import WorkFlow, WorkFlowGenerator, WorkFlowGraph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")


def main() -> None:
    """
    Main function demonstrating self-evolving agent capabilities.

    Generates a workflow for creating Tetris game HTML code,
    executes it, verifies the output, and extracts code files.
    """
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY environment variable not set")
        raise ValueError("OPENAI_API_KEY environment variable required")

    if not ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY environment variable not set")
        raise ValueError("ANTHROPIC_API_KEY environment variable required")

    # LLM configuration for workflow generation
    logger.info("Configuring OpenAI LLM for workflow generation")
    openai_config = OpenAILLMConfig(
        model="gpt-4o-mini",
        openai_key=OPENAI_API_KEY,
        stream=True,
        output_response=True,
        max_tokens=16000
    )

    # Initialize the language model
    llm = OpenAILLM(config=openai_config)

    goal = "Generate html code for the Tetris game that can be played in the browser."
    target_directory = "examples/output/tetris_game"

    logger.info(f"Starting workflow generation for goal: {goal}")

    # Generate workflow from goal
    wf_generator = WorkFlowGenerator(llm=llm)
    workflow_graph: WorkFlowGraph = wf_generator.generate_workflow(goal=goal)

    # Display and optionally save workflow
    workflow_graph.display()

    logger.info(f"Workflow generated with {len(workflow_graph.nodes)} nodes")

    # Create agent manager and add agents from workflow
    agent_manager = AgentManager()
    agent_manager.add_agents_from_workflow(
        workflow_graph,
        llm_config=openai_config
    )

    # Create and execute workflow
    logger.info("Creating and executing workflow")
    workflow = WorkFlow(
        graph=workflow_graph,
        agent_manager=agent_manager,
        llm=llm
    )

    output = workflow.execute()
    logger.info("Workflow execution completed")

    # Verify the code using Claude
    logger.info("Configuring Claude for code verification")
    verification_llm_config = LiteLLMConfig(
        model="anthropic/claude-3-7-sonnet-20250219",
        anthropic_key=ANTHROPIC_API_KEY,
        stream=True,
        output_response=True,
        max_tokens=20000
    )

    verification_llm = LiteLLM(config=verification_llm_config)

    logger.info("Verifying generated code")
    code_verifier = CodeVerification()
    output = code_verifier.execute(
        llm=verification_llm,
        inputs={
            "requirements": goal,
            "code": output
        }
    ).verified_code

    logger.info("Code verification completed")

    # Extract and save code
    logger.info(f"Extracting code to {target_directory}")
    os.makedirs(target_directory, exist_ok=True)

    code_blocks = extract_code_blocks(output)

    if len(code_blocks) == 1:
        file_path = os.path.join(target_directory, "index.html")
        with open(file_path, "w") as f:
            f.write(code_blocks[0])
        logger.info(f"Saved single code block to {file_path}")
        print(f"You can open this HTML file in a browser to play Tetris: {file_path}")
        return

    code_extractor = CodeExtraction()
    results = code_extractor.execute(
        llm=llm,
        inputs={
            "code_string": output,
            "target_directory": target_directory,
        }
    )

    logger.info(f"Extracted {len(results.extracted_files)} files")
    print(f"Extracted {len(results.extracted_files)} files:")
    for filename, path in results.extracted_files.items():
        print(f"  - {filename}: {path}")
        logger.info(f"Extracted file: {filename} -> {path}")

    if results.main_file:
        print(f"\nMain file: {results.main_file}")
        logger.info(f"Main file identified: {results.main_file}")

        file_type = os.path.splitext(results.main_file)[1].lower()
        if file_type == ".html":
            print("You can open this HTML file in a browser to play Tetris")
        else:
            print("This is the main entry point for your application")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        raise
