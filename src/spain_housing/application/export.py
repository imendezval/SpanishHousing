"""Economic run encoding, safe local publication and exact saved-input replay."""

import csv
import io
import json
import os
import shutil
import tempfile
from pathlib import Path

from spain_housing.models.contracts import MarketData
from spain_housing.models.evaluation import EvaluationContext
from spain_housing.models.results import RunResult

from .evaluate import evaluate_scenario


def run_json(run: RunResult) -> str:
    return (
        json.dumps(
            run.model_dump(mode="json"),
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
        + "\n"
    )


def summary_csv(run: RunResult) -> str:
    savings_fields = ("ending_savings_eur", "usable_savings_eur", "viability")
    purchase_fields = (
        "savings_price_limit_eur",
        "mortgage_price_limit_eur",
        "maximum_price_eur",
        "binding_constraint",
        "target_price_eur",
        "target_loan_eur",
        "target_upfront_cash_eur",
        "target_monthly_payment_eur",
        "target_cash_shortfall_eur",
        "target_payment_shortfall_eur",
    )
    fields = [
        "saving_level",
        "saving_code",
        "buying_level",
        "buying_code",
        "calculation_status",
        "explanation",
        *savings_fields,
        *purchase_fields,
        "unbounded_cash_constraint",
        "affordable_area_m2",
        "affordable_area_status",
        "affordable_area_reason",
        "target_affordability_ratio",
        "target_affordability_status",
        "target_affordability_reason",
        "dataset_kind",
        "dataset_readiness",
        "dataset_release_id",
        "model_version",
        "code_version",
    ]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fields, lineterminator="\n")
    writer.writeheader()
    for result in run.results:
        row: dict[str, object] = {
            "saving_level": result.saving_location.level,
            "saving_code": result.saving_location.code,
            "buying_level": result.buying_location.level,
            "buying_code": result.buying_location.code,
            "calculation_status": result.calculation_status,
            "explanation": result.explanation,
            "unbounded_cash_constraint": (
                None if result.purchase is None else result.purchase.savings_price_limit_eur is None
            ),
            "affordable_area_m2": result.affordable_area_m2.value,
            "affordable_area_status": result.affordable_area_m2.status,
            "affordable_area_reason": result.affordable_area_m2.reason,
            "target_affordability_ratio": result.target_affordability_ratio.value,
            "target_affordability_status": result.target_affordability_ratio.status,
            "target_affordability_reason": result.target_affordability_ratio.reason,
            "dataset_kind": run.evaluation_context.kind if run.evaluation_context else None,
            "dataset_readiness": run.evaluation_context.readiness
            if run.evaluation_context
            else None,
            "dataset_release_id": run.dataset_release_id,
            "model_version": run.model_version,
            "code_version": run.code_version,
        }
        row.update(
            {
                name: getattr(result.savings, name) if result.savings else None
                for name in savings_fields
            }
        )
        row.update(
            {
                name: getattr(result.purchase, name) if result.purchase else None
                for name in purchase_fields
            }
        )
        writer.writerow(row)
    return output.getvalue()


def export_run(run: RunResult, output_dir: Path) -> Path:
    """Publish both files together; refuse any existing destination or writer lock."""
    validated = RunResult.model_validate(run.model_dump(mode="json"))
    payloads = {"run.json": run_json(validated), "summary.csv": summary_csv(validated)}
    if os.path.lexists(output_dir):
        raise ValueError(f"output directory already exists: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    lock = output_dir.parent / f".{output_dir.name}.lock"
    # Cooperative exporters cannot race to replace an empty output directory.
    with lock.open("x"):
        pass
    staging: Path | None = None
    try:
        if os.path.lexists(output_dir):
            raise ValueError(f"output directory already exists: {output_dir}")
        staging = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.", dir=output_dir.parent))
        for name, payload in payloads.items():
            (staging / name).write_text(payload, encoding="utf-8", newline="")
        if os.path.lexists(output_dir):
            raise ValueError(f"output directory already exists: {output_dir}")
        staging.rename(output_dir)
        staging = None
    finally:
        if staging is not None:
            shutil.rmtree(staging)
        lock.unlink()
    return output_dir


def replay_run(
    saved: RunResult, *, market_data: MarketData, context: EvaluationContext
) -> RunResult:
    if saved.evaluation_context is None or saved.runtime_evidence is None:
        raise ValueError(
            "legacy run lacks evaluation/runtime evidence; exact replay is unavailable"
        )
    if saved.dataset_release_id != context.release_id:
        raise ValueError("replay dataset release ID mismatch")
    current = evaluate_scenario(
        saved.resolved_scenario,
        market_data=market_data,
        context=context,
        mapped_locations=tuple(result.buying_location for result in saved.results),
    )
    for field in ("model_version", "code_version", "runtime_evidence"):
        if getattr(current, field) != getattr(saved, field):
            raise ValueError(f"replay {field} mismatch")
    if run_json(current) != run_json(saved):
        raise ValueError("replayed economic result differs from saved run")
    return current
