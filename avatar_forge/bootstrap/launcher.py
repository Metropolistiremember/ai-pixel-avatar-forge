"""Desktop entry point. Boots the plugin host, opens the Qt shell."""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from avatar_forge.core.host import ForgeHost
from avatar_forge.services.settings import ForgeSettings
from avatar_forge.ui.main_window import MainWindow
from avatar_forge.utils.logging import configure_logging, get_logger

log = get_logger(__name__)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv if argv is None else argv)
    settings = ForgeSettings.load()
    configure_logging(settings.log_level, settings.log_dir)
    log.info("forge booting v%s", _version())

    app = QApplication(argv)
    app.setApplicationName("ai-pixel-avatar-forge")

    host = ForgeHost(settings=settings)
    loaded, failed = host.load_plugins()
    log.info("plugins loaded=%d failed=%d", len(loaded), len(failed))

    window = MainWindow(host=host)
    window.show()
    return app.exec()


def _version() -> str:
    from avatar_forge import __version__
    return __version__


if __name__ == "__main__":
    raise SystemExit(main())