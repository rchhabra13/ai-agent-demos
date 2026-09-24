# Web Scraping AI Agent

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Extract structured data from any website using natural language instructions. Describe what you want in plain English and the agent scrapes it using ScrapeGraphAI. Supports both OpenAI cloud models and local Ollama inference with Llama 3.2.

## Features

- **Natural language scraping** — describe what to extract, no CSS selectors needed
- **Two modes**: OpenAI (GPT-3.5/4) or local Ollama (Llama 3.2)
- **Streamlit UI** for interactive scraping sessions
- **Structured output** — returns clean, formatted data

## Quick Start

```bash
git clone https://github.com/rchhabra13/web-scraping-ai-agent.git
cd web-scraping-ai-agent
pip install -r requirements.txt
playwright install

# OpenAI mode
streamlit run ai_scrapper.py

# Local mode (requires Ollama with llama3.2)
streamlit run local_ai_scrapper.py
```

## Configuration

**OpenAI mode** — enter your API key in the sidebar and select a model (GPT-3.5 or GPT-4).

**Local mode** — requires [Ollama](https://ollama.ai) running locally with:
```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

## Tech Stack

Python, ScrapeGraphAI, Streamlit, OpenAI, Ollama, Playwright

## License

MIT
