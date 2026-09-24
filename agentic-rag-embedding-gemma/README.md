# Agentic RAG with EmbeddingGemma

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A 100% local Retrieval-Augmented Generation (RAG) system using Google's EmbeddingGemma for vector embeddings and Llama 3.2 for text generation. All components run locally via Ollama, requiring no external API calls.

## Description

The Agentic RAG with EmbeddingGemma demonstrates a completely local AI system for document-based question answering. It combines EmbeddingGemma for semantic search, LanceDB for vector storage, and Llama 3.2 for context-aware response generation, all orchestrated through the Agno framework.

## Features

- **100% Local Operation**
  - No external API calls required
  - Complete data privacy
  - Offline capability
  - Lower operational costs

- **Advanced Retrieval**
  - Vector embeddings via EmbeddingGemma
  - Semantic similarity search
  - LanceDB vector storage
  - Efficient PDF parsing

- **Intelligent Generation**
  - Llama 3.2 language model
  - Context-aware responses
  - Multi-document reasoning
  - Clear structured output

- **Interactive Interface**
  - Streamlit web application
  - Dynamic knowledge base management
  - Real-time answer generation
  - Professional UI

## Architecture

```
PDF URLs
    ↓
┌─────────────────────────────┐
│  PDFUrlKnowledgeBase        │
│  - Parse documents          │
│  - Split into chunks        │
└────────────┬────────────────┘
             ↓
┌─────────────────────────────┐
│  EmbeddingGemma             │
│  - Create embeddings        │
│  - Generate vectors         │
└────────────┬────────────────┘
             ↓
┌─────────────────────────────┐
│  LanceDB Vector Database    │
│  - Store embeddings         │
│  - Index vectors            │
└────────────┬────────────────┘
             ↓
         User Query
             ↓
┌─────────────────────────────┐
│  Vector Search              │
│  - Embed query              │
│  - Find similar chunks      │
└────────────┬────────────────┘
             ↓
┌─────────────────────────────┐
│  Llama 3.2                  │
│  - Generate answer          │
│  - Use retrieved context    │
└─────────────────────────────┘
```

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running
- Required models:
  - `embeddinggemma:latest`
  - `llama3.2:latest`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rchhabra13/agentic_rag_embedding_gemma.git
cd agentic_rag_embedding_gemma
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install and setup Ollama:
```bash
# Download from https://ollama.com
ollama pull embeddinggemma:latest
ollama pull llama3.2:latest
```

4. Create a `.env` file (optional):
```bash
touch .env
```

## Configuration

Create a `.env.example` file (optional for local-only setup):

```
OLLAMA_HOST=http://localhost:11434
```

## Usage

1. Ensure Ollama is running:
```bash
ollama serve
```

2. In another terminal, start the Streamlit app:
```bash
streamlit run agentic_rag_embeddinggemma.py
```

3. Open your browser to `http://localhost:8501`

4. Add PDF URLs in the sidebar:
   - Enter PDF URL
   - Click "Add URL"
   - Wait for document loading and embedding

5. Ask questions about your documents:
   - Enter your query
   - Click "Get Answer"
   - View streamed response

## Example PDF Sources

- Academic papers (arXiv, ResearchGate)
- Technical documentation
- Business reports
- Training materials
- Research publications

## How It Works

1. **PDF Loading**: PDFUrlKnowledgeBase fetches and parses PDF content from URLs
2. **Chunking**: Documents are split into manageable chunks for embedding
3. **Embedding**: EmbeddingGemma converts text chunks into 768-dimensional vectors
4. **Storage**: Vectors are stored in LanceDB with original text
5. **Query Processing**: User queries are embedded using the same model
6. **Retrieval**: LanceDB performs vector similarity search to find relevant chunks
7. **Generation**: Llama 3.2 generates contextual answers using retrieved chunks
8. **Streaming**: Responses are streamed to UI in real-time

## Technologies Used

- **Agno**: Agent framework for orchestration
- **Ollama**: Local LLM server
- **EmbeddingGemma**: Google's embedding model
- **Llama 3.2**: Meta's language model
- **LanceDB**: Vector database
- **Streamlit**: Web interface
- **Python 3.8+**: Core language

## Performance Notes

- Initial embedding: 1-5 minutes depending on PDF size
- Query response: 5-30 seconds depending on query complexity
- Vector search: <1 second typically
- No network latency for inference

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Rishi Chhabra ([@rchhabra13](https://github.com/rchhabra13))

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check Ollama documentation
- Review Agno documentation
- Review LanceDB documentation

## Roadmap

- [ ] Multiple PDF support UI
- [ ] Document metadata display
- [ ] Citation tracking
- [ ] Conversation history
- [ ] Document upload support
- [ ] Response quality metrics
- [ ] Model selection UI
- [ ] Batch processing
