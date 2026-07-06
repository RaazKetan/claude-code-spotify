#!/bin/bash
# Installer: copies scripts to ~/.claude, adds the `spot` alias, wires the
# statusLine into ~/.claude/settings.json, and (optionally) stores Spotify creds.
set -e
DEST="$HOME/.claude"
SRC="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$DEST"

echo "→ copying scripts to $DEST"
cp "$SRC/spot" "$SRC/spotify-lyrics.py" "$SRC/statusline.py" "$DEST/"
chmod +x "$DEST/spot" "$DEST/spotify-lyrics.py" "$DEST/statusline.py"

# shell alias (zsh + bash)
for rc in "$HOME/.zshrc" "$HOME/.bashrc"; do
  [ -f "$rc" ] || continue
  grep -q 'alias spot=' "$rc" || echo 'alias spot="$HOME/.claude/spot"' >> "$rc"
done
echo "→ added 'spot' alias (open a new terminal to use it)"

# Spotify creds (optional — only needed for `spot search` and auto-play)
if [ ! -f "$DEST/.spotify-creds" ]; then
  echo
  echo "Spotify search needs a free API app (id + secret): https://developer.spotify.com/dashboard"
  read -rp "Spotify Client ID (blank to skip search feature): " ID
  if [ -n "$ID" ]; then
    read -rp "Spotify Client Secret: " SECRET
    umask 077
    printf 'SPOTIFY_ID=%s\nSPOTIFY_SECRET=%s\n' "$ID" "$SECRET" > "$DEST/.spotify-creds"
    chmod 600 "$DEST/.spotify-creds"
    echo "→ saved creds to $DEST/.spotify-creds (chmod 600)"
  fi
fi

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

echo
echo "Done. RESTART Claude Code to load the statusline."
echo "Try: spot | spot next | spot search <song> | spot lyrics"
