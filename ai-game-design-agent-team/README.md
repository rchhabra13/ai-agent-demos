# AI Game Design Agent Team - AutoGen Swarm

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)

A sophisticated multi-agent system that collaboratively designs video games using AutoGen's SwarmAgent architecture. Features specialized agents for story, gameplay, visuals, and technical design that work together through coordinated hand-offs to create comprehensive game concepts.

## Overview

The Game Design Agent Team uses AutoGen SwarmAgent to orchestrate four specialized agents:

- **Story Agent** - Narrative design and world-building
- **Gameplay Agent** - Mechanics design and player systems
- **Visuals Agent** - Art direction and audio design
- **Tech Agent** - Technical requirements and architecture

Each agent contributes expertise in sequence, building on the previous agent's output.

## Features

- **Multi-Agent Swarm Coordination**: Four specialized design agents with automatic handoffs
- **Comprehensive Game Concept**: Story, gameplay, visuals, and technical sections
- **Flexible Game Types**: RPG, Action, Adventure, Puzzle, Strategy, Simulation, Platform, Horror
- **Target Audience Support**: Kids through adults with age-appropriate design
- **Budget & Timeline Constraints**: Considers practical development considerations
- **Interactive UI**: Streamlit interface for easy input and viewing results
- **Expandable Output**: View each agent's contribution separately

## Tech Stack

- **Language**: [Python 3.10+](https://www.python.org/downloads/)
- **Agent Framework**: [AutoGen](https://microsoft.github.io/autogen/)
- **LLM**: [OpenAI GPT-4o-mini](https://platform.openai.com/)
- **UI**: [Streamlit](https://docs.streamlit.io/)

## Prerequisites

- Python 3.10 or higher
- OpenAI API key with GPT-4 access

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rchhabra13/ai_game_design_agent_team.git
   cd ai_game_design_agent_team
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set API key**
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

## Usage

1. **Start application**
   ```bash
   streamlit run game_design_agent_team.py
   ```

2. **Enter API Key** (sidebar)
   - Paste your OpenAI API key

3. **Design Your Game**
   - Background vibe/setting
   - Game type (RPG, Action, etc.)
   - Target audience
   - Art style and platforms
   - Core mechanics and mood
   - Unique features

4. **Generate Concept**
   - Click "Generate Game Concept"
   - Wait for agent collaboration
   - View expandable sections for each agent's work

## Configuration

### Supported Game Types
- RPG
- Action
- Adventure
- Puzzle
- Strategy
- Simulation
- Platform
- Horror

### Supported Platforms
- PC
- Mobile
- PlayStation
- Xbox
- Nintendo Switch
- Web Browser

### Art Styles
- Realistic
- Cartoon
- Pixel Art
- Stylized
- Low Poly
- Anime
- Hand-drawn

## Project Structure

```
ai_game_design_agent_team/
├── game_design_agent_team.py  # Main application
├── requirements.txt            # Dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore patterns
└── README.md                  # This file
```

## Agent Responsibilities

### Story Agent
- Narrative and character design
- World-building and lore
- Story progression and plot points
- Dialogue and character arcs
- Mood and atmosphere integration

### Gameplay Agent
- Core gameplay loops
- Progression systems
- Control schemes and player interactions
- Difficulty balancing
- Game modes and multiplayer design

### Visuals Agent
- Visual style guides
- Character and environment aesthetics
- Visual effects and animations
- Audio direction and music style
- Platform-specific optimization

### Tech Agent
- Game engine recommendations
- Technical platform requirements
- Development pipeline planning
- Performance optimization strategies
- Team and resource requirements

## Example Game Concepts

### Epic Fantasy RPG
- Vibe: Epic fantasy with dragons
- Type: RPG
- Platforms: PC, PlayStation, Xbox
- Development: 24 months, $500K budget

### Indie Puzzle Adventure
- Vibe: Mysterious and atmospheric
- Type: Puzzle
- Platform: Web, Mobile
- Development: 6 months, $50K budget

### Mobile Casual Game
- Vibe: Whimsical and fun
- Type: Platform
- Platforms: Mobile
- Development: 3 months, $10K budget

## How It Works

1. **Setup**: User provides game specifications
2. **Agent 1**: Story agent creates narrative foundation
3. **Handoff**: Passes to gameplay agent
4. **Agent 2**: Gameplay agent designs mechanics
5. **Handoff**: Passes to visuals agent
6. **Agent 3**: Visuals agent designs art direction
7. **Handoff**: Passes to tech agent
8. **Agent 4**: Tech agent provides technical specs
9. **Completion**: All contributions compiled and displayed

## Customization

### Modify Agent Prompts
Edit system messages in `game_design_agent_team.py`:

```python
system_messages = {
    "story_agent": "Your custom prompt here..."
}
```

### Change Model
Modify LLM configuration:

```python
llm_config = {"config_list": [{"model": "gpt-4-turbo"}]}
```

## Troubleshooting

### "API key not provided"
- Paste OpenAI API key in sidebar
- Ensure key has GPT-4 access

### Agents not responding
- Check internet connection
- Verify API key validity
- Check OpenAI account status/credits

### Output truncated
- Full output stored in session state
- Export concept to file for complete text

## Performance

Typical generation time: 3-5 minutes depending on:
- Model complexity
- Detail level selected
- API response times
- Network conditions

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Submit Pull Requests.

## Support

- [GitHub Issues](https://github.com/rchhabra13/ai_game_design_agent_team/issues)
- [AutoGen Docs](https://microsoft.github.io/autogen/)
- [OpenAI API Docs](https://platform.openai.com/docs)

## Author

[Rishi Chhabra](https://github.com/rchhabra13)

---

Built with AutoGen and OpenAI GPT-4o-mini
