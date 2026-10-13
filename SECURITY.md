# Security Policy

## Scope

`ai-pixel-avatar-forge` is a desktop tool that loads third-party plugins.
Plugins execute arbitrary Python in-process. That is by design and it is the
main attack surface. Treat any plugin you install the same way you'd treat a
random `.exe`.

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.6.x   | yes       |
| 0.5.x   | security fixes only |
| < 0.5   | no        |

## Reporting a vulnerability

Email `security@ai-pixel-avatar-forge.dev` with:

- affected version (`forge --version`)
- plugin id + version if the issue is plugin-side
- a minimal repro (prompt, style pack, seed) if it's a crash or a path escape
- whether you consider it remote-triggerable

We aim to acknowledge within 72 hours. Do not open a public issue for
in-process code execution, path traversal in the asset cache, or model-file
deserialization bugs.

## Known hardening

- Model files are loaded with `weights_only=True` where the backend supports
  it. Legacy `.pt` packs trigger a confirmation dialog before load.
- The asset cache root is resolved and re-checked against the configured
  cache dir before any write; symlinks that escape the root are rejected.
- Plugin manifests are validated against `avatar_forge.contracts.manifest`
  before import. A malformed manifest fails the plugin, not the host.

## Out of scope

- Prompt injection against a local model producing a weird avatar. That's the
  model doing its job.
- DoS via a giant style pack the user chose to install.