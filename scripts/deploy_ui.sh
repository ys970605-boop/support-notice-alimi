#!/bin/zsh
set -e

cd "$(dirname "$0")/.."

MSG=${1:-"feat: ui update"}

git add -A
# UI 배포 커밋에서는 데이터 산출물 제외
if git ls-files --error-unmatch notices.json >/dev/null 2>&1; then
  git reset notices.json notices.js >/dev/null 2>&1 || true
fi

if git diff --cached --quiet; then
  echo "No UI changes to commit."
  exit 0
fi

git commit -m "$MSG"
git push

echo "UI deploy pushed."