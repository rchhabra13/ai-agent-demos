# 🧬 Clinical Trial Matchmaker

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io)
[![FHIR R4](https://img.shields.io/badge/FHIR-R4-orange.svg)](https://hl7.org/fhir/R4/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agents Assemble Hackathon](https://img.shields.io/badge/Hackathon-Agents%20Assemble-purple.svg)](https://agents-assemble.devpost.com)

> **An MCP server that reads a patient's FHIR record and uses LLM reasoning to identify, rank, and explain matching clinical trials — surfaced directly inside the clinician's workflow.**

Built for the [Agents Assemble: The Healthcare AI Endgame](https://agents-assemble.devpost.com) hackathon on the [Prompt Opinion](https://promptopinion.com) platform.

---

## The Problem

Only **3–5% of eligible cancer patients** enroll in clinical trials, despite ~50% being medically eligible. The bottleneck isn't availability — it's discovery. Existing matching systems use rigid keyword filters that fail to interpret the nuanced plain-English eligibility criteria that characterize real trials.

Traditional rule-based systems cannot answer: *"Does 'no significant cardiac history' apply to a patient with a resolved arrhythmia from 8 years ago?"* LLMs can.

## The Solution

Clinical Trial Matchmaker is a **Model Context Protocol (MCP) server** that:

1. **Parses** a patient's FHIR R4 bundle (conditions, medications, labs, demographics)
2. **Queries** ClinicalTrials.gov for currently recruiting trials matching the patient's conditions
3. **Reasons** using Claude to score each trial's eligibility criteria against the patient's profile
4. **Returns** a ranked, explained list of trials with specific matches, concerns, and clinician recommendations

All within the clinician's existing workflow via Prompt Opinion's SHARP context propagation.

---

## Architecture

```
EHR / Prompt Opinion Platform
        │
        │  SHARP context (patient_id + FHIR token)
        ▼
┌─────────────────────────────────────────────┐
│         Clinical Trial Matchmaker           │
│              (MCP Server)                   │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │  Tool 1: find_matching_trials       │    │
│  │  ┌──────────┐   ┌────────────────┐  │    │
│  │  │ FHIR R4  │   │ ClinicalTrials │  │    │
│  │  │  Parser  │──▶│  .gov API v2   │  │    │
│  │  └──────────┘   └───────┬────────┘  │    │
│  │                          │           │    │
│  │                   ┌──────▼────────┐  │    │
│  │                   │ Claude  LLM   │  │    │
│  │                   │  Reasoner     │  │    │
│  │                   └──────┬────────┘  │    │
│  └──────────────────────────┼───────────┘    │
│                              │               │
│  ┌────────────────┐  ┌───────▼────────────┐  │
│  │ Tool 3:        │  │ Tool 2:            │  │
│  │ draft_enroll   │  │ get_trial_details  │  │
│  │ ment_summary   │  │ + commentary       │  │
│  └────────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────┘
        │
        ▼  Ranked trials + eligibility scores
   Clinician / Agent
```

---

## Features

- **FHIR R4 Native** — Parses real Patient bundles including Condition, MedicationRequest, Observation, and AllergyIntolerance resources
- **LLM Eligibility Reasoning** — Claude reads plain-English inclusion/exclusion criteria and reasons against the patient's actual clinical profile
- **SHARP Context Support** — Automatically propagates patient context through Prompt Opinion's SHARP extension spec
- **Multi-language Summaries** — Patient-facing summaries in English, Spanish, French, Mandarin, and more
- **Clinician Commentary** — AI-generated next steps, fit assessment, and questions for the trial site
- **Structured Outputs** — All responses are Pydantic-validated JSON with mandatory medical disclaimers
- **Retry & Resilience** — Exponential backoff on API failures via Tenacity
- **Structured Logging** — Production-ready observability with Structlog

---

## Quickstart

### Prerequisites

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com)
- A [Prompt Opinion account](https://promptopinion.com) (for hackathon submission)

### Installation

```bash
# Clone the repository
git clone https://github.com/rchhabra13/fhir-trial-agent.git
cd clinical-trial-matchmaker

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install with uv (recommended) or pip
pip install uv
uv pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Run the server

```bash
# Start the MCP server (stdio transport)
trial-matchmaker

# Or directly:
python -m clinical_trial_matchmaker.server
```

### Connect to Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "clinical-trial-matchmaker": {
      "command": "python",
      "args": ["-m", "clinical_trial_matchmaker.server"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-..."
      }
    }
  }
}
```

---

## MCP Tools

### `find_matching_trials`

The primary tool. Finds and ranks recruiting clinical trials for a patient.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `fhir_patient_bundle` | `string` | Yes | FHIR R4 Bundle as JSON string |
| `max_results` | `integer` | No | Max trials to return (default: 10) |
| `location_country` | `string` | No | Country filter (default: "United States") |
| `sharp_patient_id` | `string` | No | SHARP context: patient ID |
| `sharp_fhir_base_url` | `string` | No | SHARP context: FHIR server URL |
| `sharp_fhir_token` | `string` | No | SHARP context: bearer token |

**Response** (`TrialMatchResponse`):
```json
{
  "patient_id": "patient-001",
  "query_conditions": ["Non-small cell lung cancer"],
  "total_trials_searched": 18,
  "matches": [
    {
      "nct_id": "NCT04513847",
      "trial_title": "Pembrolizumab + Chemo in Stage III NSCLC",
      "eligibility_score": 84,
      "likely_eligible": true,
      "key_matches": ["Stage IIIA NSCLC", "ECOG 1", "Age 56"],
      "key_concerns": ["Already on pembrolizumab — confirm combination permitted"],
      "missing_information": ["PD-L1 expression not documented"],
      "recommendation": "Strong candidate — confirm PD-L1 status before contacting site.",
      "phase": "PHASE3",
      "status": "RECRUITING",
      "sponsor": "Merck"
    }
  ],
  "reasoning_model": "claude-opus-4-6",
  "disclaimer": "This output is for informational purposes only..."
}
```

---

### `get_trial_details`

Fetches full protocol details for a specific NCT ID with optional patient-specific clinician commentary.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `nct_id` | `string` | Yes | NCT identifier, e.g. "NCT04513847" |
| `fhir_patient_bundle` | `string` | No | Patient bundle for personalized commentary |
| `include_clinician_commentary` | `boolean` | No | Generate AI commentary (default: true) |

**Response**: Full `TrialDetail` object plus optional `clinician_commentary` field containing:
- **Potential Fit** — specific matching criteria
- **Potential Concerns** — eligibility risks
- **Recommended Next Steps** — concrete actions
- **Questions for Trial Site** — what to ask

---

### `draft_enrollment_summary`

Generates a compassionate patient-facing summary for shared decision-making conversations.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `nct_id` | `string` | Yes | NCT identifier |
| `patient_name` | `string` | Yes | Patient's first name |
| `eligibility_reasoning` | `string` | Yes | Why this trial is relevant |
| `patient_language` | `string` | No | Output language (default: "English") |

**Supported languages**: English, Spanish, French, Mandarin, Portuguese, Arabic, Hindi

---

## Development

### Running tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_fhir_parser.py -v

# Run with real API (integration tests, requires ANTHROPIC_API_KEY)
pytest -m integration
```

### Generate synthetic test patients

```bash
# Single NSCLC patient (prints to stdout)
python scripts/generate_test_patient.py --condition nsclc

# 5 breast cancer patients to a directory
python scripts/generate_test_patient.py \
  --condition "breast cancer" \
  --count 5 \
  --output-dir ./test_patients/

# Save to file
python scripts/generate_test_patient.py \
  --condition "type 2 diabetes" \
  --output patient.json
```

### Code quality

```bash
# Lint
ruff check src/ tests/

# Type check
mypy src/

# Format
ruff format src/ tests/
```

### Project structure

```
clinical-trial-matchmaker/
├── src/
│   └── clinical_trial_matchmaker/
│       ├── server.py          # FastMCP server + tool registration
│       ├── config.py          # Pydantic settings
│       ├── models/
│       │   ├── patient.py     # PatientProfile, LabValue, Medication, etc.
│       │   └── trial.py       # TrialDetail, EligibilityAssessment, etc.
│       ├── services/
│       │   ├── fhir_parser.py   # FHIR R4 Bundle → PatientProfile
│       │   ├── ctgov_client.py  # ClinicalTrials.gov API v2 client
│       │   └── llm_reasoner.py  # Claude eligibility reasoning
│       └── tools/
│           ├── match_trials.py        # find_matching_trials tool
│           ├── trial_details.py       # get_trial_details tool
│           └── enrollment_summary.py  # draft_enrollment_summary tool
├── tests/
│   ├── conftest.py            # Shared fixtures
│   ├── test_fhir_parser.py
│   ├── test_ctgov_client.py
│   └── fixtures/
│       └── sample_patient.json  # Synthetic FHIR bundle for tests
├── scripts/
│   └── generate_test_patient.py  # Synthetic FHIR data generator
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

---

## Docker

```bash
# Build
docker build -t clinical-trial-matchmaker .

# Run
docker run -e ANTHROPIC_API_KEY=sk-ant-... clinical-trial-matchmaker

# Or with docker compose
cp .env.example .env  # Add your key
docker compose up
```

---

## Prompt Opinion / SHARP Integration

This server is designed to run natively on the [Prompt Opinion](https://promptopinion.com) platform.

When deployed there, SHARP context propagation automatically injects:
- `sharp_patient_id` — the current patient's EHR ID
- `sharp_fhir_base_url` — your institution's FHIR R4 endpoint
- `sharp_fhir_token` — a scoped bearer token for read access

The server will automatically fetch the patient's `$everything` bundle when these are present, eliminating the need to manually pass FHIR JSON.

---

## Medical Disclaimer

This software is intended as a **clinical decision support tool** only. It does not constitute medical advice, diagnosis, or treatment recommendations. All clinical trial eligibility must be confirmed by the trial site. Patient participation is always voluntary. This tool should be used only by qualified healthcare professionals in appropriate clinical contexts.

---

## License

MIT © 2026 Rishi Chhabra
