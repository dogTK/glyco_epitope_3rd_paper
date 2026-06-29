#!/bin/bash
# Stop hook: auto commit and push changes at session end

REPO_DIR="/Users/koreedatatsuya/research/glyco_epitope_3rd_paper"
SUMMARY_PATH="$REPO_DIR/.claude/session_summary.txt"

cd "$REPO_DIR" || exit 0

# サマリーがなければスキップ（無意味なコミットを避ける）
if [ ! -f "$SUMMARY_PATH" ]; then
    exit 0
fi

commit_msg=$(head -1 "$SUMMARY_PATH")

# 変更がなければスキップ
if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    exit 0
fi

git add -u
git add manuscript/ notes/ scripts/ inputs/ .claude/hooks/ .claude/CLAUDE.md 2>/dev/null || true

if ! git diff --cached --quiet; then
    git commit -m "$commit_msg" \
        --author="Claude Code <noreply@anthropic.com>" 2>/dev/null
fi

git push origin main 2>/dev/null || true
