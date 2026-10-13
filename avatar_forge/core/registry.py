"""PluginRegistry — discovers entry points and caches their manifests."""
from __future__ import annotations

from dataclasses import dataclass, field
from importlib import metadata

from avatar_forge.contracts.manifest import PluginManifest, ManifestError
from avatar_forge.contracts.plugin import PluginRecord
from avatar_forge.utils.logging import get_logger

log = get_logger(__name__)
ENTRY_GROUP = "avatar_forge.plugins"


@dataclass
class PluginRegistry:
    records: list[PluginRecord] = field(default_factory=list)

    @classmethod
    def discover(cls) -> "PluginRegistry":
        reg = cls()
        for ep in metadata.entry_points(group=ENTRY_GROUP):
            record = PluginRecord(entry_point_name=ep.name, module=ep.value)
            try:
                obj = ep.load()
                manifest = getattr(obj, "manifest", None)
                if callable(manifest):
                    manifest = manifest()
                if isinstance(manifest, PluginManifest):
                    record.manifest = manifest
            except Exception as exc:  # noqa: BLE001
                record.error = f"discovery: {type(exc).__name__}: {exc}"
                log.debug("discovery failed for %s: %s", ep.name, record.error)
            reg.records.append(record)
        return reg

    def find(self, plugin_id: str) -> PluginRecord | None:
        for rec in self.records:
            if rec.manifest and rec.manifest.id == plugin_id:
                return rec
        return None

    def validate_all(self) -> list[str]:
        problems: list[str] = []
        for rec in self.records:
            if rec.manifest is None:
                problems.append(f"{rec.entry_point_name}: no manifest ({rec.error})")
        return problems