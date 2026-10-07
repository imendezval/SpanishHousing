"""Scalar checks shared by the public financial functions."""

import math


def nonnegative(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite nonnegative number")
    if value < 0:
        raise ValueError(f"{name} must be a finite nonnegative number")
    return float(value)


def finite_result(value: float, name: str) -> float:
    if not math.isfinite(value):
        raise ValueError(f"{name} is not finite for these inputs")
    return value
