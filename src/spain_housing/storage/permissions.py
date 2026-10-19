"""Source/capture permissions scoped independently to each artifact component."""

from collections.abc import Iterable
from typing import Literal

from spain_housing.models.dataset import CaptureRecord, SourceDecision, UsageScope


def validate_source_use(decision: SourceDecision, kind: Literal["observed", "synthetic"]) -> None:
    if decision.local_use != "permitted":
        raise ValueError(
            f"source local acquisition/use is {decision.local_use}: {decision.source_id}"
        )
    if kind == "observed" and (
        decision.source_id.startswith("synthetic:")
        or decision.primary_url is None
        or decision.terms_url is None
    ):
        raise ValueError("observed sources require real URLs and usage evidence")
    if kind == "synthetic" and not decision.source_id.startswith("synthetic:"):
        raise ValueError("synthetic release cannot include real source decisions")


def validate_capture_permission(
    capture: CaptureRecord, decision: SourceDecision, kind: Literal["observed", "synthetic"]
) -> None:
    validate_source_use(decision, kind)
    if (
        capture.source_id != decision.source_id
        or capture.permission_reference != decision.evidence_reference
    ):
        raise ValueError("capture references an unknown source/permission decision")
    if (capture.route == "synthetic_fixture") != (kind == "synthetic"):
        raise ValueError("synthetic/observed capture mixing is prohibited")
    if kind == "observed" and capture.primary_url is None:
        raise ValueError("observed capture requires a primary URL")


def least_permissive(scopes: Iterable[UsageScope]) -> UsageScope:
    selected = set(scopes)
    return (
        "restricted"
        if "restricted" in selected
        else "unresolved"
        if "unresolved" in selected
        else "permitted"
    )


def redistribution_scope(decisions: Iterable[SourceDecision]) -> UsageScope:
    return least_permissive(source.redistribution for source in decisions)
