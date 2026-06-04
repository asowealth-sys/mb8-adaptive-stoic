from __future__ import annotations


def yes_no_protocol(required_answers: dict[str, bool]) -> tuple[bool, str]:
    failed = [name for name, answer in required_answers.items() if not answer]
    if failed:
        return False, f"YES/NO Protocol failed: {', '.join(failed)}"
    return True, "All required YES/NO controls passed"

