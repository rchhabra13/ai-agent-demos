# AI Finance Agent Team - Web + Finance

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)

A sophisticated multi-agent system that combines web search capabilities with real-time financial data analysis. This system demonstrates how to build a team of specialized AI agents that work together as a comprehensive financial analyst using Agno and GPT-4o in just a few lines of Python code.

## Overview

The Finance Agent Team implements a collaborative approach to financial analysis by combining:

- **Web Agent** - General internet research using DuckDuckGo
- **Finance Agent** - Real-time financial data and analysis using YFinance
- **Team Coordinator** - Orchestrates collaboration between specialized agents

This multi-agent architecture allows for comprehensive financial insights by leveraging both broad web knowledge and specific financial metrics.

## Features

### Multi-Agent System
- **Web Agent**: General internet research and information gathering
- **Finance Agent**: Real-time financial data, analyst recommendations, and company information
- **Team Coordinator**: Orchestrates between agents for comprehensive analysis
- **Persistent Memory**: Uses SQLite to store conversation history

### Financial Capabilities
- Real-time stock price data
- Analyst recommendations and ratings
- Company information and profiles
- Company news and press releases
- Web search for additional context and analysis

### User Interface
- Agno Playground interface for interactive conversations
- Real-time agent collaboration visualization
- Persistent conversation history
- Tool call transparency

## Tech Stack

- **Language**: [Python 3.10+](https://www.python.org/downloads/)
- **Agent Framework**: [Agno](https://agno.ai/)
- **LLM**: [OpenAI GPT-4o](https://platform.openai.com/)
- **Financial Data**: [YFinance](https://github.com/ranaroussi/yfinance)
- **Web Search**: [DuckDuckGo](https://duckduckgo.com/)
- **Storage**: [SQLite](https://www.sqlite.org/)
- **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/)

## Prerequisites

- Python 3.10 or higher
- OpenAI API key with GPT-4o access

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rchhabra13/ai_finance_agent_team.git
   cd ai_finance_agent_team
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your OpenAI API key**
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

## Usage

1. **Run the application**
   ```bash
   python finance_agent_team.py
   ```

2. **Open your browser**
   - Navigate to the URL provided in console (typically `http://localhost:8000`)
   - The Agno Playground interface will load

3. **Interact with the team**
   - Type your financial or research query
   - Agents will collaborate to provide comprehensive analysis
   - View conversation history and agent interactions

## Configuration

### Environment Variables

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
```

### Model Configuration

To use a different OpenAI model, modify the `finance_agent_team.py`:

```python
model=OpenAIChat(id="gpt-4-turbo")  # Change to preferred model
```

## Project Structure

```
ai_finance_agent_team/
├── finance_agent_team.py      # Main agent team implementation
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore patterns
├── agents.db                  # SQLite database (created on first run)
└── README.md                  # This file
```

## Example Queries

### Stock Analysis
- "What's the current price of Apple stock and what do analysts think about it?"
- "Compare Tesla and Ford in terms of recent news and stock performance"
- "What information is available about Microsoft's latest quarterly earnings?"

### Financial Research
- "Find current interest rates and economic trends affecting the tech sector"
- "What are the latest developments in cryptocurrency and blockchain technology?"
- "Research the impact of recent Fed decisions on the stock market"

### Investment Guidance
- "What's happening with renewable energy stocks right now?"
- "Compare pharmaceutical companies by recent news and analyst recommendations"
- "Analyze the current state of the real estate market"

## How It Works

1. **User Input**: You provide a financial query or research topic
2. **Agent Coordination**: Team Coordinator determines which agents are needed
3. **Web Research**: Web Agent searches the internet for context and current information
4. **Financial Analysis**: Finance Agent gathers stock data, recommendations, and company info
5. **Synthesis**: Agents work together to provide comprehensive, well-sourced responses
6. **Response**: Results are displayed with proper citations and data tables

## API Costs

### OpenAI
- GPT-4o API calls incur standard usage costs
- See [OpenAI Pricing](https://openai.com/pricing) for details

### YFinance
- Free tier available
- No API key required

### DuckDuckGo
- Free web search
- No API key required

## Troubleshooting

### "No module named 'agno'"
```bash
pip install --upgrade agno
```

### "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY='your-key-here'
# Restart the application
```

### "Port 8000 already in use"
```bash
python finance_agent_team.py --port 8001
```

### "SQLite database locked"
- Close other instances of the application
- Delete `agents.db` to reset (will lose conversation history)

## Features in Detail

### Web Agent
- Performs DuckDuckGo searches
- Gathers information from various sources
- Provides context for financial analysis
- Finds news and articles

### Finance Agent
- Real-time stock prices via YFinance
- Analyst recommendations and ratings
- Company information and profiles
- Recent company news
- Always displays data in table format

### Data Display
- Tables for financial metrics
- Formatted text for readability
- Source citations for transparency
- Tool call logs for debugging

## Advanced Usage

### Custom Instructions
Modify agent instructions in `finance_agent_team.py`:

```python
finance_agent = Agent(
    instructions=[
        "Always use tables to display data",
        "Include 5-year historical data when available",
        "Focus on dividend-paying stocks"
    ]
)
```

### Conversation History
Conversation history is automatically saved in `agents.db`. Access it through the Playground UI.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For questions and support:
- Create an issue on [GitHub](https://github.com/rchhabra13/ai_finance_agent_team/issues)
- Check [Agno documentation](https://agno.ai/)
- Review [OpenAI API docs](https://platform.openai.com/docs)
- See [YFinance docs](https://yfinance.readthedocs.io/)

## Author

[Rishi Chhabra](https://github.com/rchhabra13)

---

Built with Agno, OpenAI GPT-4o, YFinance, and DuckDuckGo
