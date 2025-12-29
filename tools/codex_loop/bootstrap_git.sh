#!/usr/bin/env bash
set -euo pipefail

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Already inside a git repository."
  exit 0
fi

git init
git add -A

if git commit -m "baseline (bootstrap)" >/dev/null 2>&1; then
  echo "Baseline commit created."
else
  echo "Commit failed. Configure git user then retry:"
  echo '  git config user.email "you@example.com"'
  echo '  git config user.name "Your Name"'
  exit 1
fi
