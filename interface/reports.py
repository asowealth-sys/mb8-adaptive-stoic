from __future__ import annotations

import json
from datetime import datetime
from textwrap import wrap

import pandas as pd


def to_csv_bytes(rows: list[dict[str, object]]) -> bytes:
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8")


def audit_to_json_bytes(audit_logs: list[dict[str, object]]) -> bytes:
    return json.dumps(audit_logs, indent=2).encode("utf-8")


def combined_report_csv_bytes(result: dict[str, object]) -> bytes:
    final_slip = pd.DataFrame(result.get("final_slip", []))
    rejected = pd.DataFrame(result.get("rejected_picks", []))
    final_slip.insert(0, "Report Section", "Final Slip")
    rejected.insert(0, "Report Section", "Rejected Picks")
    return pd.concat([final_slip, rejected], ignore_index=True, sort=False).to_csv(index=False).encode("utf-8")


def _pdf_escape(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _pdf_text_lines(result: dict[str, object], run_id: str | None = None) -> list[str]:
    lines = [
        "MB 8.0 Adaptive STOIC Report",
        f"Run ID: {run_id or 'unsaved'}",
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "Final Slip",
    ]
    final_slip = result.get("final_slip", [])
    if final_slip:
        for item in final_slip:
            lines.extend(
                wrap(
                    f"{item.get('Match', '')} | {item.get('League', '')} | "
                    f"{item.get('Market Pick', '')} | Odds {item.get('Odds', '')} | "
                    f"{item.get('Magic Check Status', '')} | {item.get('Reason', '')}",
                    width=92,
                )
            )
    else:
        lines.append("No final slip picks.")
    lines.extend(["", "Rejected Picks"])
    rejected = result.get("rejected_picks", [])
    if rejected:
        for item in rejected:
            lines.extend(
                wrap(
                    f"{item.get('Match', '')} | {item.get('League', '')} | "
                    f"{item.get('Failed Layer', '')} | {item.get('Rejection Reason', '')}",
                    width=92,
                )
            )
    else:
        lines.append("No rejected picks.")
    return lines


def pdf_report_bytes(result: dict[str, object], run_id: str | None = None) -> bytes:
    lines = _pdf_text_lines(result, run_id)
    text_ops: list[str] = ["BT", "/F1 10 Tf", "40 780 Td", "14 TL"]
    for index, line in enumerate(lines[:52]):
        if index:
            text_ops.append("T*")
        text_ops.append(f"({_pdf_escape(line)}) Tj")
    text_ops.append("ET")
    stream = "\n".join(text_ops).encode("latin-1", errors="replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n".encode(
            "ascii"
        )
    )
    return bytes(pdf)
