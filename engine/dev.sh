#!/usr/bin/env bash
# Enhanced installer with reporting, retries and basic operations
set -u

ACTION=${1:-install}   # install | reinstall | status
DRY_RUN=0
if [ "${2:-}" = "--dry-run" ]; then
  DRY_RUN=1
fi

ROOT_DIR="$(pwd)"
LOG_DIR="$ROOT_DIR/.install_logs"
mkdir -p "$LOG_DIR"

# aggregated logs
LOG_ALL="$LOG_DIR/all.log"
LOG_SUCCESS="$LOG_DIR/success.log"
LOG_FAIL="$LOG_DIR/fail.log"
LOG_SKIPPED="$LOG_DIR/skipped.log"

# rotate/clear previous logs for a fresh run
: > "$LOG_ALL"
: > "$LOG_SUCCESS"
: > "$LOG_FAIL"
: > "$LOG_SKIPPED"

get_site_packages() {
  python3 - <<'PY'
import site, sys
sp = None
try:
    sp = site.getsitepackages()[0]
except Exception:
    # fallback to first entry in sys.path that contains 'site-packages'
    for p in sys.path:
        if 'site-packages' in str(p):
            sp = p
            break
print(sp or '')
PY
}

SITE_PACKAGES=$(get_site_packages)

packages=()
while IFS= read -r setupfile; do
  packages+=("$(dirname "$setupfile")")
done < <(find . -type f -name setup.py)

total=${#packages[@]}
echo "Found $total packages to process"

success=0
failures=()

for pkgdir in "${packages[@]}"; do
  pkgdir=$(realpath "$pkgdir")
  name=$(basename "$pkgdir")
  echo "\n=== [$ACTION] $name -> $pkgdir ===" | tee -a "$LOG_ALL"

  if [ $DRY_RUN -eq 1 ]; then
    echo "DRY RUN: would perform $ACTION on $pkgdir" | tee -a "$LOG_ALL" "$LOG_SKIPPED"
    continue
  fi

  constraints_arg=""
  if [ -f "$pkgdir/constraints.txt" ]; then
    constraints_arg="--constraint $pkgdir/constraints.txt"
  fi

  start=$(date +%s)
  attempt=0
  ok=1
  max_attempts=2
  while [ $attempt -lt $max_attempts ]; do
  attempt=$((attempt+1))
  echo "Attempt #$attempt for $name" | tee -a "$LOG_ALL"
    if [ "$ACTION" = "install" ] || [ "$ACTION" = "reinstall" ]; then
      cmd=(pip install -e "$pkgdir")
      if [ -n "$constraints_arg" ]; then
        cmd+=(--constraint "$pkgdir/constraints.txt")
      fi
      if [ "$ACTION" = "reinstall" ]; then
        # force reinstall
        cmd+=(--force-reinstall)
      fi
  # write command output into aggregated all.log so failures can be inspected
  "${cmd[@]}" >>"$LOG_ALL" 2>&1 && ok=0 || ok=1
    elif [ "$ACTION" = "status" ]; then
      ok=0
      # check for .egg-link in site-packages pointing to this pkgdir
      if [ -n "$SITE_PACKAGES" ] && [ -d "$SITE_PACKAGES" ]; then
        found=0
        for f in "$SITE_PACKAGES"/*.egg-link; do
          [ -e "$f" ] || continue
          if grep -Fxq "$pkgdir" "$f" 2>/dev/null; then
            echo "Installed (editable) -> $f" | tee -a "$LOG_ALL"
            found=1
            break
          fi
        done
        if [ $found -eq 0 ]; then
          echo "Not installed (no egg-link found)" | tee -a "$log"
          ok=1
        fi
      else
        echo "Could not determine site-packages path" | tee -a "$log"
        ok=1
      fi
    else
      echo "Unknown ACTION: $ACTION" | tee -a "$LOG_ALL"
      ok=1
    fi

    if [ $ok -eq 0 ]; then
      break
    else
      echo "Attempt $attempt failed for $name" | tee -a "$LOG_ALL"
      sleep 1
    fi
  done

  duration=$(( $(date +%s) - start ))
  if [ $ok -eq 0 ]; then
    echo "SUCCESS: $name in ${duration}s" | tee -a "$LOG_ALL"
    echo "$name,$pkgdir,${duration}s" >> "$LOG_SUCCESS"
    success=$((success+1))
  else
    echo "FAIL: $name after $attempt attempts" | tee -a "$LOG_ALL"
    echo "$name,$pkgdir,${attempt} attempts" >> "$LOG_FAIL"
    failures+=("$name")
  fi

  # small delay to avoid hammering pip
  sleep 0.1
done

echo "\n=== Summary ==="
echo "Action: $ACTION"
echo "Total: $total"
echo "Success: $success"
echo "Failed: ${#failures[@]}"
if [ ${#failures[@]} -gt 0 ]; then
  echo "Failed packages:"
  for f in "${failures[@]}"; do
    echo " - $f (log: $LOG_DIR/$f.log)"
  done
fi

echo "Logs written to $LOG_DIR"

if [ ${#failures[@]} -gt 0 ]; then
  exit 2
fi
