from __future__ import annotations

import base64
import io

import pandas as pd
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.auth import require_api_key
from app.custom_gpt_actions import custom_gpt_openapi_schema
from app.database import get_run_history, init_db, list_run_history
from app.production_config import PRODUCTION_SETTINGS
from app.services import run_mb8_application
from data_layer.ingest import read_dataset
from interface.reports import combined_report_csv_bytes, pdf_report_bytes
from rules_engine.stoic_pipeline import get_pipeline_order, run_stoic_pipeline


class MB8JsonRunRequest(BaseModel):
    source_filename: str = Field(default="custom-gpt-records.json")
    records: list[dict[str, object]] | None = None
    csv_text: str | None = None
    xlsx_base64: str | None = None


app = FastAPI(
    title="MB 8.0 Adaptive STOIC",
    version="0.2.0",
    description=(
        "Application layer for running the deterministic MB 8.0 Adaptive STOIC engine. "
        "The API accepts football datasets, returns the Final Slip, Rejected Picks, "
        "Audit Logs, and stores local run history."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=PRODUCTION_SETTINGS.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-MB8-API-Key", "Authorization"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/pipeline-order")
def pipeline_order() -> dict[str, tuple[str, ...]]:
    return {"pipeline_order": get_pipeline_order()}


@app.post("/run")
async def run(file: UploadFile = File(...)) -> dict[str, object]:
    content = await file.read()
    df = read_dataset(io.BytesIO(content), filename=file.filename)
    result = run_stoic_pipeline(df, persist=True)
    return result.model_dump()


@app.post("/run-json")
def run_json(records: list[dict[str, object]]) -> dict[str, object]:
    result = run_stoic_pipeline(pd.DataFrame(records), persist=True)
    return result.model_dump()


@app.post(
    "/run-mb8",
    operation_id="runMb8FromUploadedDataset",
    summary="Run MB 8.0 from a CSV or Excel upload",
)
async def run_mb8(file: UploadFile = File(...), _: None = Depends(require_api_key)) -> dict[str, object]:
    content = await file.read()
    df = read_dataset(io.BytesIO(content), filename=file.filename)
    return run_mb8_application(df, source_filename=file.filename or "uploaded_dataset")


@app.post(
    "/run-mb8-json",
    operation_id="runMb8FromJsonRecords",
    summary="Run MB 8.0 from JSON records for Custom GPT Actions",
)
def run_mb8_json(request: MB8JsonRunRequest, _: None = Depends(require_api_key)) -> dict[str, object]:
    if request.records is not None:
        df = pd.DataFrame(request.records)
    elif request.csv_text is not None:
        df = pd.read_csv(io.StringIO(request.csv_text))
    elif request.xlsx_base64 is not None:
        df = pd.read_excel(io.BytesIO(base64.b64decode(request.xlsx_base64)))
    else:
        raise HTTPException(status_code=422, detail="Provide records, csv_text, or xlsx_base64.")
    return run_mb8_application(df, source_filename=request.source_filename)


@app.get(
    "/runs",
    operation_id="listMb8Runs",
    summary="List MB 8.0 run history",
)
def runs(limit: int = 25, _: None = Depends(require_api_key)) -> dict[str, object]:
    return {"runs": list_run_history(limit=limit)}


@app.get(
    "/runs/{run_id}",
    operation_id="getMb8Run",
    summary="Get one MB 8.0 run with full result payload",
)
def run_detail(run_id: str, _: None = Depends(require_api_key)) -> dict[str, object]:
    run_record = get_run_history(run_id)
    if run_record is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run_record


@app.get(
    "/runs/{run_id}/download.csv",
    operation_id="downloadMb8RunCsv",
    summary="Download a combined Final Slip and Rejected Picks CSV",
)
def download_run_csv(run_id: str, _: None = Depends(require_api_key)) -> Response:
    run_record = get_run_history(run_id)
    if run_record is None:
        raise HTTPException(status_code=404, detail="Run not found")
    result = dict(run_record["result"]).get("result", {})
    return Response(
        content=combined_report_csv_bytes(result),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{run_id}_mb8_report.csv"'},
    )


@app.get(
    "/runs/{run_id}/download.pdf",
    operation_id="downloadMb8RunPdf",
    summary="Download an MB 8.0 PDF report",
)
def download_run_pdf(run_id: str, _: None = Depends(require_api_key)) -> Response:
    run_record = get_run_history(run_id)
    if run_record is None:
        raise HTTPException(status_code=404, detail="Run not found")
    result = dict(run_record["result"]).get("result", {})
    return Response(
        content=pdf_report_bytes(result, run_id=run_id),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{run_id}_mb8_report.pdf"'},
    )


@app.get(
    "/custom-gpt-openapi.json",
    operation_id="getCustomGptOpenApiSchema",
    summary="Get the OpenAPI schema designed for Custom GPT Actions",
)
def custom_gpt_openapi(base_url: str | None = None) -> dict[str, object]:
    return custom_gpt_openapi_schema(base_url=base_url or PRODUCTION_SETTINGS.public_base_url)
