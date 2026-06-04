# MB 8.0 Adaptive STOIC

MB 8.0 Adaptive STOIC is a deterministic football dataset processing app. It ingests CSV or Excel files, cleans and normalizes the data, excludes SRL and Friendly matches, runs a fixed ordered rule pipeline, applies CDC correlation control, scores the slip, and only then runs the non-bypassable Magic Check.

The app does not use AI discretion for betting decisions. Every PASS or REJECT comes from hard-coded rules and every rejected pick includes an exact rejection reason.

## Install

```bash
cd mb8_adaptive_stoic
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run FastAPI

```bash
uvicorn mb8_adaptive_stoic.app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to upload a dataset through the API.

Phase 2 application endpoints:

- `POST /run-mb8` accepts a CSV, XLS, or XLSX upload.
- `POST /run-mb8-json` accepts JSON records, CSV text, or XLSX base64 for Custom GPT Actions.
- `GET /runs` lists saved run history.
- `GET /runs/{run_id}` returns a saved run with full result payload.
- `GET /runs/{run_id}/download.csv` downloads a combined CSV report.
- `GET /runs/{run_id}/download.pdf` downloads a PDF report.
- `GET /custom-gpt-openapi.json` returns an Actions-focused OpenAPI schema.

Protected production endpoints require `X-MB8-API-Key` when `MB8_AUTH_REQUIRED=true`.

## Run Streamlit

```bash
streamlit run mb8_adaptive_stoic/interface/streamlit_app.py
```

Drag and drop a CSV, XLS, or XLSX file and click `Run MB 8.0 Adaptive STOIC`. The dashboard shows the Final Slip table, Rejected Picks table, Audit Log viewer, CSV downloads, PDF download, and saved Run History.

## Dataset Template

Use `sample_data/sample_template.csv` as the starter format. Required columns are:

- `home_team`
- `away_team`
- `league`
- `market`
- `odds`

Optional scoring columns can improve deterministic scoring, including `home_strength`, `away_strength`, `xg_gap`, `elo_gap`, `momentum`, `goal_pressure`, `chaos_index`, `volatility`, `draw_risk`, `market_drift`, and `lineup_risk`.

## Run Tests

```bash
pytest
```

## Why Magic Check Is Non-Bypassable

Magic Check is implemented as the final gate after feature engineering, ecosystem classification, dominance stability, behavioral filters, PGCE risk, market selection, MVSS, CDC, and STOIC slip scoring. It rejects any pick with missing audit trail, incomplete pipeline, SRL/Friendly detection, high CDC risk, FRAGILE MVSS, or a STOIC Score below the configured threshold. The UI cannot edit thresholds at runtime.

## Deployment And Custom GPT

Render deployment is defined in the repository root `render.yaml`.

Production files:

- `render.yaml`
- `.env.production.example`
- `DEPLOYMENT.md`
- `CUSTOM_GPT_ACTIONS.md`
- `PRODUCTION_READINESS_CHECKLIST.md`

The Custom GPT Action schema is available at:

```text
/custom-gpt-openapi.json
```
