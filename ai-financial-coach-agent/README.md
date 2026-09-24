# AI Financial Coach Agent - Google ADK

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)

A comprehensive financial coaching application powered by Google's Agent Development Kit (ADK) and Gemini AI. Provides personalized financial advice through a multi-agent system that analyzes budgets, recommends savings strategies, and creates debt reduction plans.

## Overview

The AI Financial Coach implements a three-stage sequential analysis using specialized agents:

1. **Budget Analysis Agent** - Categorizes spending and identifies optimization opportunities
2. **Savings Strategy Agent** - Creates personalized savings plans and emergency fund recommendations
3. **Debt Reduction Agent** - Develops optimized debt payoff strategies

## Features

- **Multi-Agent Sequential Processing**: Specialized agents for budget, savings, and debt analysis
- **Comprehensive Financial Analysis**: Spending categorization, income analysis, and financial health assessment
- **Transaction Processing**: CSV upload support for transaction data
- **Manual Expense Entry**: Easy input form for expense categories
- **Debt Management**: Avalanche and snowball method comparisons
- **Emergency Fund Calculation**: Based on expense analysis and dependants
- **Interactive Visualizations**: Charts and tables for financial insights
- **PDF Export**: Download comprehensive reports

## Tech Stack

- **Language**: [Python 3.10+](https://www.python.org/downloads/)
- **Agent Framework**: [Google ADK](https://github.com/google-adk)
- **LLM**: [Google Gemini 2.5 Flash](https://ai.google.dev/gemini-api)
- **UI**: [Streamlit](https://docs.streamlit.io/)
- **Data Processing**: [Pandas](https://pandas.pydata.org/), [Plotly](https://plotly.com/)
- **Storage**: [SQLite](https://www.sqlite.org/) for conversation history

## Prerequisites

- Python 3.10 or higher
- Google Gemini API key
- Internet connection

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rchhabra13/ai_financial_coach_agent.git
   cd ai_financial_coach_agent
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

4. **Set up API keys**
   ```bash
   cp .env.example .env
   # Edit .env with your GOOGLE_API_KEY
   ```

## Usage

1. **Run the application**
   ```bash
   streamlit run ai_financial_coach_agent.py
   ```

2. **Enter Your Profile**
   - Monthly income
   - Number of dependants
   - Weight, height, age, sex
   - Activity level and fitness goals

3. **Input Expenses** (Choose one method)
   - Upload CSV with transactions
   - Enter manually by category

4. **Add Debts** (Optional)
   - Enter debt details: name, amount, interest rate, minimum payment

5. **Get Analysis**
   - Click "Analyze My Finances"
   - View budget analysis, savings strategy, and debt reduction plans

## Configuration

### Environment Variables

```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

### CSV Format

Required columns:
- **Date**: YYYY-MM-DD format
- **Category**: Expense category
- **Amount**: Numeric value

## Project Structure

```
ai_financial_coach_agent/
├── ai_financial_coach_agent.py  # Main application
├── requirements.txt              # Dependencies
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore patterns
└── README.md                    # This file
```

## Features in Detail

### Budget Analysis
- Spending categorization by category
- Income vs. expense comparison
- Monthly surplus/deficit calculation
- Spending reduction recommendations with estimated savings

### Savings Strategy
- Emergency fund size calculation (3-6 months expenses)
- Recommended savings allocation
- Automation techniques for consistent saving
- Progressive savings growth plan

### Debt Reduction
- Avalanche method (highest interest first)
- Snowball method (smallest balance first)
- Interest comparison and payoff timeline
- Consolidation and refinancing suggestions
- Credit score improvement strategies

## Example Scenarios

### Young Professional ($5,000/month income)
- Budget allocation: 50/30/20 rule
- Emergency fund: 3 months expenses
- Debt payoff: 5-year plan for student loans

### Family with Dependants
- Child-related expense categories
- Education savings recommendations
- Higher emergency fund requirements
- Life insurance considerations

### High-Income Earner
- Investment portfolio recommendations
- Tax optimization strategies
- Wealth building acceleration
- Retirement planning focus

## Troubleshooting

### "GOOGLE_API_KEY not found"
```bash
export GOOGLE_API_KEY='your-key-here'
```

### CSV Upload Errors
- Verify column names: Date, Category, Amount
- Check date format: YYYY-MM-DD
- Ensure amounts are numeric

### Agent Analysis Slow
- Large CSV files take longer to process
- Check internet connection
- Verify API key is valid

## Data Privacy

- All data is processed locally
- Financial information is not permanently stored
- Secure API communication with Google
- No data sharing with third parties

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Submit Pull Requests or create GitHub issues.

## Support

- [GitHub Issues](https://github.com/rchhabra13/ai_financial_coach_agent/issues)
- [Google ADK Docs](https://github.com/google-adk)
- [Gemini API Docs](https://ai.google.dev/gemini-api)

## Author

[Rishi Chhabra](https://github.com/rchhabra13)

---

**Disclaimer**: This tool provides educational and informational content only. It is not a substitute for professional financial advice. Always consult qualified financial professionals before making significant financial decisions.
