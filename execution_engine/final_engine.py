from __future__ import annotations


def final_slip_row(candidate: dict[str, object]) -> dict[str, object]:
    return {
        "Match": candidate["match"],
        "League": candidate["league"],
        "Market Pick": candidate["market_pick"],
        "Odds": candidate["odds"],
        "Ecosystem Type": candidate["ecosystem_type"],
        "MVSS Rating": candidate["mvss_rating"],
        "STOIC Score": candidate["stoic_score"],
        "Survivability Rating": candidate["survivability_rating"],
        "Slip Label": candidate["slip_label"],
        "Magic Check Status": candidate["magic_check_status"],
        "Final Decision": candidate["final_decision"],
        "Reason": candidate["reason"],
        "Audit Trail ID": candidate["audit_trail_id"],
    }


def rejected_row(candidate: dict[str, object]) -> dict[str, object]:
    return {
        "Match": candidate.get("match", ""),
        "League": candidate.get("league", ""),
        "Initial Market": candidate.get("market_pick", candidate.get("market", "")),
        "Failed Layer": candidate.get("failed_layer", "UNKNOWN"),
        "Rejection Reason": candidate.get("rejection_reason", candidate.get("reason", "Rejected by deterministic rule")),
        "Risk Flags": ", ".join(candidate.get("risk_flags", [])),
        "Audit Trail ID": candidate.get("audit_trail_id", ""),
    }

