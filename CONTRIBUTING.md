# Contributing to ai-pixel-avatar-forge

Thanks for wanting to forge pixels with us. This repo is the desktop host for
generating AI pixel-art avatars (PFPs) from a prompt plus a style pack. The
host is thin; almost everything interesting lives in a plugin.

## Ground rules

1. **The host stays dumb.** `avatar_forge/core/` never imports a concrete
   plugin. If you need host behavior changed, change a contract in
   `avatar_forge/contracts/` first, then update the host, then update plugins.
2. **Every plugin is a wheel.** Built-ins live under `avatar_forge/extensions/`
   but are still registered through the `avatar_forge.plugins` entry-point
   group. No hard-coded imports in the loader.
3. **Contracts are versioned.** Bump `PLUGIN_API_VERSION` in
   `avatar_forge/contracts/version.py` when you break a contract. Host refuses
   to load plugins declaring an incompatible major.
4. **Tests run headless.** `pytest -q` must pass with no display attached.
   Qt tests use `pytest-qt` and `QT_QPA_PLATFORM=offscreen`.

## Dev setup

```bash
python -m venv .venv
. .venv/Scripts/activate      # Windows
pip install -e ".[dev,cpu]"
pytest -q
forge --list-plugins
```

For CUDA backends: `pip install -e ".[dev,cuda]"`.

## Plugin layout

```
avatar_forge/extensions/<your_pack>/
    plugin.py          # subclass of PixelPlugin, declares manifest
    manifest.toml      # id, name, version, api, capabilities
    __init__.py
```

Register in `pyproject.toml` under `[project.entry-points."avatar_forge.plugins"]`.

## Style

- Ruff line length 100, mypy strict on `avatar_forge/`.
- No bare `except:`. Catch `ForgeError` subclasses or re-raise.
- Log through `avatar_forge.utils.logging.get_logger(__name__)`.

## PR checklist

- [ ] `ruff check .` clean
- [ ] `mypy avatar_forge` clean
- [ ] `pytest -q` green
- [ ] New plugin? Added to entry-points + a smoke test in `tests/`
- [ ] Contract change? `PLUGIN_API_VERSION` bumped + migration note in the PR body