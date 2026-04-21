# claw_env

Python sandbox for healthcare automation patterns using Playwright scraping, OpenClaw-style parallel extraction, and optional LLM/CrewAI reporting workflows.

## What this repository contains

- Browser automation examples with Playwright (`healthcare_automation.py`, `advanced_playwright.py`)
- OpenClaw-style concurrency demos (`openclaw_final_working.py`, `openclaw_final.py`, `openclaw_healthcare.py`)
- LLM reporting flows (OpenAI and Ollama variants)
- Crew-based multi-agent healthcare analysis scripts
- Generated artifacts (Excel, JSON, HTML, TXT reports)

## Quick start

### 1) Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2) Install core dependencies

```powershell
pip install pandas openpyxl playwright tenacity requests
python -m playwright install
```

### 3) Run a baseline OpenClaw-style pipeline

```powershell
python openclaw_final_working.py
```

Expected outputs include:
- `openclaw_healthcare_report.xlsx`
- `openclaw_results.json`
- `PORTFOLIO.txt`
- `INTERVIEW_OPENCLAW_SCRIPT.txt`

## Optional workflows

### Playwright extraction + report seed

```powershell
python healthcare_automation.py
```

Generates:
- `staff_report.xlsx`

### OpenAI-based LLM reporting

```powershell
python llm_reporting.py
```

Generates:
- `ai_generated_report.html`
- `ai_summary.txt`

### Ollama/Crew workflows

Scripts such as `healthcare_crew_ollama.py` and `ollama_reporting.py` target a local Ollama server (`http://localhost:11434`) and compatible local models.

## Dependency notes

This repo includes multiple experimental tracks. Install what you need:

- Base: `pandas`, `openpyxl`, `playwright`, `tenacity`, `requests`
- OpenAI track: `openai`
- CrewAI track: `crewai`, `crewai_tools`, `langchain-community`
- OpenClaw/CMDOP experiments: `openclaw`, `cmdop` (if you intend to run related scripts)

## Project file map (high-level)

- `openclaw_final_working.py`: main production-style OpenClaw demo pipeline
- `openclaw_final.py`: similar pipeline with richer console output
- `healthcare_automation.py`: Playwright extraction against OrangeHRM demo
- `llm_reporting.py`: OpenAI summarization/anomaly reporting on extracted data
- `healthcare_crew.py` / `healthcare_crew_ollama.py`: crew-based analysis flows
- `test_playwrite.py`, `test_ollama.py`: basic connectivity/test scripts

## Security and configuration

- Do not hardcode API keys in source files.
- Use environment variables for credentials (`OPENAI_API_KEY`, tool-specific API keys).
- Treat files like `auth.json` and generated reports as sensitive.
- Review `.gitignore` before committing local credentials or artifacts.

## Typical run order

1. Run extraction (`healthcare_automation.py` or `openclaw_final_working.py`)
2. Validate output Excel/JSON files
3. Run LLM analysis (`llm_reporting.py` or Ollama/Crew scripts)
4. Share generated report artifacts
