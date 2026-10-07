"""Actual installed calculation-source and runtime evidence, independent of Git."""

import hashlib
import platform
from importlib.metadata import version
from pathlib import Path

from spain_housing.models.evaluation import DependencyVersion, RuntimeEvidence

MODEL_VERSION = "finance-v1/scenario-v1"


def code_version() -> str:
    package = Path(__file__).resolve().parents[1]
    digest = hashlib.sha256()
    for path in sorted(package.rglob("*.py")):
        name = path.relative_to(package).as_posix().encode("utf-8")
        payload = path.read_bytes()
        digest.update(len(name).to_bytes(8, "big"))
        digest.update(name)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return f"spain-housing-{version('spain-housing')}/sha256-{digest.hexdigest()}"


def runtime_evidence() -> RuntimeEvidence:
    return RuntimeEvidence(
        python_version=platform.python_version(),
        dependencies=tuple(
            DependencyVersion(name=name, version=version(name))
            for name in sorted(("pydantic", "PyYAML", "shapely", "openpyxl"))
        ),
    )
