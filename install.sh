#!/bin/bash
# Installer for claude-spotify-statusline.
#
# Works two ways:
#   • one-liner:  curl -fsSL <raw>/install.sh | bash   (fetches scripts from GitHub)
#   • from clone: ./install.sh                          (copies local scripts)
#
# Copies scripts to ~/.claude, adds the `spot` alias, wires the statusLine into
# ~/.claude/settings.json (preserving your other settings), and optionally
# stores Spotify API creds for search.
set -e

DEST="$HOME/.claude"
RAW_BASE="https://raw.githubusercontent.com/RaazKetan/claude-spotify-statusline/main"
SCRIPTS="spot spotify-lyrics.py statusline.py"
mkdir -p "$DEST"

# Are we running from a local checkout, or piped from curl?
SRC="$(cd "$(dirname "$0")" 2>/dev/null && pwd || true)"
if [ -n "$SRC" ] && [ -f "$SRC/statusline.py" ]; then
  echo "→ installing from local checkout ($SRC)"
  for f in $SCRIPTS; do cp "$SRC/$f" "$DEST/$f"; done
else
  echo "→ fetching scripts from GitHub"
  for f in $SCRIPTS; do
    curl -fsSL "$RAW_BASE/$f" -o "$DEST/$f" || { echo "failed to fetch $f"; exit 1; }
  done
fi
for f in $SCRIPTS; do chmod +x "$DEST/$f"; done
echo "→ installed scripts to $DEST"

# shell alias (zsh + bash)
for rc in "$HOME/.zshrc" "$HOME/.bashrc"; do
  [ -f "$rc" ] || continue
  grep -q 'alias spot=' "$rc" || echo 'alias spot="$HOME/.claude/spot"' >> "$rc"
done
echo "→ added 'spot' alias (open a new terminal to use it)"

# merge statusLine into settings.json (preserves existing settings)
python3 - "$DEST/settings.json" <<'PY'
import json, sys, os
p = sys.argv[1]
s = json.load(open(p)) if os.path.exists(p) else {}
s["statusLine"] = {"type": "command",
                   "command": 'python3 "$HOME/.claude/statusline.py"',
                   "refreshInterval": 1}
json.dump(s, open(p, "w"), indent=2)
print("→ wired statusLine into", p)
PY

# Spotify creds (optional — only `spot search` / auto-play need them). Auto-skipped
# in a non-interactive (piped) run; re-run locally to add them.
if [ ! -f "$DEST/.spotify-creds" ] && [ -t 0 ]; then
  echo
  echo "Spotify search needs a free API app (id + secret): https://developer.spotify.com/dashboard"
  read -rp "Spotify Client ID (blank to skip search): " ID
  if [ -n "$ID" ]; then
    read -rp "Spotify Client Secret: " SECRET
    umask 077
    printf 'SPOTIFY_ID=%s\nSPOTIFY_SECRET=%s\n' "$ID" "$SECRET" > "$DEST/.spotify-creds"
    chmod 600 "$DEST/.spotify-creds"
    echo "→ saved creds to $DEST/.spotify-creds (chmod 600)"
  fi
fi

echo
echo "Done. RESTART Claude Code to load the statusline."
echo "Try: spot | spot next | spot search <song> | spot lyrics"
