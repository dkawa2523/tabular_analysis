#!/usr/bin/env bash
set -euo pipefail

echo "Selfcheck: codex exec from stdin"

PROMPT="Create a file named .codex_exec_selfcheck.txt containing 'ok'."

if codex exec --help 2>&1 | grep -q -- "--skip-git-repo-check"; then
  echo "$PROMPT" | codex exec --sandbox workspace-write --skip-git-repo-check -
else
  echo "$PROMPT" | codex exec --sandbox workspace-write -
fi

if [[ ! -f ".codex_exec_selfcheck.txt" ]]; then
  echo "FAILED: file not created."
  exit 1
fi
echo "PASS: .codex_exec_selfcheck.txt created"
