# Multimodal AI Agent

Analyze videos and images with advanced reasoning using Google's Gemini 2.0 model. Upload media content and ask questions to get comprehensive AI-powered analysis combined with real-time research.

Two Streamlit applications included:
- `multimodal_agent.py`: Video analysis with web research integration
- `multimodal_reasoning_agent.py`: Image-based reasoning with extended thinking

## Features

- **Video & Image Analysis**: Understand visual content with Gemini 2.0 Flash
- **Web Integration**: Combine visual analysis with real-time web research
- **Multimodal Understanding**: Process multiple media types seamlessly
- **Interactive Interface**: User-friendly Streamlit web interface
- **Extended Reasoning**: Deep analysis using extended thinking capabilities
- **Multi-Format Support**: MP4, MOV, AVI for video; JPG, PNG for images

## Quick Start

```bash
git clone https://github.com/rchhabra13/multimodal_ai_agent.git
cd multimodal_ai_agent
pip install -r requirements.txt

# For video analysis with web research:
streamlit run multimodal_agent.py

# For image-based reasoning:
streamlit run multimodal_reasoning_agent.py
```

Access the app at `http://localhost:8501`.

## Configuration

| Component | Default | Notes |
|-----------|---------|-------|
| Video Model | gemini-2.0-flash | Optimized for video analysis |
| Image Model | gemini-2.0-flash-thinking-exp-1219 | Extended reasoning capabilities |
| Max Upload | Streamlit default | Check your connection speed |
| Supported Formats | MP4, MOV, AVI, JPG, PNG | Standard media formats |

## Tech Stack

Python, Streamlit, Google Gemini 2.0, Agno Framework

## License

MIT

**Credit**: Rishi Chhabra (rchhabra13)
