"""PluginLoader — resolves entry points, validates manifests, imports safely."""
from __future__ import annotations

from importlib import metadata

from avatar_forge.contracts.manifest import PluginManifest, ManifestError
from avatar_forge.contracts.plugin import PixelPlugin, PluginRecord
from avatar_forge.contracts.version import is_compatible
from avatar_forge.core.registry import PluginRegistry
from avatar_forge.utils.logging import get_logger

log = get_logger(__name__)

ENTRY_GROUP = "avatar_forge.plugins"


class PluginLoader:
    def __init__(self, registry: PluginRegistry) -> None:
        self.registry = registry

    def load_all(self, host: object) -> tuple[list[PixelPlugin], list[PluginRecord]]:
        loaded: list[PixelPlugin] = []
        failed: list[PluginRecord] = []

        for record in self.registry.records:
            try:
                plugin = self._instantiate(record)
            except Exception as exc:  # noqa: BLE001 — one bad plugin must not kill the host
                record.error = f"{type(exc).__name__}: {exc}"
                log.warning("plugin %s failed: %s", record.entry_point_name, record.error)
                failed.append(record)
                continue

            manifest = plugin.manifest
            if not is_compatible(manifest.api):
                record.error = f"api {manifest.api} incompatible with host"
                log.warning("plugin %s skipped: %s", manifest.id, record.error)
                failed.append(record)
                continue

            plugin.on_load(host)  # type: ignore[arg-type]
            loaded.append(plugin)
            log.info("loaded plugin %s v%s", manifest.id, manifest.version)

        return loaded, failed

    def _instantiate(self, record: PluginRecord) -> PixelPlugin:
        ep = next(
            (e for e in metadata.entry_points(group=ENTRY_GROUP)
             if e.name == record.entry_point_name),
            None,
        )
        if ep is None:
            raise ManifestError(f"entry point vanished: {record.entry_point_name}")
        obj = ep.load()
        plugin = obj() if isinstance(obj, type) else obj
        if not isinstance(plugin, PixelPlugin):
            raise ManifestError(f"{record.entry_point_name} is not a PixelPlugin")
        return plugin