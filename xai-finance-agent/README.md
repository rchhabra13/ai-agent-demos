# xAI Finance Agent

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Financial analysis agent powered by xAI's Grok model. Combines real-time stock data from Yahoo Finance with DuckDuckGo web search to deliver market analysis, company fundamentals, and analyst recommendations through Agno's interactive playground.

## Features

- **Real-time stock data** — prices, fundamentals, analyst recommendations via YFinance
- **Web research** — DuckDuckGo integration for news and market context
- **Interactive playground** — Agno's built-in chat UI at localhost:7777
- **Formatted output** — tables for financial data, bullet points for text

## Quick Start

```bash
git clone https://github.com/rchhabra13/xai-finance-agent.git
cd xai-finance-agent
pip install -r requirements.txt
cp .env.example .env  # Add your xAI API key
python xai_finance_agent.py
```

Open `http://localhost:7777` to interact with the agent.

## Configuration

| Variable | Description |
|----------|-------------|
| `XAI_API_KEY` | xAI API key for Grok model access |

## Tech Stack

Python, Agno, xAI Grok, YFinance, DuckDuckGo, FastAPI

## License

MIT
