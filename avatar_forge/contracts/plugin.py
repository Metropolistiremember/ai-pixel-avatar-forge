"""PixelPlugin base class + PluginRecord dataclass."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from avatar_forge.contracts.jobs import RenderJob, RenderResult
from avatar_forge.contracts.manifest import PluginManifest

if TYPE_CHECKING:
    from avatar_forge.core.host import ForgeHost


@dataclass
class PluginRecord:
    entry_point_name: str
    module: str | None = None
    manifest: PluginManifest | None = None
    error: str | None = None
    tags: list[str] = field(default_factory=list)


class PixelPlugin(ABC):
    """Base class every avatar plugin inherits. Host lifecycle is explicit."""

    manifest: PluginManifest

    def on_load(self, host: "ForgeHost") -> None:
        """Called once after manifest validation. Store `host` if you need it."""

    def on_unload(self) -> None:
        """Release GPU buffers, temp files, threads."""

    @abstractmethod
    def render(self, job: RenderJob) -> RenderResult:
        """Produce one avatar frame (or a batch) for `job`."""

    def describe(self) -> str:
        m = self.manifest
        return f"{m.name} v{m.version} ({m.kind}) — {m.description}"