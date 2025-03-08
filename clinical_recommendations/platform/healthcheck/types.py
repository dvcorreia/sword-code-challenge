from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Mapping, Optional, Sequence, TypeAlias

JSON: TypeAlias = (
    Mapping[str, "JSON"] | Sequence["JSON"] | str | int | float | bool | None
)


@dataclass(frozen=True)
class Healthcheck:
    message: str
    error: Optional[dict] = None  # dict | None seems unsupported by pydantic in py312

    def dict(self) -> dict:
        return asdict(self)

    def json(self) -> str:
        return json.dumps(self.dict())
