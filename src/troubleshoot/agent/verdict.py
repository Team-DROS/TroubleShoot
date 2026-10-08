"""Deterministic verification. Fresh symptom checks decide the verdict; an
execution "ok", a zero exit code or a model saying "fixed" never does."""

from dataclasses import dataclass

EXECUTION_STATUSES = ("ok", "blocked", "failed", "cancelled")
VERDICTS = ("resolved", "partial", "unresolved", "cancelled", "error")


@dataclass(frozen=True)
class Check:
    name: str
    expected: str
    actual: str
    passed: bool
    symptom: bool = True      # tied to the user's original symptom, not just tool success

    def __post_init__(self):
        if type(self.passed) is not bool or type(self.symptom) is not bool:
            raise ValueError("Check flags must be boolean")


@dataclass(frozen=True)
class Verdict:
    verdict: str
    checks: tuple[Check, ...]
    limitations: tuple[str, ...]

    def to_dict(self) -> dict:
        return {"verdict": self.verdict, "checks": [c.__dict__ for c in self.checks],
                "limitations": list(self.limitations)}


def judge(execution_status: str, checks, model_opinion: str | None = None) -> Verdict:
    """Combine execution status and fresh checks. A model opinion may only
    downgrade a deterministic result, never upgrade it."""
    if execution_status not in EXECUTION_STATUSES:
        raise ValueError("Unknown execution status")
    checks = tuple(checks)
    notes = []
    if execution_status == "cancelled":
        return Verdict("cancelled", checks, ("Action was cancelled",))
    if execution_status in ("blocked", "failed"):
        notes.append(f"Action {execution_status}")
    symptom = [c for c in checks if c.symptom]
    if not symptom:
        notes.append("No fresh symptom check was available, so the fix is not confirmed")
        return Verdict("unresolved", checks, tuple(notes))
    passed = sum(c.passed for c in symptom)
    if passed == len(symptom) and all(c.passed for c in checks):
        verdict = "resolved" if execution_status == "ok" else "partial"
    elif passed:
        verdict = "partial"
    else:
        verdict = "unresolved"
    if execution_status == "ok" and verdict != "resolved":
        notes.append("The action ran but the symptom checks did not all pass")
    if model_opinion in ("partial", "unresolved") and verdict == "resolved":
        verdict = "partial"
        notes.append("Model analysis disagreed with the checks; verdict lowered to partial")
    return Verdict(verdict, checks, tuple(notes))
