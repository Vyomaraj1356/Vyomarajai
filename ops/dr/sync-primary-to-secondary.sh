#!/usr/bin/env bash
set -Eeuo pipefail
PRIMARY_REPO="${PRIMARY_REPO:-Vyomaraj1356/Vyomarajai}"
DR_REPO="${DR_REPO:-deepakGoyal1356/Vyomaraj-Agent-6d64e}"
SOURCE_REF="${SOURCE_REF:-feat/vyomaraj-surya-presence-runtime}"
TARGET_REF="${TARGET_REF:-main}"

echo "VYOMARAJ PRIMARY → DR SYNC"
echo "source: $PRIMARY_REPO@$SOURCE_REF"
echo "target: $DR_REPO@$TARGET_REF"

if [[ -z "${VYOMARAJ_PAT:-}" ]]; then
  echo "BLOCKED: VYOMARAJ_PAT is not configured."
  echo "No credential is embedded in this script."
  exit 20
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

git init -q
git remote add primary "https://x-access-token:${VYOMARAJ_PAT}@github.com/$PRIMARY_REPO.git"
git remote add dr "https://x-access-token:${VYOMARAJ_PAT}@github.com/$DR_REPO.git"
git fetch --no-tags primary "$SOURCE_REF"
git fetch --no-tags dr "$TARGET_REF"

src="$(git rev-parse "refs/remotes/primary/$SOURCE_REF")"
dst="$(git rev-parse "refs/remotes/dr/$TARGET_REF")"
echo "source_sha=$src"
echo "target_sha_before=$dst"

if [[ "$src" == "$dst" ]]; then
  echo "ALREADY_SYNCED"
  exit 0
fi

git push dr "$src:refs/heads/$TARGET_REF"

git fetch --no-tags dr "$TARGET_REF"
after="$(git rev-parse "refs/remotes/dr/$TARGET_REF")"
echo "target_sha_after=$after"

if [[ "$after" != "$src" ]]; then
  echo "FAIL: DR read-after-write mismatch"
  exit 30
fi

echo "PASS: PRIMARY_TO_DR_READ_AFTER_WRITE"
