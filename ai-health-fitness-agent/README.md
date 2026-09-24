# AI Health & Fitness Planner Agent

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)

An intelligent health and fitness planning agent powered by Agno AI framework and Google's Gemini model. Generates personalized dietary and fitness plans based on user profile including age, weight, height, activity level, dietary preferences, and fitness goals.

## Overview

The AI Health & Fitness Planner uses two specialized agents:

- **Dietary Expert Agent** - Creates personalized meal plans and nutrition recommendations
- **Fitness Expert Agent** - Designs customized exercise routines and training programs

Both agents work together to provide comprehensive health and fitness guidance based on individual user profiles.

## Features

- **Personalized Dietary Plans**: Detailed meal plans with breakfast, lunch, dinner, and snacks
- **Fitness Customization**: Exercise routines tailored to fitness goals and activity level
- **Multiple Dietary Preferences**: Supports Vegetarian, Keto, Gluten-Free, Low-Carb, Dairy-Free
- **Goal-Based Planning**: Lose Weight, Gain Muscle, Endurance, Stay Fit, Strength Training
- **Interactive Q&A**: Follow-up questions about generated plans
- **Health Considerations**: Important hydration, electrolytes, and fiber recommendations
- **Progress Tips**: Actionable advice for implementation and tracking

## Tech Stack

- **Language**: [Python 3.10+](https://www.python.org/downloads/)
- **Agent Framework**: [Agno](https://agno.ai/)
- **LLM**: [Google Gemini 2.5 Flash Preview](https://ai.google.dev/gemini-api)
- **UI**: [Streamlit](https://docs.streamlit.io/)

## Prerequisites

- Python 3.10 or higher
- Google Gemini API key (free tier available)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rchhabra13/ai_health_fitness_agent.git
   cd ai_health_fitness_agent
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

4. **Set up API key**
   ```bash
   cp .env.example .env
   # Add your GEMINI_API_KEY to .env
   ```

## Usage

1. **Start the application**
   ```bash
   streamlit run health_agent.py
   ```

2. **Enter API Key** (sidebar)
   - Add your Google Gemini API key

3. **Complete Your Profile**
   - Age, weight (kg), height (cm)
   - Sex (Male, Female, Other)
   - Activity level (Sedentary to Extremely Active)
   - Fitness goals (Lose Weight, Gain Muscle, etc.)
   - Dietary preferences (Vegetarian, Keto, etc.)

4. **Generate Plans**
   - Click "Generate My Personalized Plan"
   - View dietary and fitness recommendations

5. **Ask Questions**
   - Use Q&A section to ask about your plans
   - Get clarifications on exercises or nutrition

## Configuration

### Supported Dietary Preferences
- Vegetarian
- Keto
- Gluten Free
- Low Carb
- Dairy Free

### Supported Fitness Goals
- Lose Weight
- Gain Muscle
- Endurance
- Stay Fit
- Strength Training

### Activity Levels
- Sedentary
- Lightly Active
- Moderately Active
- Very Active
- Extremely Active

## Project Structure

```
ai_health_fitness_agent/
├── health_agent.py           # Main application
├── requirements.txt          # Dependencies
├── .env.example             # Environment template
├── .gitignore               # Git ignore patterns
└── README.md                # This file
```

## Example Scenarios

### Weight Loss Plan
- Goal: Lose Weight
- Activity: Lightly Active
- Preferences: Vegetarian
- Dietary focus: Calorie-controlled, high-protein meals
- Exercise: Cardio + strength training combination

### Muscle Gain Program
- Goal: Gain Muscle
- Activity: Very Active
- Preferences: No restrictions
- Dietary focus: High-protein, caloric surplus
- Exercise: Progressive strength training

### Endurance Training
- Goal: Endurance
- Activity: Moderately Active
- Preferences: Low-carb optional
- Dietary focus: Balanced macros with carb-loading options
- Exercise: Cardio progression + recovery

## Features in Detail

### Dietary Plans Include
- Breakfast recommendations with nutritional breakdown
- Lunch options with variety
- Dinner suggestions with portion guidance
- Healthy snack ideas
- Hydration guidelines
- Macro and micronutrient balance
- Consideration of dietary restrictions

### Fitness Plans Include
- Warm-up exercises
- Main workout routine with sets/reps
- Cool-down and stretching
- Recovery guidance
- Progressive overload strategies
- Form tips for injury prevention
- Rest day recommendations

### Q&A Capability
- Ask clarification questions about exercises
- Request modifications to meal plans
- Get motivation and tips
- Discuss dietary substitutions
- Ask about progression strategies

## Troubleshooting

### "GEMINI_API_KEY not found"
```bash
export GEMINI_API_KEY='your-key-here'
# Or add to .env file
```

### API key error
- Verify key is from [AI Studio](https://aistudio.google.com/apikey)
- Check key has necessary permissions
- Ensure no extra spaces in .env

### Slow response
- Internet connection check
- API rate limiting (wait a moment)
- Try a simpler query first

## Health & Safety

This tool provides educational fitness and nutrition guidance. It is NOT a substitute for:
- Professional medical advice
- Personalized nutrition counseling
- Physical therapy
- Mental health support

Always consult healthcare professionals before:
- Starting new exercise programs
- Making major dietary changes
- If you have health conditions
- If you take medications

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Submit Pull Requests or GitHub issues.

## Support

- [GitHub Issues](https://github.com/rchhabra13/ai_health_fitness_agent/issues)
- [Google Gemini Docs](https://ai.google.dev/gemini-api)
- [Agno Framework](https://agno.ai/)

## Author

[Rishi Chhabra](https://github.com/rchhabra13)

---

Built with Agno and Google Gemini API
