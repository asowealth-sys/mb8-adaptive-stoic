from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from app.database import get_run_history, init_db, list_run_history
from app.services import run_mb8_application
from data_layer.ingest import read_dataset
from interface.reports import (
    audit_to_json_bytes,
    combined_report_csv_bytes,
    pdf_report_bytes,
    to_csv_bytes,
)

st.set_page_config(page_title="MB 8.0 Adaptive STOIC", layout="wide")
init_db()
st.title("MB 8.0 Adaptive STOIC")

if "mb8_payload" not in st.session_state:
    st.session_state["mb8_payload"] = None

upload_tab, history_tab = st.tabs(["Run MB 8.0", "Run History"])

with upload_tab:
    uploaded = st.file_uploader(
        "Drag and drop CSV or Excel dataset",
        type=["csv", "xls", "xlsx"],
        accept_multiple_files=False,
    )

    if uploaded and st.button("Run MB 8.0 Adaptive STOIC", type="primary"):
        try:
            df = read_dataset(uploaded, filename=uploaded.name)
            st.session_state["mb8_payload"] = run_mb8_application(df, source_filename=uploaded.name)
        except Exception as exc:
            st.error(str(exc))

    payload = st.session_state["mb8_payload"]
    if payload:
        result = payload["result"]
        final_slip = result["final_slip"]
        rejected_picks = result["rejected_picks"]
        audit_logs = result["audit_logs"]

        metric_cols = st.columns(4)
        metric_cols[0].metric("Run ID", payload["run_id"])
        metric_cols[1].metric("Rows", payload["total_rows"])
        metric_cols[2].metric("Final Slip", payload["final_count"])
        metric_cols[3].metric("Rejected", payload["rejected_count"])

        final_tab, rejected_tab, audit_tab, download_tab = st.tabs(
            ["Final Slip", "Rejected Picks", "Audit Log", "Downloads"]
        )

        with final_tab:
            st.dataframe(pd.DataFrame(final_slip), use_container_width=True, hide_index=True)

        with rejected_tab:
            st.dataframe(pd.DataFrame(rejected_picks), use_container_width=True, hide_index=True)

        with audit_tab:
            audit_ids = [item["audit_trail_id"] for item in audit_logs]
            selected_audit_id = st.selectbox("Audit Trail ID", audit_ids) if audit_ids else None
            selected_audit = next(
                (item for item in audit_logs if item["audit_trail_id"] == selected_audit_id),
                None,
            )
            st.json(selected_audit or audit_logs)

        with download_tab:
            st.download_button(
                "Download Final Slip CSV",
                to_csv_bytes(final_slip),
                file_name=f"{payload['run_id']}_final_slip.csv",
                mime="text/csv",
            )
            st.download_button(
                "Download Combined CSV",
                combined_report_csv_bytes(result),
                file_name=f"{payload['run_id']}_mb8_report.csv",
                mime="text/csv",
            )
            st.download_button(
                "Download audit log",
                audit_to_json_bytes(audit_logs),
                file_name=f"{payload['run_id']}_audit_log.json",
                mime="application/json",
            )
            st.download_button(
                "Download PDF",
                pdf_report_bytes(result, run_id=payload["run_id"]),
                file_name=f"{payload['run_id']}_mb8_report.pdf",
                mime="application/pdf",
            )

with history_tab:
    runs = list_run_history(limit=50)
    if not runs:
        st.info("No runs saved yet.")
    else:
        st.dataframe(pd.DataFrame(runs), use_container_width=True, hide_index=True)
        run_ids = [run["run_id"] for run in runs]
        selected_run_id = st.selectbox("Open saved run", run_ids)
        selected_run = get_run_history(selected_run_id)
        if selected_run:
            st.json(
                {
                    "run_id": selected_run["run_id"],
                    "source_filename": selected_run["source_filename"],
                    "total_rows": selected_run["total_rows"],
                    "final_count": selected_run["final_count"],
                    "rejected_count": selected_run["rejected_count"],
                    "created_at": selected_run["created_at"],
                }
            )
            result = selected_run["result"]["result"]
            st.download_button(
                "Download saved run PDF",
                pdf_report_bytes(result, run_id=selected_run_id),
                file_name=f"{selected_run_id}_mb8_report.pdf",
                mime="application/pdf",
            )
            st.download_button(
                "Download saved run JSON",
                json.dumps(selected_run, indent=2).encode("utf-8"),
                file_name=f"{selected_run_id}_mb8_run.json",
                mime="application/json",
            )
