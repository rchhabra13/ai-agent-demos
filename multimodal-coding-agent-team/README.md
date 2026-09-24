# Multimodal AI Coding Agent Team

Multi-agent system for solving coding problems through image analysis, code generation, and secure sandboxed execution. Combines OpenAI's o3-mini with Google Gemini for comprehensive problem-solving with real-time code execution.

## Features

- **Multi-Modal Input**: Upload images or describe coding problems in text
- **Vision-Based Problem Extraction**: Automatic extraction of problems from screenshots, whiteboards, or diagrams
- **Optimal Code Generation**: AI-powered solutions with best time/space complexity
- **Secure Execution**: Sandboxed E2B environment with 30-second timeout protection
- **Multi-Agent Architecture**: Specialized agents for vision analysis, coding, and execution
- **Real-time Feedback**: Instant results with comprehensive error handling

## Quick Start

```bash
git clone https://github.com/rchhabra13/multimodal_coding_agent_team.git
cd multimodal_coding_agent_team
pip install -r requirements.txt
streamlit run ai_coding_agent_o3.py
```

Access at `http://localhost:8501`. Enter API keys in sidebar to start.

## Configuration

| Component | API Key | Purpose |
|-----------|---------|---------|
| Code Generation | OpenAI | o3-mini model |
| Image Analysis | Google | Gemini 2.0 Flash |
| Execution | E2B | Secure sandbox environment |
| Timeout | Fixed | 30 seconds per execution |

## Tech Stack

Python, Streamlit, OpenAI o3-mini, Google Gemini 2.0, E2B Sandbox, Agno Framework

## License

MIT

**Credit**: Rishi Chhabra (rchhabra13)
