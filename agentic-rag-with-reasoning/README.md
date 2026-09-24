# Agentic RAG with Reasoning

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A sophisticated Retrieval-Augmented Generation (RAG) system that demonstrates transparent reasoning processes. This application allows users to upload documents, add web sources, ask questions, and observe Claude's step-by-step reasoning in real-time.

## Description

The Agentic RAG with Reasoning combines Claude's advanced reasoning capabilities with OpenAI embeddings for semantic search and LanceDB for vector storage. It provides users with complete visibility into the AI's thinking process, showing how it retrieves information, reasons through queries, and generates answers with proper citations.

## Features

- **Interactive Knowledge Base Management**
  - Add URLs dynamically for web content
  - Persistent vector database storage using LanceDB
  - Real-time document loading and indexing

- **Transparent Reasoning Process**
  - Real-time display of the agent's thinking steps
  - Side-by-side view of reasoning and final answer
  - Clear visibility into the RAG process
  - Step-by-step analysis display

- **Advanced RAG Capabilities**
  - Vector search using OpenAI embeddings for semantic matching
  - Source attribution with citations
  - Multi-URL document processing
  - Reasoning tool integration

- **Professional Interface**
  - Streamlit web application
  - Responsive layout design
  - Real-time streaming updates
  - Clear information architecture

## Architecture

```
User Query
    ↓
┌─────────────────────────────────┐
│  OpenAI Embedder                │
│  - Convert query to embedding   │
│  - Generate vector              │
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│  LanceDB Vector Search          │
│  - Find similar documents       │
│  - Retrieve context chunks      │
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│  ReasoningTools                 │
│  - Analyze query                │
│  - Plan reasoning steps         │
│  - Structure analysis           │
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│  Claude with Extended Thinking  │
│  - Reason through context       │
│  - Generate comprehensive answer│
│  - Track sources                │
└─────────────────────────────────┘
```

## Prerequisites

- Python 3.8 or higher
- Anthropic API key (for Claude)
- OpenAI API key (for embeddings)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rchhabra13/agentic_rag_with_reasoning.git
cd agentic_rag_with_reasoning
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file:
```bash
touch .env
```

## Configuration

Create a `.env.example` file:

```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run rag_reasoning_agent.py
```

2. Open your browser to `http://localhost:8501`

3. Enter your API keys:
   - Anthropic API Key (for Claude)
   - OpenAI API Key (for embeddings)

4. Add knowledge sources:
   - Use the sidebar to add URLs to your knowledge base
   - System loads and embeds documents automatically

5. Ask questions:
   - Enter your query in the main input field
   - Click "Get Answer with Reasoning"
   - View reasoning process and answer side-by-side
   - Check sources in the Sources section

## How It Works

### Knowledge Base Setup
- Documents are loaded from URLs using UrlKnowledge
- Text is chunked and embedded using OpenAI's embedding model
- Vectors are stored in LanceDB for efficient retrieval
- Vector search enables semantic matching for relevant information

### Agent Processing
- User queries trigger the agent's reasoning process
- ReasoningTools help the agent think step-by-step
- The agent searches the knowledge base for relevant information
- Claude processes context and generates comprehensive answers with citations

### UI Flow
- Enter API keys → Add knowledge sources → Ask questions
- Reasoning process and answer generation displayed side-by-side
- Sources cited for transparency and verification

## Technologies Used

- **Agno**: Agent framework and orchestration
- **Claude Sonnet 4**: Language model for reasoning
- **OpenAI Embeddings**: Text-to-vector conversion
- **LanceDB**: Vector database
- **Streamlit**: Web interface
- **Python 3.8+**: Core language

## Output

**Reasoning Panel**: Shows Claude's step-by-step thinking process

**Answer Panel**: Final synthesized response to your question

**Sources Panel**: URLs and references used in generating the answer

## API Configuration

### Anthropic API
- Visit: https://console.anthropic.com
- Create API key
- Model: Claude Sonnet 4

### OpenAI API
- Visit: https://platform.openai.com
- Create API key
- Used for embedding generation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Rishi Chhabra ([@rchhabra13](https://github.com/rchhabra13))

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check Agno documentation
- Review Claude documentation
- Review OpenAI documentation

## Roadmap

- [ ] Document upload support
- [ ] Multi-language support
- [ ] Custom prompt templates
- [ ] Response quality metrics
- [ ] Conversation history
- [ ] Export reasoning traces
- [ ] Batch processing
- [ ] Performance analytics
