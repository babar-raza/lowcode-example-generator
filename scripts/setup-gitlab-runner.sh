#!/usr/bin/env bash
# setup-gitlab-runner.sh — bash equivalent of setup-gitlab-runner.ps1
# Usage: bash scripts/setup-gitlab-runner.sh [--force] [--skip-ci-var] [--dry-run]
set -euo pipefail

GITLAB_URL="https://gitlab.recruitize.ai"
PROJECT_PATH="sialkot/cantt-smallize/lowcode-example-generator"
RUNNER_DESC="local-docker-lowcode"
DEFAULT_IMAGE="python:3.13-slim"
FORCE=0; SKIP_CI_VAR=0; DRY_RUN=0

for arg in "$@"; do
  case $arg in
    --force)       FORCE=1 ;;
    --skip-ci-var) SKIP_CI_VAR=1 ;;
    --dry-run)     DRY_RUN=1 ;;
  esac
done

cyan()  { printf '\033[0;36m\n=== %s ===\033[0m\n' "$*"; }
ok()    { printf '\033[0;32m  OK  %s\033[0m\n' "$*"; }
warn()  { printf '\033[0;33m  WARN %s\033[0m\n' "$*"; }
fail()  { printf '\033[0;31m  FAIL %s\033[0m\n' "$*"; exit 1; }

gl_api() {
  local method="${1:-GET}" path="$2" body="${3:-}"
  local url="$GITLAB_URL/api/v4$path"
  if [ "$method" = "GET" ]; then
    curl -fsSL -H "PRIVATE-TOKEN: $PAT" "$url"
  else
    curl -fsSL -X "$method" -H "PRIVATE-TOKEN: $PAT" -H "Content-Type: application/json" -d "$body" "$url"
  fi
}

# ── Step 0: Read gl_pat ────────────────────────────────────────────────────────
cyan "Reading gl_pat"
PAT="${gl_pat:-}"
if [ -z "$PAT" ]; then
  fail "gl_pat environment variable not set. Export it before running this script."
fi
ok "gl_pat found (length=${#PAT})"
[ $DRY_RUN -eq 1 ] && warn "DRY RUN mode — API calls and registrations will be skipped."

# ── Step 1: Resolve project ID ─────────────────────────────────────────────────
cyan "Resolving project ID"
ENCODED_PATH=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$PROJECT_PATH', safe=''))")
PROJECT_ID=$(gl_api GET "/projects/$ENCODED_PATH" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
ok "Project ID: $PROJECT_ID"

# ── Step 2: Check existing runners ────────────────────────────────────────────
cyan "Checking for existing runners"
EXISTING_ID=$(gl_api GET "/projects/$PROJECT_ID/runners" | \
  python3 -c "import sys,json; rs=[r for r in json.load(sys.stdin) if r.get('description')=='$RUNNER_DESC']; print(rs[0]['id'] if rs else '')")

if [ -n "$EXISTING_ID" ] && [ $FORCE -eq 0 ]; then
  warn "Runner '$RUNNER_DESC' already registered (id=$EXISTING_ID). Use --force to re-register."
  SKIP_REGISTRATION=1
else
  [ -n "$EXISTING_ID" ] && warn "Force: will create new registration alongside existing id=$EXISTING_ID"
  ok "Proceeding with registration."
  SKIP_REGISTRATION=0
fi

# ── Step 3: Create runner token ────────────────────────────────────────────────
RUNNER_TOKEN=""
if [ $SKIP_REGISTRATION -eq 0 ]; then
  cyan "Creating runner token via GitLab API"
  if [ $DRY_RUN -eq 1 ]; then
    warn "DRY RUN: would POST /api/v4/user/runners"
  else
    RUNNER_TOKEN=$(gl_api POST "/user/runners" \
      "{\"runner_type\":\"project_type\",\"project_id\":$PROJECT_ID,\"description\":\"$RUNNER_DESC\",\"run_untagged\":true}" | \
      python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
    ok "Runner token: ${RUNNER_TOKEN:0:12}..."
  fi
fi

# ── Step 4: Detect runner ──────────────────────────────────────────────────────
cyan "Detecting gitlab-runner installation"
RUNNER_CONTAINER=""
RUNNER_BINARY=0

if command -v docker &>/dev/null; then
  RUNNER_CONTAINER=$(docker ps --format "{{.Names}}" 2>/dev/null | grep -m1 "gitlab-runner" || true)
fi
if [ -z "$RUNNER_CONTAINER" ] && command -v gitlab-runner &>/dev/null; then
  RUNNER_BINARY=1
fi

if [ -n "$RUNNER_CONTAINER" ]; then
  ok "Using Docker container: $RUNNER_CONTAINER"
elif [ $RUNNER_BINARY -eq 1 ]; then
  ok "Using gitlab-runner binary in PATH"
else
  fail "gitlab-runner not found. Start with: docker run -d --name gitlab-runner --restart always -v /var/run/docker.sock:/var/run/docker.sock -v gitlab-runner-config:/etc/gitlab-runner gitlab/gitlab-runner:latest"
fi

# ── Step 5: Register ───────────────────────────────────────────────────────────
if [ $SKIP_REGISTRATION -eq 0 ] && [ $DRY_RUN -eq 0 ] && [ -n "$RUNNER_TOKEN" ]; then
  cyan "Registering runner"
  REGISTER_ARGS=(register --non-interactive --url "$GITLAB_URL" --token "$RUNNER_TOKEN" --executor docker --docker-image "$DEFAULT_IMAGE" --description "$RUNNER_DESC")
  if [ -n "$RUNNER_CONTAINER" ]; then
    docker exec "$RUNNER_CONTAINER" gitlab-runner "${REGISTER_ARGS[@]}"
  else
    gitlab-runner "${REGISTER_ARGS[@]}"
  fi
  ok "Runner registered."
elif [ $DRY_RUN -eq 1 ]; then
  warn "DRY RUN: would run gitlab-runner register --url $GITLAB_URL --executor docker --docker-image $DEFAULT_IMAGE"
fi

# ── Step 6: Add gl_pat CI/CD variable ──────────────────────────────────────────
if [ $SKIP_CI_VAR -eq 0 ]; then
  cyan "Adding gl_pat as GitLab CI/CD variable"
  if [ $DRY_RUN -eq 1 ]; then
    warn "DRY RUN: would POST /api/v4/projects/$PROJECT_ID/variables key=gl_pat masked=true"
  else
    # Try update first; fall back to create
    UPDATE_RESULT=$(curl -s -o /dev/null -w "%{http_code}" -X PUT \
      -H "PRIVATE-TOKEN: $PAT" -H "Content-Type: application/json" \
      -d "{\"value\":\"$PAT\",\"masked\":true,\"protected\":true}" \
      "$GITLAB_URL/api/v4/projects/$PROJECT_ID/variables/gl_pat")
    if [ "$UPDATE_RESULT" = "200" ]; then
      ok "gl_pat variable updated."
    else
      gl_api POST "/projects/$PROJECT_ID/variables" \
        "{\"key\":\"gl_pat\",\"value\":\"$PAT\",\"variable_type\":\"env_var\",\"masked\":true,\"protected\":true}" >/dev/null
      ok "gl_pat variable created (masked + protected)."
    fi
  fi
fi

# ── Step 7: Verify ─────────────────────────────────────────────────────────────
cyan "Verifying runner"
if [ $DRY_RUN -eq 0 ]; then
  if [ -n "$RUNNER_CONTAINER" ]; then
    docker exec "$RUNNER_CONTAINER" gitlab-runner verify 2>&1 | grep -E "(Verifying|alive|error)" || true
  else
    gitlab-runner verify 2>&1 | grep -E "(Verifying|alive|error)" || true
  fi
fi

# ── Done ────────────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Setup complete."
echo ""
echo " Runner settings : $GITLAB_URL/$PROJECT_PATH/-/settings/ci_cd"
echo " Pipelines       : $GITLAB_URL/$PROJECT_PATH/-/pipelines"
echo " Trigger pipeline: git push origin main"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
