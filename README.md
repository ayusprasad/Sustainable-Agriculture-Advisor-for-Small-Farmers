# Sustainable Agriculture Advisor

[![CI](https://github.com/ayusprasad/Sustainable-Agriculture-Advisor-for-Small-Farmers/actions/workflows/ci.yml/badge.svg)](https://github.com/ayusprasad/Sustainable-Agriculture-Advisor-for-Small-Farmers/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Inference-Groq-F55036)

A Streamlit demonstration that generates crop and soil aware sustainable farming suggestions with a Groq language model.

## Features

- Collects crop, location, soil condition, and optional pest context.
- Generates an initial recommendation and supports follow-up questions.
- Shows a small crop calendar for wheat and corn.
- Keeps the conversation and saved recommendations in the current Streamlit session.
- Handles missing credentials and provider errors with a clear message.

Weather information and yield figures are not generated: this demo does not connect to a weather service or validate agronomic outcomes. Treat model output as general information and confirm decisions with local agricultural experts.

## Architecture

```text
Farmer
  └─ Streamlit interface (app.py)
       ├─ Session state: conversation and saved advice
       └─ Groq Chat Completions API
```

## Tech stack

Python 3.11+, Streamlit, Groq Python SDK, pytest, Ruff, GitHub Actions.

## Run locally

### Prerequisites

- Python 3.11 or newer
- A Groq API key

### Install

```bash
git clone https://github.com/ayusprasad/Sustainable-Agriculture-Advisor-for-Small-Farmers.git
cd Sustainable-Agriculture-Advisor-for-Small-Farmers
python -m venv .venv
```

Activate the environment:

- macOS/Linux: `source .venv/bin/activate`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`

Install the application dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Configure and run

Copy `.env.example` to `.env`, set `GROQ_API_KEY`, then start the app:

```bash
streamlit run app.py
```

## Quality checks

```bash
ruff check app.py tests
pytest -q
python -m compileall -q app.py tests
```

GitHub Actions runs linting, unit tests, and compilation on each push and pull request.
