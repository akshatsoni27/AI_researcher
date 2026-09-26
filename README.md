# MIMIR

MIMIR is an autonomous research assistant that plans a research task, gathers web or document evidence, verifies the results, and generates a cited Markdown report and PDF.

## Requirements

- Python 3.11, 3.12, or 3.13
- A Groq API key

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder with your own `GROQ_API_KEY`. Never commit `.env` or expose the key publicly. If a real key has been exposed, revoke it and create a replacement before using this project.

## Run the CLI

```powershell
python -m backend.main
```

The CLI researches the prompt, prints the final report, and writes a PDF to `reports/research_report.pdf`.

## Run the API

```powershell
uvicorn backend.api:app --reload
```

Once running, open `http://127.0.0.1:8000/docs` for the interactive API documentation.

The API exposes:

- `GET /api/health` to check service status
- `POST /api/research` to start a research job
- `GET /api/research/{job_id}` to retrieve job status and results
- `POST /api/research/{job_id}/chat` to ask follow-up questions about a completed report
- `GET /api/research/{job_id}/pdf` to download the generated PDF

## Document research

Place source PDFs in `uploads/` and use the document-loading workflow to populate the local Chroma knowledge base. The generated `uploads/` and `chroma_db/` directories are local runtime data and are intentionally excluded from Git.

## Project layout

```text
backend/
  agents/       Planning, research, verification, and report generation
  graph/        LangGraph state and workflow
  rag/          PDF loading and document retrieval
  reports/      PDF generation
  tools/        Web search integration
```

## Validation

```powershell
python -m compileall -q backend
```

The scripts under `backend/rag/test_rag.py` and `backend/tools/test_search.py` are interactive smoke checks. They require network access and a configured `GROQ_API_KEY` where applicable.