FILING_PARSER_PROMPT = """You are a financial analyst extracting structured data from an SEC 10-K filing.

Extract the following from the text below and return a valid JSON object with these exact keys:

{{
  "revenue": [list of annual revenue figures in USD millions, most recent first],
  "net_income": [list of annual net income figures in USD millions, most recent first],
  "operating_cash_flow": [list of annual OCF in USD millions, most recent first],
  "capex": [list of annual capex in USD millions, most recent first, as positive numbers],
  "total_debt": <most recent total debt in USD millions>,
  "cash_and_equivalents": <most recent cash in USD millions>,
  "shares_outstanding": <diluted shares outstanding in millions>,
  "revenue_growth_guidance": <management guidance for next year revenue growth as decimal, e.g. 0.12 for 12%, null if not stated>,
  "key_risks": [top 3 risk factors as short strings],
  "business_description": <2-sentence description of what the company does>,
  "fiscal_year_end": <most recent fiscal year end date as YYYY-MM-DD>
}}

Rules:
- All monetary values in USD millions
- Return null for any field you cannot find
- Do not include markdown, only raw JSON

10-K TEXT:
{filing_text}
"""

MOAT_ASSESSMENT_PROMPT = """You are a senior equity analyst at a top-tier hedge fund. Assess the competitive moat of {company_name} ({ticker}).

Use the financial data and business description below to evaluate five moat sources. Return a structured JSON object:

{{
  "pricing_power": {{
    "score": <1-5>,
    "evidence": "<one sentence>"
  }},
  "switching_costs": {{
    "score": <1-5>,
    "evidence": "<one sentence>"
  }},
  "network_effects": {{
    "score": <1-5>,
    "evidence": "<one sentence>"
  }},
  "cost_advantages": {{
    "score": <1-5>,
    "evidence": "<one sentence>"
  }},
  "intangible_assets": {{
    "score": <1-5>,
    "evidence": "<one sentence>"
  }},
  "overall_moat_rating": "<Wide / Narrow / None>",
  "moat_summary": "<2-3 sentence synthesis of competitive position>"
}}

Scoring: 1=none, 2=weak, 3=moderate, 4=strong, 5=dominant

FINANCIAL DATA:
{financials_summary}

BUSINESS DESCRIPTION:
{business_description}

KEY RISKS:
{key_risks}

Return only raw JSON.
"""

MEMO_SYNTHESIS_PROMPT = """You are a buy-side equity analyst writing an investment memo for a portfolio manager.

Generate a structured investment memo for {company_name} ({ticker}) based on the analysis below.

Return a JSON object:
{{
  "recommendation": "<BUY / HOLD / SELL>",
  "confidence_score": <0.0 to 1.0>,
  "memo": "<full investment memo in markdown format>",
  "key_catalysts": ["<catalyst 1>", "<catalyst 2>", "<catalyst 3>"],
  "key_risks": ["<risk 1>", "<risk 2>", "<risk 3>"]
}}

The memo markdown must include these sections:
## Executive Summary
## Business Overview
## Valuation (DCF)
## Sentiment Analysis
## Competitive Position (Moat)
## Key Risks
## Recommendation

Be specific, cite numbers, and justify the recommendation clearly.

--- INPUT DATA ---

DCF MODEL:
{dcf_summary}

SENTIMENT ANALYSIS:
{sentiment_summary}

MOAT ASSESSMENT:
{moat_analysis}

PARSED FINANCIALS:
{financials_summary}

Return only raw JSON.
"""

SENTIMENT_SUMMARY_PROMPT = """Summarize the following FinBERT sentiment results from an earnings call / MD&A section for {company_name} ({ticker}).

Identify:
1. Overall management tone (bullish / neutral / cautious / bearish)
2. Key themes driving sentiment
3. Any notable tone shifts compared to typical corporate language

Sentiment data:
{sentiment_data}

Respond in 3-4 sentences.
"""
