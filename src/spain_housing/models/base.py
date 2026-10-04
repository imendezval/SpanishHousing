"""Shared validated primitives for public records."""

import re
from datetime import date, datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)


def parse_month(value: Any) -> date:
    if isinstance(value, datetime):
        raise ValueError("expected a calendar month, not a timestamp")
    if isinstance(value, str):
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
            raise ValueError("expected an ISO date YYYY-MM-01")
        try:
            value = date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("expected an ISO date YYYY-MM-01") from exc
    if not isinstance(value, date) or value.day != 1:
        raise ValueError("expected the first day of a calendar month")
    return value


Month = Annotated[date, BeforeValidator(parse_month)]


def _schema_tag(value: Any) -> Any:
    if isinstance(value, bool):
        raise ValueError("schema_version must be integer 1")
    return value


SchemaVersion = Annotated[Literal[1], BeforeValidator(_schema_tag)]
NonNegativeFinite = Annotated[float, Field(strict=True, allow_inf_nan=False, ge=0)]
PositiveFinite = Annotated[float, Field(strict=True, allow_inf_nan=False, gt=0)]
Money = NonNegativeFinite
FiniteAmount = Annotated[float, Field(strict=True, allow_inf_nan=False)]
PositiveMoney = PositiveFinite
Ratio = Annotated[float, Field(strict=True, allow_inf_nan=False, ge=0, le=1)]
PositiveRatio = Annotated[float, Field(strict=True, allow_inf_nan=False, gt=0, le=1)]
Offset = Annotated[int, Field(strict=True, ge=0)]
PositiveInt = Annotated[int, Field(strict=True, gt=0)]


def add_months(start: date, count: int) -> date:
    year, month = divmod(start.year * 12 + start.month - 1 + count, 12)
    return date(year, month + 1, 1)
