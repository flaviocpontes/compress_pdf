# AGENTS.md

## Commands

- Run tests: `uv run tests.py`
- Run the tool: `uv run main.py <input.pdf> <output.pdf> <size_in_mib>`
- Build the standalone binary: `uv run pyinstaller --onefile --name compress-pdf main.py` (output in `dist/`)

## Commits — Conventional Commits

Format: `type(scope): subject` (scope optional). Types: `feat`, `fix`, `docs`,
`refactor`, `test`, `chore`, `build`, `ci`. Subject in imperative mood,
lowercase, no trailing period. Example: `fix: stop at first setting that fits target`.

## Versioning — Semantic Versioning

- MAJOR: incompatible CLI or behavior changes
- MINOR: backwards-compatible new functionality
- PATCH: bug fixes

The canonical version lives in `pyproject.toml`. Current release: **1.0.0**.

## Releasing (manual)

1. Bump `version` in `pyproject.toml`.
2. Commit as `chore(release): vX.Y.Z`.
3. Tag the release commit `vX.Y.Z` and push the tag.
4. CI (`.github/workflows/release.yml`) builds binaries for Linux, Windows and
   macOS and attaches them to the GitHub release for that tag.
