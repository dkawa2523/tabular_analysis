#!/usr/bin/env bash
set -euo pipefail

# Selfcheck for codex-cli.
# - codex exec expects prompt as positional argument (NOT stdin).
# - Valid sandbox values: read-only | workspace-write | danger-full-access
# - Some environments require --skip-git-repo-check (if supported).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "Selfcheck: codex exec (prompt as positional argument)"
cd "${REPO_ROOT}"

if ! command -v codex >/dev/null 2>&1; then
  echo "FAILED: codex command not found in PATH"
  echo "Hint: install codex-cli and ensure `codex --help` works."
  exit 1
fi

HELP_OUT="$(codex exec --help 2>&1 || true)"

SKIP_FLAG=""
if echo "${HELP_OUT}" | grep -q -- "--skip-git-repo-check"; then
  SKIP_FLAG="--skip-git-repo-check"
fi

# Candidate sandbox modes (preferred order)
CANDIDATES=("workspace-write" "danger-full-access" "read-only")

# If user explicitly sets CODEX_SANDBOX_MODE (and not 'auto'), try only that value.
if [[ "${CODEX_SANDBOX_MODE:-auto}" != "auto" ]]; then
  CANDIDATES=("${CODEX_SANDBOX_MODE}")
fi

# Create selfcheck file inside tools/ to avoid cluttering repo root
CHECK_FILE_REL="tools/codex_loop/.codex_exec_selfcheck.txt"
CHECK_FILE="${REPO_ROOT}/${CHECK_FILE_REL}"
LOG_FILE="${REPO_ROOT}/tools/codex_loop/.codex_exec_selfcheck.log"
RUNTIME_FILE="${REPO_ROOT}/tools/codex_loop/runtime.json"

rm -f "${CHECK_FILE}" "${LOG_FILE}"

PROMPT="Create the file ${CHECK_FILE_REL} with the single line: OK"

LAST_OUT=""

for MODE in "${CANDIDATES[@]}"; do
  echo "Trying: --sandbox ${MODE} ${SKIP_FLAG}"
  rm -f "${CHECK_FILE}" "${LOG_FILE}"

  set +e
  if [[ -n "${SKIP_FLAG}" ]]; then
    codex exec --sandbox "${MODE}" "${SKIP_FLAG}" "${PROMPT}" > "${LOG_FILE}" 2>&1
  else
    codex exec --sandbox "${MODE}" "${PROMPT}" > "${LOG_FILE}" 2>&1
  fi
  RC=$?
  set -e

  if [[ -f "${CHECK_FILE}" ]]; then
    echo "OK: created ${CHECK_FILE_REL} (sandbox=${MODE})"
    rm -f "${CHECK_FILE}"  # cleanup to avoid git untracked noise

    REPO_ROOT="${REPO_ROOT}" MODE="${MODE}" SKIP_FLAG="${SKIP_FLAG}" python - <<'PY'
import json, os, pathlib
repo_root = pathlib.Path(os.environ["REPO_ROOT"])
mode = os.environ["MODE"]
skip_flag = os.environ.get("SKIP_FLAG","")
runtime_file = repo_root / "tools" / "codex_loop" / "runtime.json"
runtime_file.parent.mkdir(parents=True, exist_ok=True)
data = {
  "sandbox_mode": mode,
  "use_skip_git_repo_check": bool(skip_flag),
  "skip_git_repo_check_flag": "--skip-git-repo-check" if bool(skip_flag) else None,
}
runtime_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
print(f"Wrote runtime settings: {runtime_file}")
PY
    exit 0
  fi

  echo "  Not created (rc=${RC})."
  if [[ -f "${LOG_FILE}" ]]; then
    LAST_OUT="$(tail -n 80 "${LOG_FILE}")"
  else
    LAST_OUT="(no log output captured)"
  fi
done

echo "FAILED: codex exec did not create ${CHECK_FILE_REL}"
echo "---- last codex output ----"
echo "${LAST_OUT}"
echo
echo "Tips:"
echo "  - Valid sandbox values: read-only | workspace-write | danger-full-access"
echo "  - You can force sandbox mode, e.g.:"
echo "      export CODEX_SANDBOX_MODE=workspace-write"
echo "  - See your codex exec help:"
echo "      codex exec --help"
exit 1
