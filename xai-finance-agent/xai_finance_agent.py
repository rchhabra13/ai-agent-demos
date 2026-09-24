"""xAI Finance Agent for financial analysis and stock research.

This module creates a finance agent using Grok model that analyzes financial data,
stock prices, and provides investment insights with web research capabilities.
"""

from agno.agent import Agent
from agno.models.xai import xAI
from agno.playground import Playground, serve_playground_app
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools


def create_finance_agent() -> Agent:
    """Create and configure the finance agent.

    Returns:
        Agent: Configured finance agent with financial tools.
    """
    agent = Agent(
        name="xAI Finance Agent",
        model=xAI(id="grok-beta"),
        tools=[
            DuckDuckGoTools(),
            YFinanceTools(
                stock_price=True,
                analyst_recommendations=True,
                stock_fundamentals=True,
            ),
        ],
        instructions=[
            "Always use tables to display financial/numerical data.",
            "For text data use bullet points and short paragraphs.",
        ],
        show_tool_calls=True,
        markdown=True,
    )
    return agent


def main() -> None:
    """Main execution function."""
    agent = create_finance_agent()
    app = Playground(agents=[agent]).get_app()
    serve_playground_app("xai_finance_agent:app", reload=True)


if __name__ == "__main__":
    main()
