# Deep Research Agent - OpenAI Agents SDK & Firecrawl

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)

A powerful research assistant that leverages OpenAI's Agents SDK and Firecrawl's deep research capabilities to perform comprehensive web research on any topic and generate enhanced, elaborated reports with proper citations and insights.

## Overview

The Deep Research Agent combines cutting-edge AI capabilities with advanced web crawling to produce thorough research reports. It implements a two-stage process:

1. **Initial Research** - Uses Firecrawl to search multiple sources and synthesize findings
2. **Elaboration** - Enhances the initial report with deeper insights and context

## Features

- **Deep Web Research**: Automatically searches the web, extracts content, and synthesizes findings
- **Enhanced Analysis**: Uses OpenAI's Agents SDK to elaborate on research findings with additional context and insights
- **Interactive UI**: Clean Streamlit interface for easy interaction
- **Downloadable Reports**: Export research findings as markdown files
- **Real-time Progress**: Live updates showing research progress
- **Multi-source Coverage**: Gathers information from up to 10 different sources
- **Structured Output**: Well-organized reports with proper citations

## How It Works

1. **Input Phase**: User provides a research topic and API credentials
2. **Research Phase**: The tool uses Firecrawl to search the web and extract relevant information
3. **Analysis Phase**: Initial research report is generated based on findings
4. **Enhancement Phase**: Second agent elaborates on initial report, adding depth and context
5. **Output Phase**: Enhanced report is presented to user and available for download

## Tech Stack

- **Language**: [Python 3.10+](https://www.python.org/downloads/)
- **Research Framework**: [OpenAI Agents SDK](https://platform.openai.com/)
- **Web Crawling**: [Firecrawl](https://www.firecrawl.dev/)
- **UI**: [Streamlit](https://docs.streamlit.io/)
- **LLM**: [OpenAI GPT-4](https://platform.openai.com/)

## Prerequisites

- Python 3.10 or higher
- OpenAI API key (GPT-4 access required)
- Firecrawl API key

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rchhabra13/ai_deep_research_agent.git
   cd ai_deep_research_agent
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

4. **Configure API keys**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Usage

1. **Start the application**
   ```bash
   streamlit run deep_research_openai.py
   ```

2. **Configure API Keys** (in the sidebar)
   - Enter your OpenAI API key
   - Enter your Firecrawl API key

3. **Enter Research Topic**
   - Type your research topic in the input field
   - Click "Start Research"

4. **View Results**
   - Initial research report appears in an expandable section
   - Enhanced report is displayed in the main area
   - Download button allows saving the report as markdown

## Configuration

### Environment Variables (.env)

```bash
OPENAI_API_KEY=your_openai_api_key_here
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

### Research Parameters

The following parameters control the research depth (configurable in `deep_research` function):

- **max_depth**: 3 (research iteration depth)
- **time_limit**: 180 seconds (3 minutes)
- **max_urls**: 10 (number of sources to research)

## Project Structure

```
ai_deep_research_agent/
├── deep_research_openai.py    # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore patterns
└── README.md                  # This file
```

## Example Research Topics

- "Latest developments in quantum computing"
- "Impact of climate change on marine ecosystems"
- "Advancements in renewable energy storage"
- "Ethical considerations in artificial intelligence"
- "Emerging trends in remote work technologies"
- "Applications of blockchain in healthcare"
- "Future of autonomous vehicles"
- "Developments in biotechnology and gene therapy"

## How the Agents Work

### Research Agent
- Uses Firecrawl's deep research endpoint to gather information
- Searches multiple websites and extracts relevant content
- Synthesizes findings into a coherent initial report
- Includes citations and source references

### Elaboration Agent
- Analyzes the initial research report
- Adds detailed explanations and context
- Provides real-world examples and case studies
- Identifies trends and future implications
- Maintains academic rigor and factual accuracy

## API Costs

### OpenAI
- GPT-4 API calls incur standard usage costs
- Check [pricing](https://openai.com/pricing) for current rates

### Firecrawl
- Deep research endpoint has specific pricing
- Check [Firecrawl pricing](https://www.firecrawl.dev/pricing) for details

## Troubleshooting

### "API keys not configured"
- Ensure both API keys are entered in the sidebar
- Check that keys are valid and have appropriate permissions

### "Research taking too long"
- Firecrawl's deep research can take several minutes
- Check your internet connection
- Verify Firecrawl API status

### "Empty research results"
- Try a different research topic
- Use more specific or detailed query terms
- Check Firecrawl API logs for errors

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For questions and support:
- Create an issue on [GitHub](https://github.com/rchhabra13/ai_deep_research_agent/issues)
- Check [OpenAI documentation](https://platform.openai.com/docs)
- Review [Firecrawl documentation](https://www.firecrawl.dev/docs)

## Author

[Rishi Chhabra](https://github.com/rchhabra13)

---

Built with OpenAI Agents SDK and Firecrawl
