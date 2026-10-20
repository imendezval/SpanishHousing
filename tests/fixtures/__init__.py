"""Small fixture data and its explicit repository paths; no production imports."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PILOT = Path(__file__).resolve().parent / "synthetic/pilot"
