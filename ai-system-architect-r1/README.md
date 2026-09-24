# AI System Architect Advisor with R1

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

An intelligent system architecture advisor powered by DeepSeek R1's reasoning capabilities and Claude 3.5 Sonnet's synthesis abilities. This Streamlit application provides expert-level architecture analysis, implementation strategies, and technical recommendations for complex software systems.

## Description

The AI System Architect Advisor combines DeepSeek R1's advanced reasoning with Claude's comprehensive analysis to provide detailed architecture guidance. It analyzes project requirements, generates architectural recommendations, identifies infrastructure needs, assesses security measures, and creates implementation roadmaps.

## Features

- **Dual AI Model Architecture**
  - DeepSeek R1: Advanced reasoning about architecture decisions
  - Claude 3.5: Detailed synthesis and technical specifications

- **Comprehensive Analysis**
  - Architecture pattern selection (microservices, monolithic, serverless, event-driven)
  - Infrastructure planning and resource estimation
  - Security measures and compliance frameworks
  - Database architecture decisions
  - Performance requirement analysis
  - Risk assessment and mitigation strategies

- **Structured Output**
  - JSON-formatted technical analysis
  - Clear reasoning explanations
  - Mermaid diagram descriptions
  - Implementation roadmaps
  - Cost estimations

- **Interactive Chat Interface**
  - Multi-turn conversation support
  - Chat history persistence
  - Clear reasoning visibility
  - Real-time analysis updates

## Architecture

```
User Query
    ↓
┌──────────────────────────────┐
│  DeepSeek R1 Reasoning       │
│  - Architecture analysis     │
│  - Pattern selection         │
│  - Cost estimation           │
└────────────┬─────────────────┘
             ↓
┌──────────────────────────────┐
│  Claude 3.5 Synthesis        │
│  - Technical specifications  │
│  - Implementation roadmap    │
│  - Detailed explanations     │
└────────────┬─────────────────┘
             ↓
        Chat Response
```

## Prerequisites

- Python 3.8 or higher
- DeepSeek API key
- Anthropic API key (Claude)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rchhabra13/ai_system_architect_r1.git
cd ai_system_architect_r1
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
DEEPSEEK_API_KEY=your_deepseek_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run ai_system_architect_r1.py
```

2. Open your browser to `http://localhost:8501`

3. Enter your API keys in the sidebar

4. Structure your architecture query with:
   - Project context
   - Requirements
   - Constraints
   - Scale
   - Security/compliance needs

5. Submit your query and view the analysis

## API Configuration

### DeepSeek API
- Visit: https://deepseek.com
- Create an API key
- Provides R1 reasoning model

### Anthropic API
- Visit: https://console.anthropic.com
- Create an API key
- Provides Claude 3.5 Sonnet model

## Output Sections

**DeepSeek Reasoning**:
- Detailed thought process for architectural decisions
- Pattern justification
- Trade-off analysis

**Technical Analysis**:
- JSON-formatted architectural decisions
- Infrastructure specifications
- Security measures
- Database recommendations
- Performance metrics

**Claude's Response**:
- Implementation roadmap
- Detailed technical specifications
- Cost breakdowns
- Risk mitigation strategies
- Clear explanations of design choices

## Example Prompts

### Financial Trading Platform
"Design a high-frequency trading platform that processes market data streams with sub-millisecond latency, maintains audit trails, handles 100,000 transactions per second, and has robust disaster recovery."

### Multi-tenant SaaS
"Design a multi-tenant SaaS platform supporting customization per tenant, different data residency requirements, offline capabilities, and performance isolation for 10,000 concurrent users."

### Healthcare System
"Build a healthcare data management system for patient records and appointments, scaling to 10,000 users, HIPAA compliant, with $50k budget constraint and existing hospital system integration."

## Technologies Used

- **DeepSeek R1**: Advanced reasoning model
- **Claude 3.5 Sonnet**: Language model for synthesis
- **Streamlit**: Web application framework
- **Agno**: AI agent framework
- **Pydantic**: Data validation
- **Python 3.8+**: Core language

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

- [ ] Architecture visualization diagrams
- [ ] Cost calculator refinement
- [ ] Database schema suggestions
- [ ] Security audit templates
- [ ] Implementation timeline generator
- [ ] Team skill requirement analysis
- [ ] Technology selection advisor
- [ ] Multi-project comparison tool
