from __future__ import annotations


def ecosystem_rule(ecosystem_type: str, pgce: float) -> tuple[bool, str]:
    if ecosystem_type == "COMPRESSION" and pgce > 0.62:
        return False, "Compression ecosystem with excessive PGCE risk"
    return True, "Ecosystem rule passed"

