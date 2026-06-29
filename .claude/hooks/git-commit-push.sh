#!/bin/bash
# Stop hook: auto commit and push changes at session end

REPO_DIR="/Users/koreedatatsuya/research/glyco_epitope_3rd_paper"
cd "$REPO_DIR" || exit 0

# ステージングされていない変更・未追跡ファイルがあればコミット
if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    # 追跡済みの変更をステージ（新規ファイルは除く）
    git add -u

    # 未追跡ファイルのうち .gitignore 対象外のものを追加
    git add manuscript/ notes/ scripts/ inputs/ 2>/dev/null || true

    # ステージに何かあればコミット
    if ! git diff --cached --quiet; then
        git commit -m "Auto-commit: session end $(date '+%Y-%m-%d %H:%M')" \
            --author="Claude Code <noreply@anthropic.com>" 2>/dev/null
    fi
fi

# リモートにプッシュ
git push origin main 2>/dev/null || true
