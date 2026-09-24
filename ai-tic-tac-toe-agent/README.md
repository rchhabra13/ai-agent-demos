# AI Tic Tac Toe Game

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

An interactive Tic-Tac-Toe game where two AI agents powered by different language models compete against each other. Built with the Agno Agent Framework and Streamlit, this application showcases real-time AI decision-making and game coordination.

## Description

The AI Tic Tac Toe Game demonstrates multi-agent coordination in a turn-based game scenario. Two independent AI agents play against each other, using different language models and strategies. Players can select from various AI models (GPT-4, Claude, Gemini, Groq) and watch the agents compete in real-time.

## Features

- **Multiple AI Model Support**
  - OpenAI: GPT-4o, o3-mini
  - Anthropic: Claude 3.5, Claude 3.7, Claude with extended thinking
  - Google: Gemini 2.0 Flash, Gemini 2.0 Pro
  - Groq: Llama 3.3

- **Real-time Game Visualization**
  - Live board display with updates
  - Move history tracking with board states
  - Current player indicator
  - Game status monitoring

- **Game Features**
  - Interactive player model selection
  - Start, pause, and reset game controls
  - Move validation and enforcement
  - Win detection and game conclusion
  - Move history with mini board visualizations

- **Professional UI**
  - Dark-themed interface
  - Responsive design
  - Clear move history display
  - Real-time updates
  - Player status indicators

## Architecture

```
┌─────────────────────────┐
│   Streamlit UI          │
│   - Game Display        │
│   - Controls            │
│   - Move History        │
└────────┬────────────────┘
         ↓
┌─────────────────────────┐
│   Game Coordinator      │
│   - State Management    │
│   - Move Validation     │
│   - Turn Control        │
└────────┬────────────────┘
         ↓
   ┌─────┴─────┐
   ↓           ↓
┌─────┐     ┌─────┐
│Agent│     │Agent│
│  X  │     │  O  │
└─────┘     └─────┘
  (Model1)   (Model2)
```

## Prerequisites

- Python 3.8 or higher
- At least one API key from: OpenAI, Anthropic, Google, or Groq

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rchhabra13/ai_tic_tac_toe_agent.git
cd ai_tic_tac_toe_agent
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

Create a `.env.example` file with your API keys:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_API_KEY=AIza_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser to `http://localhost:8501`

3. Enter your API keys in the sidebar (at least one required)

4. Select models for Player X and Player O

5. Click "Start Game" to begin

6. Watch the AI agents play:
   - Move history updates in real-time
   - Board state changes after each move
   - Game concludes when won or drawn

7. Use controls to:
   - Pause/Resume game
   - Start a new game
   - View complete move history

## Available Models

### OpenAI
- gpt-4o
- o3-mini

### Anthropic
- Claude 3.5 Sonnet
- Claude 3.7 Sonnet
- Claude 3.7 Sonnet (with extended thinking)

### Google
- Gemini 2.0 Flash
- Gemini 2.0 Pro

### Groq
- Llama 3.3 70B Versatile

## Game Rules

- 3x3 grid (positions from 0,0 to 2,2)
- Players alternate placing X and O
- First to get 3 marks in a row (horizontal, vertical, or diagonal) wins
- If all spaces filled with no winner, game is a draw

## Output

The application provides:

**Game Board**: Visual 3x3 grid showing current state

**Move History**: Chronological list of moves with:
- Move number
- Player and model used
- Position (row, col)
- Mini board snapshot

**Game Status**: Current phase (in progress, winner, draw)

## Technologies Used

- **Agno**: Multi-agent framework
- **Streamlit**: Web application interface
- **OpenAI, Anthropic, Google, Groq**: LLM providers
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

- [ ] Game statistics tracking
- [ ] Player rating system
- [ ] Tournament mode
- [ ] Strategy analysis
- [ ] Move explanation
- [ ] Game replay viewer
- [ ] Web deployment
