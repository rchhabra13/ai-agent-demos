# Clinical Insights Assistant

> An agentic AI system for clinical trial analysis — detect issues, compare cohorts, simulate what-if scenarios, and generate regulatory-ready summaries, all from a Streamlit dashboard or the CLI.

---

## What it does

This project was built as a capstone to explore how an AI agent can autonomously reason about clinical trial data. At its core it works like this:

1. **Load** synthetic longitudinal patient data (200 patients × 30 days)
2. **Detect** problems — non-compliance, adverse events, dosage instability, declining outcomes
3. **Compare** cohorts statistically (Welch t-test, chi-squared, Cohen's d)
4. **Simulate** what-if scenarios — bump a dosage, run a compliance intervention, sweep sensitivity
5. **Summarize** everything through a mock LLM layer (swappable with OpenAI / Azure)
6. **Agent loop** — a ReAct-style autonomous agent that chains all of the above and generates a final report

You can drive all of this through a **Streamlit web app**, a **CLI**, or the **Python API** directly.

---

## Demo

```
streamlit run src/ui/streamlit_app.py
```

Open `http://localhost:8501` and you'll get:

| Page | What you can do |
|------|----------------|
| Dashboard | KPIs, outcome distributions, trends by cohort |
| Issue Detection | Tune thresholds, see flagged records with severity |
| Cohort Comparison | Statistical tests + AI narrative |
| Scenario Simulation | Dosage change, compliance intervention, sensitivity sweep |
| GenAI Summaries | Doctor notes summary, regulatory report, recommendations |
| Agentic AI | Watch the agent reason step-by-step, ask it questions |
| Patient Lookup | Drill down into any individual patient |

---

## Project Structure

```
clinical-insights-assistant/
├── src/
│   ├── data_loader.py          # synthetic data generation + loading + validation
│   ├── issue_detection.py      # rule-based + z-score anomaly detection
│   ├── cohort_analysis.py      # t-tests, chi-squared, compliance trends
│   ├── scenario_simulation.py  # dosage / compliance what-if simulations
│   ├── genai_interface.py      # mock LLM (drop-in for real API)
│   ├── agent/
│   │   ├── agent_core.py       # ReAct-style autonomous agent
│   │   └── memory.py           # conversation + analysis memory
│   └── ui/
│       ├── streamlit_app.py    # main web interface
│       └── cli.py              # command-line interface
├── notebooks/
│   ├── 01_data_ingestion_and_eda.ipynb
│   ├── 02_issue_detection.ipynb
│   ├── 03_cohort_comparison.ipynb
│   ├── 04_scenario_simulation.ipynb
│   ├── 05_genai_summary_generation.ipynb
│   └── 06_agentic_ai_loop.ipynb
├── tests/                      # pytest suite — 50+ tests across all modules
├── data/                       # generated CSV lives here (gitignored)
├── Dockerfile
└── requirements.txt
```

---

## Quick Start

### Local

```bash
git clone https://github.com/rchhabra13/clinical-insights-assistant.git
cd clinical-insights-assistant

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

# generate the synthetic dataset
python src/data_loader.py

# launch the app
streamlit run src/ui/streamlit_app.py
```

### Docker

```bash
docker build -t clinical-insights-assistant .
docker run -p 8501:8501 clinical-insights-assistant
```

Then open `http://localhost:8501`.

---

## CLI

```bash
# validate the dataset
python src/ui/cli.py validate

# run issue detection with custom thresholds
python src/ui/cli.py detect --compliance-threshold 80 --z-threshold 2.5

# cohort comparison
python src/ui/cli.py cohort

# scenario simulation
python src/ui/cli.py simulate --scenario-type dosage_change --dosage 75

# generate summaries
python src/ui/cli.py summarize --summary-type regulatory

# run the autonomous agent
python src/ui/cli.py agent
```

---

## Python API

```python
from src.data_loader import load_data, generate_synthetic_data
from src.issue_detection import run_all_detections
from src.cohort_analysis import run_full_cohort_analysis
from src.agent.agent_core import ClinicalInsightsAgent

df = generate_synthetic_data(num_patients=200, days_per_patient=30)

# detect issues
issues = run_all_detections(df)
print(issues['summary'])

# compare cohorts
cohort_results = run_full_cohort_analysis(df)
print(cohort_results['outcome_comparison']['interpretation'])

# run the agent
agent = ClinicalInsightsAgent(df, verbose=True)
report = agent.run()

# ask it a question
answer = agent.ask("Which cohort has better outcomes?")
print(answer)
```

---

## Dataset

Fully synthetic — generated on-the-fly with `src/data_loader.py`. Each record represents one patient visit:

| Column | Description |
|--------|-------------|
| `patient_id` | P001 – P200 |
| `trial_day` | Day 1 – 30 |
| `dosage_mg` | 50 / 75 / 100 mg |
| `compliance_pct` | 50 – 100% (drifts slightly over time) |
| `adverse_event_flag` | 0 or 1 (~10% rate) |
| `doctor_notes` | One of 10 templated note strings |
| `outcome_score` | 40 – 100 (function of dosage + compliance + adverse event) |
| `cohort` | A or B (Cohort A has a +5 point advantage baked in) |
| `visit_date` | 2024-01-01 + trial_day |

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Data | pandas, numpy |
| Stats | scipy (Welch t-test, chi-squared, Cohen's d) |
| Viz | plotly, matplotlib, seaborn |
| UI | streamlit |
| Agent | custom ReAct loop (no LangChain dependency) |
| LLM | mock (template-based) — swap `genai_interface.py` for real API |
| Tests | pytest |
| Deploy | Docker (python:3.10-slim) |

---

## Tests

```bash
pytest tests/ -v
```

The test suite covers all five modules: data loading, issue detection, cohort analysis, scenario simulation, and the agent/memory system.

---

## Swapping the Mock LLM

The `MockLLM` in `src/genai_interface.py` handles all text generation with keyword routing. To plug in a real model, replace the `generate()` method body with an OpenAI / Anthropic / Azure call — everything else stays the same.

```python
# example drop-in
from openai import OpenAI

client = OpenAI()

def generate(self, prompt: str, max_tokens: int = 500) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content
```

---

## Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Run `pytest tests/ -v` to make sure nothing breaks
5. Open a pull request

---

## License

MIT
