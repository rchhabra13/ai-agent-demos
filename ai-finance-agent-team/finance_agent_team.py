"""
Multi-agent finance team using Agno with web search and YFinance.

This module implements a collaborative team of AI agents specializing in web
search and financial analysis to provide comprehensive financial insights.
"""

import logging

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from agno.playground import Playground, serve_playground_app

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize Web Agent
web_agent = Agent(
    name="Web Agent",
    role="Search the web for information",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    storage=SqliteAgentStorage(table_name="web_agent", db_file="agents.db"),
    add_history_to_messages=True,
    markdown=True,
)

# Initialize Finance Agent
finance_agent = Agent(
    name="Finance Agent",
    role="Get financial data",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YFinanceTools(
        stock_price=True,
        analyst_recommendations=True,
        company_info=True,
        company_news=True
    )],
    instructions=["Always use tables to display data"],
    storage=SqliteAgentStorage(table_name="finance_agent", db_file="agents.db"),
    add_history_to_messages=True,
    markdown=True,
)

# Initialize Agent Team
agent_team = Agent(
    team=[web_agent, finance_agent],
    name="Agent Team (Web+Finance)",
    model=OpenAIChat(id="gpt-4o"),
    show_tool_calls=True,
    markdown=True,
)

# Create Playground app
app = Playground(agents=[agent_team]).get_app()


if __name__ == "__main__":
    serve_playground_app("finance_agent_team:app", reload=True)
