#!/usr/bin/env bash
# Upgrade git dependency tags, the uv lock, .venv, and requirements.txt.
#
# requirements.txt is what Docker installs with pip. The image does not need uv.
#
# Usage (from repo root):
#   ./update_dependencies.sh
#   ./update_dependencies.sh --dry-run

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [[ $# -gt 1 ]] || [[ $# -eq 1 && "$1" != "--dry-run" ]]; then
  echo "Usage: ./update_dependencies.sh [--dry-run]" >&2
  exit 2
fi

dry_run=0
if [[ "${1:-}" == "--dry-run" ]]; then
  dry_run=1
fi

python3 "$ROOT/scripts/update_git_dependencies.py" "$@"

if command -v uv >/dev/null 2>&1; then
  UV="$(command -v uv)"
elif [[ -x "${HOME}/.local/bin/uv" ]]; then
  UV="${HOME}/.local/bin/uv"
else
  echo "uv was not found on PATH or at ~/.local/bin/uv" >&2
  exit 1
fi

run() {
  printf '+'
  printf ' %q' "$@"
  printf '\n'
  if [[ "$dry_run" -eq 0 ]]; then
    "$@"
  fi
}

run "$UV" lock --upgrade
run "$UV" sync
run "$UV" export \
  --frozen \
  --no-dev \
  --no-hashes \
  --no-annotate \
  --no-header \
  --no-emit-project \
  --output-file requirements.txt
