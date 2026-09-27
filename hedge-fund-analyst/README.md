# LLM-Powered Hedge Fund Analyst Agent

An autonomous multi-agent system that mimics a buy-side equity analyst. Feed it a ticker, get a structured investment memo with a Buy/Hold/Sell recommendation — all in under 30 seconds.

It ingests SEC 10-K filings, runs a DCF valuation model, analyzes management sentiment with FinBERT, assesses competitive moat, and synthesizes everything into a cited memo using Claude. All agent traces are logged to LangSmith and company data is stored in a Neo4j knowledge graph for cross-company analysis.

## What It Does

- **Filing Parser Agent** — fetches the latest 10-K from SEC EDGAR and extracts revenue, margins, OCF, capex, and risk factors
- **DCF Valuation Agent** — builds a 5-year discounted cash flow model with WACC, terminal value, and intrinsic value per share
- **Sentiment Agent** — runs FinBERT over the MD&A / earnings transcript in chunks, aggregates tone, generates a narrative summary
- **Moat Assessment Agent** — scores pricing power, switching costs, network effects, cost advantages, and intangibles (1–5 scale)
- **Memo Synthesis Agent** — combines all outputs into a structured Buy/Hold/Sell memo with confidence score and citations

## Architecture

```
POST /analyze/{ticker}
        │
        ▼
┌───────────────┐
│  fetch_data   │  SEC EDGAR (10-K) + yfinance (price, beta, market cap)
└──────┬────────┘
       │
┌──────▼────────┐
│ parse_filing  │  Claude extracts structured financials from raw 10-K text
└──────┬────────┘
       │
┌──────▼────────┐
│   run_dcf     │  5-year FCF projection → WACC → terminal value → intrinsic value
└──────┬────────┘
       │
┌──────▼────────┐
│ run_sentiment │  FinBERT chunks MD&A / transcript → aggregate tone → Claude narrative
└──────┬────────┘
       │
┌──────▼────────┐
│ assess_moat   │  Claude scores 5 moat dimensions → Wide / Narrow / None rating
└──────┬────────┘
       │
┌──────▼────────┐
│ synthesize    │  Claude writes full investment memo + BUY / HOLD / SELL + confidence
└──────┬────────┘
       │
┌──────▼────────┐
│  store_neo4j  │  Company → Metric → Analysis nodes written to knowledge graph
└───────────────┘
```

All nodes are traced end-to-end in **LangSmith**. The LangGraph `StateGraph` passes a single typed state object through the pipeline.

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph (StateGraph) |
| LLM | Claude API (Anthropic) — Sonnet for analysis, Haiku for summaries |
| Sentiment | FinBERT (`ProsusAI/finbert`) |
| Data | SEC EDGAR API, yfinance |
| Knowledge Graph | Neo4j 5.x |
| API | FastAPI |
| Observability | LangSmith |
| Deployment | Docker + Docker Compose |

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Anthropic API key
- LangSmith API key (optional, for tracing)

### 1. Clone and configure

```bash
cd hedge_fund

cp .env.example .env
# Fill in ANTHROPIC_API_KEY, SEC_USER_AGENT, and optionally LANGSMITH_API_KEY
```

### 2. Start with Docker

```bash
docker-compose up --build
```

This starts the FastAPI app on port 8000 and Neo4j on ports 7474/7687. Neo4j browser is available at `http://localhost:7474`.

### 3. Run locally (without Docker)

```bash
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# Start Neo4j separately or set NEO4J_URI to a hosted instance
uvicorn main:app --reload
```

## Usage

### Analyze a ticker

```bash
curl -X POST http://localhost:8000/analyze/AAPL
```

Response includes the full investment memo, DCF output, sentiment score, and moat rating.

```bash
# With an earnings call transcript
curl -X POST http://localhost:8000/analyze/MSFT \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "MSFT",
    "include_transcript": true,
    "transcript_text": "Q4 FY2024 earnings call... [paste transcript here]"
  }'
```

### Check analysis history (from Neo4j)

```bash
curl http://localhost:8000/history/AAPL
```

### Health check

```bash
curl http://localhost:8000/health
```

### Interactive API docs

Visit `http://localhost:8000/docs` for the full Swagger UI.

## Example Output

_Coming soon_

## DCF Model

The valuation model uses:

- **FCF** = Operating Cash Flow − CapEx (from 10-K)
- **Growth rate** — management guidance if disclosed, otherwise historical OCF CAGR, fallback 8%
- **WACC** = CAPM cost of equity + after-tax cost of debt, weighted by market cap / debt ratio
- **Terminal value** = FCF₅ × (1 + 3%) / (WACC − 3%)
- **Equity value** = PV(FCFs) + PV(terminal value) − net debt

The model is intentionally transparent — every input and assumption is returned in the response so you can audit it.

## Neo4j Knowledge Graph

Schema:

```
(Company {ticker, name, sector, industry})
  -[:HAS_METRIC]->  (Metric {name, period, value, unit})
  -[:HAS_ANALYSIS]-> (Analysis {recommendation, confidence, analyzed_at})
```

This lets you query across multiple companies — e.g. compare revenue growth or recommendation history across a sector.

## Project Structure

```
hedge_fund/
├── main.py                   ← FastAPI app (3 endpoints)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── models/
│   └── schemas.py            ← AnalystState TypedDict + Pydantic request/response models
├── utils/
│   └── prompts.py            ← All Claude prompt templates
├── data/
│   ├── edgar.py              ← SEC EDGAR API client + 10-K text extraction
│   ├── market.py             ← yfinance wrapper
│   └── neo4j_client.py       ← Neo4j driver (upsert, metrics, history queries)
├── agents/
│   ├── filing_parser.py      ← Claude extracts structured financials
│   ├── dcf_valuation.py      ← 5-year DCF model (pure Python)
│   ├── sentiment.py          ← FinBERT pipeline + Claude narrative
│   ├── moat_assessment.py    ← Claude moat scoring
│   └── memo_synthesis.py     ← Claude investment memo generator
└── graph/
    └── workflow.py           ← LangGraph StateGraph + run_analysis() entrypoint
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Claude API key |
| `NEO4J_URI` | Yes | Neo4j connection URI (default: `bolt://neo4j:7687`) |
| `NEO4J_USER` | Yes | Neo4j username |
| `NEO4J_PASSWORD` | Yes | Neo4j password |
| `SEC_USER_AGENT` | Yes | Identifies your app to EDGAR (e.g. `YourName email@example.com`) |
| `LANGCHAIN_TRACING_V2` | No | Set `true` to enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | No | LangSmith API key |
| `LANGCHAIN_PROJECT` | No | LangSmith project name |

> SEC EDGAR requires a valid `User-Agent` header per their [access policy](https://www.sec.gov/os/accessing-edgar-data). Use your real name and email.

## Limitations

- Earnings call transcripts aren't freely available via API — the sentiment agent falls back to the MD&A section from the 10-K if no transcript is provided
- DCF accuracy depends on how cleanly Claude extracts financials from the 10-K. Complex holding company structures or non-standard filings may produce noisy results
- FinBERT requires ~1.5GB RAM. The Docker image pre-downloads the model at build time

## License

MIT
