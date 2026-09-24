"""
Tic Tac Toe Game Agents.

This module defines AI agents that play Tic Tac Toe against each other
using different language models.
"""

import logging
from pathlib import Path
from textwrap import dedent
from typing import Any, Tuple

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.models.google import Gemini
from agno.models.groq import Groq
from agno.models.openai import OpenAIChat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_model_for_provider(
    provider: str,
    model_name: str
) -> Any:
    """
    Create and return the appropriate model instance based on provider.

    Args:
        provider: The model provider (openai, google, anthropic, groq)
        model_name: The specific model name/ID

    Returns:
        An instance of the appropriate model class

    Raises:
        ValueError: If the provider is not supported
    """
    if provider == "openai":
        return OpenAIChat(id=model_name)
    elif provider == "google":
        return Gemini(id=model_name)
    elif provider == "anthropic":
        if model_name == "claude-3-5-sonnet":
            return Claude(id="claude-3-5-sonnet-20241022", max_tokens=8192)
        elif model_name == "claude-3-7-sonnet":
            return Claude(
                id="claude-3-7-sonnet-20250219",
                max_tokens=8192,
            )
        elif model_name == "claude-3-7-sonnet-thinking":
            return Claude(
                id="claude-3-7-sonnet-20250219",
                max_tokens=8192,
                thinking={"type": "enabled", "budget_tokens": 4096},
            )
        else:
            return Claude(id=model_name)
    elif provider == "groq":
        return Groq(id=model_name)
    else:
        raise ValueError(f"Unsupported model provider: {provider}")


def get_tic_tac_toe_players(
    model_x: str = "openai:gpt-4o",
    model_o: str = "openai:o3-mini",
    debug_mode: bool = True,
) -> Tuple[Agent, Agent]:
    """
    Create two Tic Tac Toe player agents.

    Args:
        model_x: Model config for player X (format: provider:model_name)
        model_o: Model config for player O (format: provider:model_name)
        debug_mode: Enable logging and debug features

    Returns:
        Tuple of (player_x_agent, player_o_agent)

    Raises:
        ValueError: If model configuration is invalid
    """
    try:
        provider_x, model_name_x = model_x.split(":")
        provider_o, model_name_o = model_o.split(":")
    except ValueError as e:
        logger.error(f"Invalid model configuration format: {e}")
        raise ValueError(
            "Model configuration must be in format 'provider:model_name'"
        ) from e

    logger.info(f"Creating player X agent with {provider_x}:{model_name_x}")
    logger.info(f"Creating player O agent with {provider_o}:{model_name_o}")

    model_x_instance = get_model_for_provider(provider_x, model_name_x)
    model_o_instance = get_model_for_provider(provider_o, model_name_o)

    player_x = Agent(
        name="Player X",
        description=dedent("""\
        You are Player X in a Tic Tac Toe game. Your goal is to win by placing \
three X's in a row (horizontally, vertically, or diagonally).

        BOARD LAYOUT:
        - The board is a 3x3 grid with coordinates from (0,0) to (2,2)
        - Top-left is (0,0), bottom-right is (2,2)

        RULES:
        - You can only place X in empty spaces (shown as " " on the board)
        - Players take turns placing their marks
        - First to get 3 marks in a row (horizontal, vertical, or diagonal) wins
        - If all spaces are filled with no winner, the game is a draw

        YOUR RESPONSE:
        - Provide ONLY two numbers separated by a space (row column)
        - Example: "1 2" places your X in row 1, column 2
        - Choose only from the valid moves list provided to you

        STRATEGY TIPS:
        - Study the board carefully and make strategic moves
        - Block your opponent's potential winning moves
        - Create opportunities for multiple winning paths
        - Pay attention to the valid moves and avoid illegal moves
        """),
        model=model_x_instance,
        debug_mode=debug_mode,
    )

    player_o = Agent(
        name="Player O",
        description=dedent("""\
        You are Player O in a Tic Tac Toe game. Your goal is to win by placing \
three O's in a row (horizontally, vertically, or diagonally).

        BOARD LAYOUT:
        - The board is a 3x3 grid with coordinates from (0,0) to (2,2)
        - Top-left is (0,0), bottom-right is (2,2)

        RULES:
        - You can only place O in empty spaces (shown as " " on the board)
        - Players take turns placing their marks
        - First to get 3 marks in a row (horizontal, vertical, or diagonal) wins
        - If all spaces are filled with no winner, the game is a draw

        YOUR RESPONSE:
        - Provide ONLY two numbers separated by a space (row column)
        - Example: "1 2" places your O in row 1, column 2
        - Choose only from the valid moves list provided to you

        STRATEGY TIPS:
        - Study the board carefully and make strategic moves
        - Block your opponent's potential winning moves
        - Create opportunities for multiple winning paths
        - Pay attention to the valid moves and avoid illegal moves
        """),
        model=model_o_instance,
        debug_mode=debug_mode,
    )

    logger.info("Successfully created player agents")
    return player_x, player_o
