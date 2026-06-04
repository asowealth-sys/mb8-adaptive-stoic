from __future__ import annotations


CRITICAL_FLAGS = {"emotional_chaos", "motivation_distortion"}


def behavioral_filter(flags: list[str]) -> tuple[bool, str]:
    critical = sorted(CRITICAL_FLAGS.intersection(flags))
    if critical:
        return False, f"Critical behavioral flags detected: {', '.join(critical)}"
    return True, "Behavioral filters passed"

