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

echo "Fleet home template checks passed."
