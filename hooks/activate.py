#!/usr/bin/env python3
"""SessionStart hook: point Claude Code's statusLine at this plugin's
statusline.py. Idempotent — writes only when the setting differs, preserves
all other settings, and never corrupts settings.json (atomic replace; bails
out untouched if the file is unreadable/invalid).

Runs each session so it self-heals when the plugin path changes on update.
Uninstall the plugin (and remove the statusLine key) to turn it off.
"""

import json
import os
import sys

root = os.environ.get("CLAUDE_PLUGIN_ROOT")
if not root:
    sys.exit(0)  # not running under the plugin runtime; nothing to do

settings_path = os.path.expanduser("~/.claude/settings.json")
desired = {
    "type": "command",
    "command": f'python3 "{os.path.join(root, "statusline.py")}"',
    "refreshInterval": 1,
}

# Load existing settings safely. Missing file is fine (start empty). Invalid
# JSON is NOT — bail rather than risk clobbering the user's whole config.
settings = {}
if os.path.exists(settings_path):
    try:
        with open(settings_path) as f:
            settings = json.load(f)
        if not isinstance(settings, dict):
            sys.exit(0)
    except Exception:
        print("[spotify-statusline] ~/.claude/settings.json is unreadable; "
              "add the statusLine manually. Left it untouched.")
        sys.exit(0)

if settings.get("statusLine") == desired:
    sys.exit(0)  # already ours — silent no-op

settings["statusLine"] = desired
os.makedirs(os.path.dirname(settings_path), exist_ok=True)
tmp = settings_path + ".tmp"
try:
    with open(tmp, "w") as f:
        json.dump(settings, f, indent=2)
    os.replace(tmp, settings_path)  # atomic
except Exception as e:
    print(f"[spotify-statusline] couldn't update settings.json: {e}")
    sys.exit(0)

print("[spotify-statusline] statusline activated — it appears on your next line. "
      "Play something on Spotify to see the lyric.")
