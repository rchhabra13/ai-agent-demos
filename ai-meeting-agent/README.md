# AI Meeting Preparation Agent

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A comprehensive AI-powered meeting preparation system leveraging CrewAI and Claude to analyze company context, research industry trends, develop meeting strategies, and create executive briefings.

## Description

The AI Meeting Preparation Agent is a multi-agent system that automates comprehensive meeting preparation. It coordinates specialized AI agents to handle context analysis, industry research, strategy development, and executive briefing creation, significantly reducing preparation time while improving meeting effectiveness.

## Features

- **Multi-Agent Coordination**: Four specialized agents working collaboratively
- **Context Analysis**: Deep analysis of company background and meeting context
- **Industry Research**: Real-time market and competitor intelligence
- **Strategy Development**: Customized meeting agendas and talking points
- **Executive Briefings**: Comprehensive pre-meeting preparation packages
- **Real-time Progress Tracking**: Visual feedback on agent activities
- **Markdown Formatting**: Well-structured, professional output

## Architecture

```
User Input (Meeting Details)
        ↓
    ┌───────────────────────────┐
    │  Context Analyzer Agent   │ (Research company background)
    └───────────┬───────────────┘
                ↓
    ┌───────────────────────────┐
    │  Industry Expert Agent    │ (Analyze market trends)
    └───────────┬───────────────┘
                ↓
    ┌───────────────────────────┐
    │  Meeting Strategist Agent │ (Develop strategy & agenda)
    └───────────┬───────────────┘
                ↓
    ┌──────────────────────────┐
    │ Communication Specialist │ (Create executive brief)
    └──────────┬───────────────┘
               ↓
         Output (Brief)
```

## Prerequisites

- Python 3.8 or higher
- Anthropic API key (Claude)
- Serper API key (web search)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rchhabra13/ai_meeting_agent.git
cd ai_meeting_agent
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

Create a `.env.example` file in the root directory:

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run meeting_agent.py
```

2. Open your browser to `http://localhost:8501`

3. Enter your API keys in the sidebar

4. Provide meeting details:
   - Company name
   - Meeting objective
   - Attendees and their roles
   - Meeting duration
   - Specific focus areas

5. Click "Prepare Meeting" to generate comprehensive materials

## API Configuration

### Anthropic API
- Visit: https://console.anthropic.com
- Create an API key
- Add to `.env` as `ANTHROPIC_API_KEY`

### Serper API
- Visit: https://serper.dev
- Sign up and create an API key
- Add to `.env` as `SERPER_API_KEY`

## Output

The system generates:

- **Executive Summary**: High-level meeting overview with objectives and key attendees
- **Company Analysis**: Recent news, products, competitors, and market position
- **Industry Insights**: Market trends, competitive landscape, opportunities and threats
- **Meeting Strategy**: Time-boxed agenda with talking points and speaker assignments
- **Q&A Preparation**: Anticipated questions with strategic responses
- **Next Steps**: Actionable recommendations and implementation timeline

## Technologies Used

- **CrewAI**: Multi-agent orchestration framework
- **Claude 3.5 Sonnet**: Language model for analysis and synthesis
- **Serper API**: Real-time web search capability
- **Streamlit**: Web application interface
- **Python 3.8+**: Core programming language

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Rishi Chhabra ([@rchhabra13](https://github.com/rchhabra13))

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review usage examples

## Roadmap

- [ ] Meeting outcome tracking
- [ ] Historical meeting analysis
- [ ] Participant briefing materials
- [ ] Post-meeting analysis and follow-up generation
- [ ] Multi-language support
- [ ] Calendar integration
- [ ] Video conferencing integration
