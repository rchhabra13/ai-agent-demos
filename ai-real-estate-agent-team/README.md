# AI Real Estate Agent Team

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A sophisticated real estate search and analysis platform powered by Firecrawl and Google Gemini. This application provides comprehensive property insights, market analysis, and investment recommendations using advanced web scraping and multi-agent AI.

## Description

The AI Real Estate Agent Team is a multi-agent system that automates property search and analysis. It uses Firecrawl for efficient property data extraction from multiple real estate websites and AI agents for market analysis and property valuations, helping you find your ideal home with data-driven insights.

## Features

- **Multi-Agent Analysis System**
  - Property Search Agent: Extracts properties using Firecrawl
  - Market Analysis Agent: Provides market trends and insights
  - Property Valuation Agent: Evaluates properties for investment potential

- **Multi-Platform Property Search**
  - Zillow: Largest real estate marketplace
  - Realtor.com: Official NAR website
  - Trulia: Neighborhood-focused search
  - Homes.com: Comprehensive property platform

- **Advanced Property Analysis**
  - Detailed property information extraction
  - Property features and amenities
  - Listing URLs and agent contact information
  - Direct property links for quick navigation

- **Comprehensive Market Insights**
  - Current market conditions
  - Price trends and analysis
  - Neighborhood insights
  - Investment potential assessment
  - Strategic recommendations

- **Interactive UI**
  - Real-time progress tracking
  - Tabbed interface for different views
  - Professional presentation of results
  - Responsive design

## Architecture

```
User Inputs
    ↓
┌─────────────────────────────────┐
│  DirectFirecrawlAgent           │ (Extract properties)
│  - Firecrawl Integration        │
│  - Multi-website search         │
│  - Structured data extraction   │
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│  Market Analysis Agent          │ (Analyze market trends)
│  - Market conditions            │
│  - Neighborhood insights        │
│  - Investment outlook           │
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│  Property Valuation Agent       │ (Evaluate properties)
│  - Value assessment             │
│  - Investment potential         │
│  - Recommendations              │
└────────────┬────────────────────┘
             ↓
        Results UI
```

## Prerequisites

- Python 3.8 or higher
- Google AI API key (Gemini)
- Firecrawl API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rchhabra13/ai_real_estate_agent_team.git
cd ai_real_estate_agent_team
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
GOOGLE_API_KEY=your_google_api_key_here
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run ai_real_estate_agent_team.py
```

2. Open your browser to `http://localhost:8501`

3. Enter API keys in the sidebar

4. Select real estate websites to search

5. Configure your property requirements:
   - Location (city, state)
   - Budget range
   - Property details (type, bedrooms, bathrooms, sqft)
   - Special features and timeline

6. Click "Start Property Analysis" to generate comprehensive results

## API Configuration

### Google AI API
- Visit: https://aistudio.google.com/app/apikey
- Create an API key
- Model used: Gemini 2.5 Flash

### Firecrawl API
- Visit: https://firecrawl.dev
- Sign up and create an API key
- Used for property data extraction

## Output

The system generates three analysis views:

**Properties Tab**:
- Detailed listings with full information
- Price, type, bedrooms, bathrooms, sqft
- Expandable investment analysis
- Direct links to property listings

**Market Analysis Tab**:
- Market condition assessment
- Neighborhood insights
- Investment outlook and trends

**Valuations Tab**:
- Property value assessments
- Investment potential ratings
- Actionable recommendations

## Technologies Used

- **Agno**: Multi-agent framework
- **Google Gemini 2.5 Flash**: Language model
- **Firecrawl**: Web data extraction
- **Streamlit**: Web application interface
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

- [ ] Mortgage calculator integration
- [ ] School district information
- [ ] Crime statistics integration
- [ ] Historical price trends
- [ ] Property management integration
- [ ] Virtual tour support
- [ ] Neighborhood comparison tool
- [ ] Export to PDF reports
