# AI Self-Evolving Agent

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

An advanced AI agent system demonstrating self-evolution capabilities using EvoAgentX. This application automatically generates workflows, executes multi-agent systems, verifies code output, and learns from feedback to continuously improve its solutions.

## Description

The AI Self-Evolving Agent leverages EvoAgentX to create self-improving AI systems. It automatically generates optimal agent workflows from natural language goals, executes them with multiple AI models, verifies the generated code with Claude, and extracts structured outputs. This demonstrates the power of agentic automation in software development.

## Features

- **Automatic Workflow Generation**
  - Convert natural language goals to agent workflows
  - Dynamic agent instantiation
  - Optimized execution order

- **Multi-Agent Execution**
  - Parallel and sequential agent coordination
  - Task decomposition and delegation
  - Result aggregation and synthesis

- **Code Verification**
  - Automated code quality checks
  - Requirement validation
  - Output refinement with Claude

- **Intelligent Code Extraction**
  - Multi-file project generation
  - Main file identification
  - Structured output organization

- **Self-Improvement Capabilities**
  - Learn from execution results
  - Adapt strategies based on feedback
  - Optimize workflow structures

## Architecture

```
Natural Language Goal
        ↓
┌─────────────────────────────┐
│  WorkFlowGenerator          │
│  - Parse goal               │
│  - Create task graph        │
│  - Design agent structure   │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│  AgentManager               │
│  - Instantiate agents       │
│  - Assign models            │
│  - Configure tools          │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│  WorkFlow Execution         │
│  - Execute tasks            │
│  - Monitor progress         │
│  - Aggregate results        │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│  CodeVerification           │
│  - Validate output          │
│  - Check requirements       │
│  - Refine code              │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│  CodeExtraction             │
│  - Parse generated code     │
│  - Extract files            │
│  - Save outputs             │
└─────────────────────────────┘
```

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (for gpt-4o-mini)
- Anthropic API key (for Claude 3.7 Sonnet)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rchhabra13/ai-self-evolving-agent.git
cd ai-self-evolving-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install EvoAgentX:
```bash
pip install git+https://github.com/rchhabra13/ai-self-evolving-agent.git
```

4. Create a `.env` file:
```bash
touch .env
```

## Configuration

Create a `.env.example` file:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Usage

1. Run the self-evolving agent:
```bash
python ai_Self-Evolving_agent.py
```

2. The agent will:
   - Generate a workflow for the specified goal
   - Create multiple agents to execute the workflow
   - Execute the workflow and generate code
   - Verify the generated code with Claude
   - Extract and save output files

3. Find generated files in `examples/output/tetris_game/`

## Example Workflow

The default example generates HTML code for a Tetris game:

1. **Goal Definition**: "Generate html code for the Tetris game that can be played in the browser."

2. **Workflow Generation**: The system breaks this into subtasks:
   - HTML structure creation
   - CSS styling
   - JavaScript game logic
   - Event handling

3. **Agent Execution**: Multiple agents work in parallel/sequence to implement each component

4. **Code Verification**: Claude reviews the generated code for:
   - Correctness
   - Completeness
   - Quality standards

5. **Output Extraction**: Save generated files to disk

## Customization

Modify the goal in `ai_Self-Evolving_agent.py`:

```python
goal = "Your custom goal here"
target_directory = "path/to/output"
```

Examples:
- "Generate a Python Flask web application with user authentication"
- "Create a React component library with TypeScript support"
- "Build a REST API with FastAPI and MongoDB integration"

## Technologies Used

- **EvoAgentX**: Self-evolving agent framework
- **OpenAI**: GPT-4o-mini for workflow generation
- **Anthropic**: Claude 3.7 for code verification
- **LiteLLM**: Multi-LLM integration
- **Python 3.8+**: Core language

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Rishi Chhabra ([@rchhabra13](https://github.com/rchhabra13))

## Roadmap

- [ ] Visual workflow editor
- [ ] Interactive refinement loops
- [ ] Performance metrics dashboard
- [ ] Multi-goal optimization
- [ ] Continuous learning module
- [ ] Integration with version control
- [ ] Deployment automation
- [ ] Cost optimization tracking
