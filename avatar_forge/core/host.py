"""ForgeHost — owns the registry, the render queue, and the asset cache."""
from __future__ import annotations

from pathlib import Path

from avatar_forge.contracts.plugin import PixelPlugin, PluginRecord
from avatar_forge.core.loader import PluginLoader
from avatar_forge.core.registry import PluginRegistry
from avatar_forge.core.scheduler import RenderScheduler
from avatar_forge.services.asset_cache import AssetCache
from avatar_forge.services.settings import ForgeSettings
from avatar_forge.utils.logging import get_logger

log = get_logger(__name__)


class ForgeHost:
    """Central object every plugin talks to. Plugins never see each other."""

    def __init__(self, settings: ForgeSettings) -> None:
        self.settings = settings
        self.registry = PluginRegistry.discover()
        self.loader = PluginLoader(self.registry)
        self.cache = AssetCache(root=Path(settings.cache_dir))
        self.scheduler = RenderScheduler(max_workers=settings.render_workers)
        self._loaded: dict[str, PixelPlugin] = {}

    def load_plugins(self) -> tuple[list[str], list[PluginRecord]]:
        loaded, failed = self.loader.load_all(self)
        for plugin in loaded:
            self._loaded[plugin.manifest.id] = plugin
        return [p.manifest.id for p in loaded], failed

    def plugin(self, plugin_id: str) -> PixelPlugin:
        try:
            return self._loaded[plugin_id]
        except KeyError as exc:
            raise KeyError(f"plugin not loaded: {plugin_id}") from exc

    def shutdown(self) -> None:
        self.scheduler.drain()
        for plugin in self._loaded.values():
            plugin.on_unload()
        self._loaded.clear()