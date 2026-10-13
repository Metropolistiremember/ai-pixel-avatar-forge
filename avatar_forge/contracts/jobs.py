"""Render job + result shapes shared across host and plugins."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RenderJob:
    job_id: str
    prompt: str
    style_pack: str
    size: int = 32                # pixel grid edge, 16/32/64/128
    seed: int = 0
    palette: str = "auto"
    steps: int = 24
    uses_gpu: bool = True
    out_dir: Path = Path("output")
    extras: dict[str, Any] = field(default_factory=dict)


@dataclass
class RenderResult:
    job_id: str
    frames: list[Path]
    elapsed_ms: int
    backend: str
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.frames)
</｜｜DSML｜｜ parameter>