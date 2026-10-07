"""Scalar checks shared by the public financial functions."""

import math


def nonnegative(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite nonnegative number")
    try:
        number = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} must be a finite nonnegative number") from exc
    if not math.isfinite(number) or number < 0:
        raise ValueError(f"{name} must be a finite nonnegative number")
    return number


def positive(value: float, name: str) -> float:
    result = nonnegative(value, name)
    if result == 0:
        raise ValueError(f"{name} must be a finite positive number")
    return result


def finite_result(value: float, name: str) -> float:
    if not math.isfinite(value):
        raise ValueError(f"{name} is not finite for these inputs")
    return value
