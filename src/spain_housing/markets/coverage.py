"""Deterministic aggregation only; storage owns coverage/lineage validation."""

from spain_housing.models.coverage import EvidenceCounts, ProfileCoverage, ReleaseCoverageReport
from spain_housing.models.dataset import (
    CoverageCell,
    CoverageSummary,
    LocationRecord,
    ReleasedObservation,
    ReleaseManifest,
)
from spain_housing.models.market import METRIC_UNITS


def coverage_report(
    manifest: ReleaseManifest,
    locations: tuple[LocationRecord, ...],
    cells: tuple[CoverageCell, ...],
    observations: tuple[ReleasedObservation, ...],
) -> ReleaseCoverageReport:
    """Project already validated cells; never invent missing rows or suitability."""
    recipe = manifest.recipe
    evidence = {
        (o.location.code, o.metric, o.period_start, o.period_end, o.segment): o.evidence_kind
        for row in observations
        for o in (row.observation,)
    }
    profiles = []
    for profile in sorted(recipe.profiles, key=lambda p: p.profile_id):
        selected = tuple(c for c in cells if c.profile_id == profile.profile_id)
        kinds = [
            evidence[
                (
                    c.location_code,
                    profile.metric,
                    profile.period_start,
                    profile.period_end,
                    profile.segment,
                )
            ]
            for c in selected
            if c.status == "available"
        ]
        profiles.append(
            ProfileCoverage(
                profile=profile,
                unit=METRIC_UNITS[profile.metric],
                counts=CoverageSummary(
                    expected=len(selected),
                    available=sum(c.status == "available" for c in selected),
                    missing=sum(c.status == "missing" for c in selected),
                    unsupported=sum(c.status == "unsupported" for c in selected),
                ),
                evidence=EvidenceCounts(
                    observed=kinds.count("observed"),
                    estimated=kinds.count("estimated"),
                    synthetic=kinds.count("synthetic"),
                ),
            )
        )
    return ReleaseCoverageReport(
        release_id=manifest.release_id,
        kind=manifest.kind,
        readiness=manifest.readiness,
        registry_version=recipe.geography.registry_version,
        boundary_version=recipe.geography.boundary_version,
        attribution=recipe.geography.attribution,
        limitations=recipe.limitations,
        redistribution=manifest.redistribution,
        decisions=tuple(sorted(recipe.decisions, key=lambda d: d.source_id)),
        captures=tuple(sorted(recipe.captures, key=lambda c: c.capture_id)),
        locations=tuple(sorted(locations, key=lambda loc: loc.location.code)),
        profiles=tuple(profiles),
        cells=tuple(sorted(cells, key=lambda c: (c.location_code, c.profile_id))),
        counts=manifest.coverage,
        evidence=EvidenceCounts(
            observed=sum(p.evidence.observed for p in profiles),
            estimated=sum(p.evidence.estimated for p in profiles),
            synthetic=sum(p.evidence.synthetic for p in profiles),
        ),
    )
