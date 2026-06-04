from __future__ import annotations

import json

import pandas as pd

from app.config import SETTINGS
from app.database import init_db, save_audit_log
from data_layer.clean import clean_dataset
from data_layer.validators import missing_required_columns
from execution_engine.behavioral_ai import behavioral_flags
from execution_engine.cdc import apply_cdc_control, item_cdc_score
from execution_engine.dominance_stability import dominance_score
from execution_engine.ecosystem_engine import classify_ecosystem
from execution_engine.feature_engineering import profile_match
from execution_engine.final_engine import final_slip_row, rejected_row
from execution_engine.market_selection import select_market
from execution_engine.mvss import mvss_rating
from execution_engine.pgce_risk import pgce_score
from execution_engine.stoic_slip_scorer import slip_label, stoic_score, survivability_rating
from rules_engine.behavioral_filters import behavioral_filter
from rules_engine.dominance_gates import dominance_gate
from rules_engine.double_chance_gate import double_chance_integrity_gate
from rules_engine.ecosystem_rules import ecosystem_rule
from rules_engine.magic_check import magic_check
from rules_engine.rejection_logic import new_audit_trail, reject_candidate
from rules_engine.yes_no_protocol import yes_no_protocol
from schemas.result_schema import EngineResult


PIPELINE_ORDER = (
    "RAW_DATASET",
    "FEATURE_ENGINEERING_LAYER",
    "ECOSYSTEM_ENGINE",
    "DOMINANCE_AND_STABILITY_LAYER",
    "BEHAVIORAL_AI_LAYER",
    "PGCE_RISK_ENGINE",
    "MARKET_SELECTION_ENGINE",
    "MVSS_SCORING",
    "CDC",
    "STOIC_SLIP_SCORER",
    "MAGIC_CHECK",
    "FINAL_SLIP",
)


def get_pipeline_order() -> tuple[str, ...]:
    return PIPELINE_ORDER


def _base_candidate(row: pd.Series) -> dict[str, object]:
    audit = new_audit_trail()
    match = str(row.get("match", f"{row.get('home_team', '')} vs {row.get('away_team', '')}")).strip()
    return {
        "audit": audit,
        "audit_trail_id": audit.audit_trail_id,
        "match": match,
        "league": str(row.get("league", "")),
        "market": str(row.get("market", "")),
        "market_pick": str(row.get("market", "")),
        "odds": row.get("odds", ""),
        "risk_flags": [],
        "final_decision": "PENDING",
        "reason": "Pipeline started",
    }


def _reject_missing_columns(df: pd.DataFrame) -> EngineResult | None:
    missing = missing_required_columns(df)
    if not missing:
        return None
    audit = new_audit_trail()
    reason = f"Missing required columns: {', '.join(missing)}"
    audit.add("RAW_DATASET", "REJECT", reason)
    rejected = {
        "match": "",
        "league": "",
        "market": "",
        "market_pick": "",
        "failed_layer": "RAW_DATASET",
        "rejection_reason": reason,
        "reason": reason,
        "risk_flags": ["missing_required_data"],
        "audit_trail_id": audit.audit_trail_id,
    }
    return EngineResult(rejected_picks=[rejected_row(rejected)], audit_logs=[audit.model_dump()])


def _excluded_to_rejects(excluded: pd.DataFrame) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rejected: list[dict[str, object]] = []
    audits: list[dict[str, object]] = []
    for _, row in excluded.iterrows():
        candidate = _base_candidate(row)
        reason = str(row.get("exclusion_reason", "SRL/Friendly match detected"))
        candidate["risk_flags"] = ["srl_friendly_exclusion"]
        reject_candidate(candidate, "FEATURE_ENGINEERING_LAYER", reason)
        audits.append(candidate["audit"].model_dump())
        rejected.append(rejected_row(candidate))
    return rejected, audits


def run_stoic_pipeline(raw_df: pd.DataFrame, persist: bool = False) -> EngineResult:
    missing_result = _reject_missing_columns(raw_df)
    if missing_result:
        return missing_result

    cleaned, excluded = clean_dataset(raw_df)
    rejected_rows, audit_logs = _excluded_to_rejects(excluded)
    pre_cdc_candidates: list[dict[str, object]] = []

    for _, row in cleaned.iterrows():
        candidate = _base_candidate(row)
        audit = candidate["audit"]
        audit.add("RAW_DATASET", "PASS", "Raw record accepted for deterministic processing")

        if pd.isna(row.get("odds")):
            rejected = reject_candidate(candidate, "FEATURE_ENGINEERING_LAYER", "Required odds value is missing or invalid")
            rejected_rows.append(rejected_row(rejected))
            audit_logs.append(audit.model_dump())
            continue

        features = profile_match(row)
        audit.add("FEATURE_ENGINEERING_LAYER", "PASS", "Data cleaning, odds normalization, duplicate removal, SRL/Friendly exclusion, and match profiling completed", **features)

        ecosystem_type, ecosystem_quality = classify_ecosystem(row)
        candidate["ecosystem_type"] = ecosystem_type
        ecosystem_passed, ecosystem_reason = ecosystem_rule(ecosystem_type, pgce_score(row))
        audit.add("ECOSYSTEM_ENGINE", "PASS" if ecosystem_passed else "REJECT", ecosystem_reason, ecosystem_type=ecosystem_type)
        if not ecosystem_passed:
            rejected_rows.append(rejected_row(reject_candidate(candidate, "ECOSYSTEM_ENGINE", ecosystem_reason)))
            audit_logs.append(audit.model_dump())
            continue

        dominance = dominance_score(features)
        candidate["dominance_score"] = dominance
        dominance_passed, dominance_reason = dominance_gate(dominance)
        audit.add("DOMINANCE_AND_STABILITY_LAYER", "PASS" if dominance_passed else "REJECT", dominance_reason, dominance_score=dominance)
        if not dominance_passed:
            rejected_rows.append(rejected_row(reject_candidate(candidate, "DOMINANCE_AND_STABILITY_LAYER", dominance_reason)))
            audit_logs.append(audit.model_dump())
            continue

        flags = behavioral_flags(row)
        candidate["risk_flags"] = flags
        behavior_passed, behavior_reason = behavioral_filter(flags)
        audit.add("BEHAVIORAL_AI_LAYER", "PASS" if behavior_passed else "REJECT", behavior_reason, risk_flags=flags)
        if not behavior_passed:
            rejected_rows.append(rejected_row(reject_candidate(candidate, "BEHAVIORAL_AI_LAYER", behavior_reason)))
            audit_logs.append(audit.model_dump())
            continue

        pgce = pgce_score(row)
        candidate["pgce_score"] = pgce
        pgce_passed = pgce <= SETTINGS.pgce_max_risk
        pgce_reason = "PGCE risk within threshold" if pgce_passed else f"PGCE risk {pgce} above threshold {SETTINGS.pgce_max_risk}"
        audit.add("PGCE_RISK_ENGINE", "PASS" if pgce_passed else "REJECT", pgce_reason, pgce_score=pgce)
        if not pgce_passed:
            rejected_rows.append(rejected_row(reject_candidate(candidate, "PGCE_RISK_ENGINE", pgce_reason)))
            audit_logs.append(audit.model_dump())
            continue

        market_pick, market_reason = select_market(row, dominance, pgce)
        candidate["market_pick"] = market_pick
        double_passed, double_reason = double_chance_integrity_gate(market_pick, float(row.get("draw_risk", 0.35)))
        yes_no_passed, yes_no_reason = yes_no_protocol(
            {
                "market_supported": market_reason is None,
                "double_chance_integrity": double_passed,
                "audit_trail_present": bool(candidate["audit_trail_id"]),
            }
        )
        market_status = "PASS" if yes_no_passed else "REJECT"
        market_final_reason = yes_no_reason if market_reason is None and double_passed else market_reason or double_reason
        audit.add("MARKET_SELECTION_ENGINE", market_status, market_final_reason, market_pick=market_pick)
        if not yes_no_passed:
            rejected_rows.append(rejected_row(reject_candidate(candidate, "MARKET_SELECTION_ENGINE", market_final_reason)))
            audit_logs.append(audit.model_dump())
            continue

        mvss = mvss_rating(dominance, pgce, len(flags))
        candidate["mvss_rating"] = mvss
        audit.add("MVSS_SCORING", "PASS", f"MVSS classified as {mvss}", mvss_rating=mvss)

        cdc_risk = item_cdc_score(ecosystem_type, flags)
        candidate["cdc_risk"] = cdc_risk
        candidate["cdc_status"] = "PENDING"
        audit.add("CDC", "PASS", "Candidate sent through CDC correlation control", cdc_risk=cdc_risk)

        score = stoic_score(dominance, mvss, ecosystem_quality, pgce, cdc_risk)
        candidate["stoic_score"] = score
        candidate["survivability_rating"] = survivability_rating(score)
        candidate["slip_label"] = slip_label(score)
        audit.add("STOIC_SLIP_SCORER", "PASS", "STOIC slip scoring completed", stoic_score=score)
        pre_cdc_candidates.append(candidate)

    kept_candidates, cdc_rejections = apply_cdc_control(pre_cdc_candidates, SETTINGS.max_cdc_risk)
    for candidate in cdc_rejections:
        candidate["audit"].add("CDC", "REJECT", str(candidate["reason"]), cdc_risk=candidate.get("cdc_risk"))
        status, reason = magic_check(candidate)
        candidate["magic_check_status"] = status
        candidate["reason"] = reason
        candidate["rejection_reason"] = reason
        candidate["audit"].add("MAGIC_CHECK", status, reason)
        rejected_rows.append(rejected_row(candidate))
        audit_logs.append(candidate["audit"].model_dump())

    final_rows: list[dict[str, object]] = []
    for candidate in kept_candidates:
        status, reason = magic_check(candidate)
        candidate["magic_check_status"] = status
        candidate["final_decision"] = "PASS" if status == "PASS" else "REJECT"
        candidate["reason"] = reason
        candidate["audit"].add("MAGIC_CHECK", status, reason)
        if status == "PASS":
            candidate["audit"].add("FINAL_SLIP", "PASS", "Pick approved for final slip")
            final_rows.append(final_slip_row(candidate))
        else:
            candidate["failed_layer"] = "MAGIC_CHECK"
            candidate["rejection_reason"] = reason
            rejected_rows.append(rejected_row(candidate))
        audit_logs.append(candidate["audit"].model_dump())

    if persist:
        init_db()
        for audit in audit_logs:
            events = audit["events"]
            last = events[-1] if events else {"reason": "No audit events"}
            match = ""
            for event in events:
                if event["layer"] == "FEATURE_ENGINEERING_LAYER":
                    match = str(event["details"].get("match", ""))
            save_audit_log(
                str(audit["audit_trail_id"]),
                match,
                str(last["status"]),
                str(last["reason"]),
                json.dumps(audit),
            )

    return EngineResult(final_slip=final_rows, rejected_picks=rejected_rows, audit_logs=audit_logs)

