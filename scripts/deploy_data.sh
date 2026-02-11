#!/bin/zsh
set -e

cd "$(dirname "$0")/.."

MSG=${1:-"chore: data refresh"}

python3 build_notices.py

git add notices.json notices.js

if git diff --cached --quiet; then
  echo "No data changes to commit."
  exit 0
fi

git commit -m "$MSG"
git push

echo "Data deploy pushed."