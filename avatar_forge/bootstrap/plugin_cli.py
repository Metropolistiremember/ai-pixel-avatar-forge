"""`forge-plugin` CLI: inspect, validate, and scaffold plugins."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from avatar_forge.core.registry import PluginRegistry
from avatar_forge.contracts.manifest import PluginManifest, ManifestError


def _cmd_list(_: argparse.Namespace) -> int:
    registry = PluginRegistry.discover()
    for rec in registry.records:
        flag = "ok" if rec.manifest is not None else "BAD"
        print(f"[{flag}] {rec.entry_point_name:24} {rec.module or '?'}")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.manifest)
    try:
        manifest = PluginManifest.from_toml(path)
    except ManifestError as exc:
        print(f"invalid: {exc}", file=sys.stderr)
        return 2
    print(f"ok: {manifest.id} v{manifest.version} api={manifest.api}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="forge-plugin")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="list discovered plugins").set_defaults(fn=_cmd_list)

    val = sub.add_parser("validate", help="validate a manifest.toml")
    val.add_argument("manifest", help="path to manifest.toml")
    val.set_defaults(fn=_cmd_validate)

    args = parser.parse_args(argv)
    return int(args.fn(args))


if __name__ == "__main__":
    raise SystemExit(main())