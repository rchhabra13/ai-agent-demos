# AI Legal Agent Team

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)

A comprehensive legal document analysis application powered by multiple AI agents. This Streamlit application simulates a full-service legal team using specialized agents for research, contract analysis, and legal strategy to provide thorough legal analysis and recommendations.

## Overview

The AI Legal Agent Team uses three specialized agents coordinated by a team lead:

- **Legal Researcher** - Finds and cites relevant legal cases and precedents with web search
- **Contract Analyst** - Reviews contracts, identifies key terms and potential issues
- **Legal Strategist** - Develops comprehensive legal strategies and recommendations
- **Team Lead** - Coordinates analysis and ensures comprehensive, well-sourced responses

## Features

- **Multi-Agent Analysis**: Three specialized legal agents with team coordination
- **PDF Document Processing**: Upload and analyze legal documents
- **Vector Database Storage**: Uses Qdrant for intelligent document retrieval
- **Multiple Analysis Types**:
  - Contract Review
  - Legal Research
  - Risk Assessment
  - Compliance Check
  - Custom Queries
- **Web Research Integration**: DuckDuckGo search for legal cases and precedents
- **Detailed Output**: Analysis, key points, and recommendations in separate tabs
- **RAG Architecture**: Retrieval-augmented generation for document-aware responses

## Tech Stack

- **Language**: [Python 3.10+](https://www.python.org/downloads/)
- **Agent Framework**: [Agno](https://agno.ai/)
- **LLM**: [OpenAI GPT-4](https://platform.openai.com/)
- **Vector Database**: [Qdrant](https://qdrant.tech/)
- **Embeddings**: [OpenAI text-embedding-3-small](https://platform.openai.com/)
- **Web Search**: [DuckDuckGo](https://duckduckgo.com/)
- **UI**: [Streamlit](https://docs.streamlit.io/)
- **PDF Processing**: [PyPDF](https://github.com/py-pdf/pypdf)

## Prerequisites

- Python 3.10 or higher
- OpenAI API key (GPT-4 access required)
- Qdrant Cloud instance or local Qdrant server

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rchhabra13/ai_legal_agent_team.git
   cd ai_legal_agent_team
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API keys**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

## Usage

1. **Set up Qdrant**
   - Create free instance at [Qdrant Cloud](https://cloud.qdrant.io)
   - Or run locally: `docker run -p 6333:6333 qdrant/qdrant`

2. **Start application**
   ```bash
   streamlit run legal_agent_team.py
   ```

3. **Configure API Keys** (sidebar)
   - Enter OpenAI API key
   - Enter Qdrant API key
   - Enter Qdrant URL
   - Click "Successfully connected to Qdrant!"

4. **Upload Document**
   - Upload PDF legal document
   - System processes and embeds document

5. **Select Analysis Type**
   - Contract Review
   - Legal Research
   - Risk Assessment
   - Compliance Check
   - Custom Query

6. **View Results**
   - Analysis tab: Detailed analysis
   - Key Points tab: Summarized findings
   - Recommendations tab: Action items

## Configuration

### Environment Variables

```bash
OPENAI_API_KEY=your_openai_api_key_here
QDRANT_HOST=https://your-instance.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here
```

### Analysis Types

- **Contract Review**: Identifies key terms, obligations, and potential issues
- **Legal Research**: Researches relevant cases and precedents
- **Risk Assessment**: Analyzes legal risks and liabilities
- **Compliance Check**: Checks regulatory compliance
- **Custom Query**: Analyze with your specific questions

## Project Structure

```
ai_legal_agent_team/
├── legal_agent_team.py              # Main application
├── local_ai_legal_agent_team/       # Local variant (uses Ollama)
│   ├── local_legal_agent.py
│   └── requirements.txt
├── requirements.txt                 # Dependencies
├── .env.example                     # Environment template
├── .gitignore                       # Git ignore patterns
└── README.md                        # This file
```

## Local Setup (Using Ollama)

For running locally without cloud APIs:

1. **Install Ollama**
   ```bash
   # Download from https://ollama.ai
   ```

2. **Pull Llama 3.1 model**
   ```bash
   ollama pull llama3.1:8b
   ```

3. **Start Ollama**
   ```bash
   ollama serve
   ```

4. **Run local agent**
   ```bash
   cd local_ai_legal_agent_team
   pip install -r requirements.txt
   streamlit run local_legal_agent.py
   ```

## Agent Responsibilities

### Legal Researcher
- Uses DuckDuckGo for web search
- Finds relevant legal cases and precedents
- Provides detailed research summaries with sources
- References specific document sections

### Contract Analyst
- Reviews contracts thoroughly
- Identifies key terms and obligations
- Flags potential issues and red flags
- References specific clauses

### Legal Strategist
- Develops comprehensive legal strategies
- Provides actionable recommendations
- Considers risks and opportunities
- Suggests implementation approaches

### Team Lead
- Coordinates between specialists
- Ensures comprehensive responses
- Verifies proper sourcing
- Manages knowledge base searches

## Example Scenarios

### Contract Review
- Employment contracts
- Service agreements
- Purchase agreements
- Licensing agreements
- Non-disclosure agreements

### Legal Research
- Relevant case law
- Regulatory precedents
- Industry standards
- Compliance requirements

### Risk Assessment
- Liability identification
- Compliance risks
- Financial exposure
- Mitigation strategies

## Troubleshooting

### "Qdrant connection failed"
- Verify instance is running
- Check URL format: `https://instance-name.qdrant.io`
- Verify API key is correct

### "PDF processing error"
- Ensure PDF is readable text (not scanned image)
- File size should be reasonable (< 100MB)
- Check PDF format compatibility

### "No documents retrieved"
- Verify document was successfully uploaded
- Try different query terms
- Check Qdrant collection has documents

### "API rate limiting"
- Wait before next request
- Check OpenAI account quotas
- Consider upgrading API plan

## Performance

Typical analysis time: 30-60 seconds depending on:
- Document length
- Complexity of analysis
- API response times
- Network latency

## Data Privacy

- Documents processed locally first
- Embeddings stored in your Qdrant instance
- OpenAI processes queries (see their privacy policy)
- No permanent storage on third-party servers

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Submit Pull Requests.

## Support

- [GitHub Issues](https://github.com/rchhabra13/ai_legal_agent_team/issues)
- [Agno Documentation](https://agno.ai/)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Qdrant Docs](https://qdrant.tech/documentation/)

## Author

[Rishi Chhabra](https://github.com/rchhabra13)

---

**Legal Disclaimer**: This tool provides analysis assistance only. It is not a substitute for professional legal advice. Always consult with qualified attorneys before making legal decisions or taking legal action.

Built with Agno, OpenAI, and Qdrant
