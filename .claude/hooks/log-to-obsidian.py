#!/usr/bin/env python3
"""Stop hook: logs Claude Code actions to today's Obsidian note."""
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

# Extract last user message from transcript as summary
summary = ""
transcript_path = hook_input.get("transcript_path", "")
if transcript_path and os.path.exists(transcript_path):
    try:
        messages = []
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        messages.append(json.loads(line))
                    except Exception:
                        pass
        for msg in reversed(messages):
            # Handle both flat {"role":...} and nested {"message":{"role":...}}
            role = msg.get("role") or (msg.get("message") or {}).get("role", "")
            if role != "user":
                continue
            content = msg.get("content") or (msg.get("message") or {}).get("content", "")
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        content = block.get("text", "")
                        break
            text = str(content).strip().split("\n")[0][:120]
            if text and not text.startswith("<"):  # skip XML-like tool results
                summary = text
                break
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
