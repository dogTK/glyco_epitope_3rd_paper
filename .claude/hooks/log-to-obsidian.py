#!/usr/bin/env python3
"""Stop hook: logs Claude Code session summary to today's Obsidian note."""
import json
import sys
import os
from datetime import date, timedelta, datetime

try:
    hook_input = json.load(sys.stdin)
except Exception:
    hook_input = {}

VAULT_DIR = "/Users/koreedatatsuya/research/glyco_epitope_3rd_paper"
NOTES_DIR = os.path.join(VAULT_DIR, "notes")
TEMPLATE_PATH = os.path.join(NOTES_DIR, "templates", "daily.md")
SUMMARY_PATH = os.path.join(VAULT_DIR, ".claude", "session_summary.txt")

today = date.today()
today_str = today.strftime("%Y-%m-%d")
yesterday_str = (today - timedelta(days=1)).strftime("%Y-%m-%d")
tomorrow_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")
note_path = os.path.join(NOTES_DIR, f"{today_str}.md")

# Create today's note if missing
if not os.path.exists(note_path):
    try:
        with open(TEMPLATE_PATH) as f:
            template = f.read()
        content = (
            template
            .replace("{{date}}", today_str)
            .replace("{{yesterday}}", yesterday_str)
            .replace("{{tomorrow}}", tomorrow_str)
        )
        with open(note_path, "w") as f:
            f.write(content)
    except Exception:
        pass

# Read summary written by Claude at end of session
summary = ""
if os.path.exists(SUMMARY_PATH):
    try:
        with open(SUMMARY_PATH) as f:
            summary = f.read().strip().split("\n")[0][:200]
        os.remove(SUMMARY_PATH)
    except Exception:
        pass

if not summary:
    summary = "(作業完了)"

# Append log line under ## 作業ログ section
time_str = datetime.now().strftime("%H:%M")
log_line = f"- {time_str}: {summary}"

try:
    with open(note_path, "r") as f:
        content = f.read()

    if "## 作業ログ" not in content:
        content = content.rstrip() + "\n\n## 作業ログ\n"

    content = content.rstrip() + "\n" + log_line + "\n"

    with open(note_path, "w") as f:
        f.write(content)
except Exception:
    pass
