#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

LOG_FILE="${TOOLS_DIR}/codex_exec_selfcheck.log"
RUNTIME_JSON="${TOOLS_DIR}/runtime.json"

echo "Selfcheck: codex exec (prompt as positional argument)" | tee "${LOG_FILE}"

cd "${ROOT_DIR}"

# Determine whether codex supports --skip-git-repo-check
SUPPORTS_SKIP=0
if codex exec --help 2>/dev/null | grep -q -- "--skip-git-repo-check"; then
  SUPPORTS_SKIP=1
fi

# Sandbox mode order: prefer workspace-write (needed for edits)
MODES=("workspace-write" "danger-full-access" "read-only")
if [[ -n "${CODEX_SANDBOX_MODE:-}" ]]; then
  MODES=("${CODEX_SANDBOX_MODE}")
fi

# Create a temporary marker file inside tools dir (avoid polluting repo root)
MARKER_REL="tools/codex_loop/codex_exec_selfcheck.txt"
rm -f "${MARKER_REL}"

PROMPT="Create file ${MARKER_REL} with text 'ok' and exit. Do not modify anything else."

for MODE in "${MODES[@]}"; do
  echo "Trying sandbox=${MODE}" | tee -a "${LOG_FILE}"
  set +e
  if [[ ${SUPPORTS_SKIP} -eq 1 ]]; then
    codex exec --sandbox "${MODE}" --skip-git-repo-check "${PROMPT}" >> "${LOG_FILE}" 2>&1
  else
    codex exec --sandbox "${MODE}" "${PROMPT}" >> "${LOG_FILE}" 2>&1
  fi
  RC=$?
  set -e

  if [[ ${RC} -ne 0 ]]; then
    echo "codex exec failed rc=${RC} for sandbox=${MODE}" | tee -a "${LOG_FILE}"
    continue
  fi

  if [[ -f "${MARKER_REL}" ]]; then
    echo "OK: created ${MARKER_REL}" | tee -a "${LOG_FILE}"
    rm -f "${MARKER_REL}"

    # Write runtime.json for run.py
    cat > "${RUNTIME_JSON}" <<EOF
{
  "sandbox_mode": "${MODE}",
  "supports_skip_git_repo_check": $( [[ ${SUPPORTS_SKIP} -eq 1 ]] && echo "true" || echo "false" )
}
EOF
    echo "Wrote ${RUNTIME_JSON}" | tee -a "${LOG_FILE}"
    exit 0
  fi
done

echo "FAILED: codex exec did not create marker file (${MARKER_REL})" | tee -a "${LOG_FILE}"
exit 2
