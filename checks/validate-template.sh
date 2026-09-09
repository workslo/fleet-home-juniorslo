#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

required_files=(
  "README.md"
  "home/entry.yaml"
  "scratch/notes.md"
  "ui/home.html"
  "validations/template-checklist.md"
)

for file in "${required_files[@]}"; do
  if [[ ! -f "${ROOT_DIR}/${file}" ]]; then
    echo "Missing required file: ${file}" >&2
    exit 1
  fi
done

if ! grep -q "repository: \"read_write\"" "${ROOT_DIR}/home/entry.yaml"; then
  echo "home/entry.yaml must declare read/write repository permissions." >&2
  exit 1
fi

if ! grep -q "entrypoint: \"ui/home.html\"" "${ROOT_DIR}/home/entry.yaml"; then
  echo "home/entry.yaml must define a UI entrypoint." >&2
  exit 1
fi

# Compiled Python must not be tracked. The tests load checks/memory-lint through
# importlib, which writes a __pycache__ beside it; one such file shipped in PR #24.
# Presence on disk is fine (it is a side effect of running the tests) -- being
# tracked by git is the defect.
if tracked_pyc="$(git -C "${ROOT_DIR}" ls-files -- '*.pyc' '**/__pycache__/*' 2>/dev/null)" \
   && [[ -n "${tracked_pyc}" ]]; then
  echo "Compiled Python is tracked in git (add it to .gitignore and git rm --cached):" >&2
  echo "${tracked_pyc}" >&2
  exit 1
fi

echo "Fleet home template checks passed."
