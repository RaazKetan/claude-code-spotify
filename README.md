# 🎵 claude-spotify-statusline

A [Claude Code](https://claude.com/claude-code) statusline that shows your
session at a glance **and** the live, synced lyric of whatever's playing on
Spotify — Spotify-green themed, updating with the music. Ships with `spot`, a
tiny terminal remote for Spotify.

![statusline screenshot](assets/statusline.png)

```
◈ 90d19fcb · ✦ Opus 4.8 (1M context) · 📁 Conekt · ⎇ docs/scoring-rubric · ⇅ #10 · ▰▰▰▱▱ 547k   │  🎵 The Winner Takes It All  Always staying low
```

Left to right: **session · model · folder · git branch · PR · context-usage bar · now-playing lyric**. Fields with no data (no branch, no PR, nothing playing) simply drop out.

> **macOS only.** Playback control uses AppleScript against the Spotify **desktop app** (installed + running). Lyrics come from [lrclib.net](https://lrclib.net) — free, no key. Python 3 stdlib only, no pip installs.

---

## Install

**One-liner** (fetches the scripts, wires everything, preserves your existing `settings.json`):

```bash
curl -fsSL https://raw.githubusercontent.com/RaazKetan/claude-spotify-statusline/main/install.sh | bash
```

Then **restart Claude Code**. That's it.

<details>
<summary>From a clone (if you'd rather read it first)</summary>

```bash
git clone https://github.com/RaazKetan/claude-spotify-statusline.git
cd claude-spotify-statusline
./install.sh
```
</details>

<details>
<summary>Manual</summary>

1. Copy `spot`, `spotify-lyrics.py`, `statusline.py` to `~/.claude/` and `chmod +x` them.
2. Add to `~/.claude/settings.json`:
   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "python3 \"$HOME/.claude/statusline.py\"",
       "refreshInterval": 1
     }
   }
   ```
3. Optional alias: `echo 'alias spot="$HOME/.claude/spot"' >> ~/.zshrc`
4. Restart Claude Code.
</details>

The installer is idempotent — re-run it any time to update.

## `spot` — terminal remote

```bash
spot                 # now playing
spot play / pause / stop
spot next / prev
spot vol 50          # volume 0–100
spot search <song>   # search + play the top match
spot lyrics          # full-screen fading synced lyrics (Ctrl-C to exit)
```

### Search (optional, needs a free Spotify app)

Only `spot search` / auto-play use the Spotify Web API — playback and lyrics don't.

1. <https://developer.spotify.com/dashboard> → **Create app** (any name/redirect).
2. Re-run the installer, or drop the creds in `~/.claude/.spotify-creds` (chmod 600):
   ```
   SPOTIFY_ID=your_client_id
   SPOTIFY_SECRET=your_client_secret
   ```

Uses the app-only **Client Credentials** flow (no browser login), finds the top match, plays it through the desktop app.

## How it works

- **Playback** — one batched `osascript` (AppleScript) call to the Spotify app.
- **Lyrics** — pulled from lrclib, cached per track in `/tmp/spot-lrc/`. The statusline **never blocks on the network**: on a cache miss it shows the track name and fetches in a detached background process that fills the cache for the next tick. Each render stays well under the 1-second refresh window (~0.2s), so Claude Code never cancels it mid-draw.
- **Statusline fields** — session/model/context/PR come straight from the JSON Claude Code pipes to the command; the git branch is a local `git` call.
- **Context bar** — `▰▰▰▱▱` fills with context-window usage and shifts green → orange → red as you approach the limit.

## Notes / limits

- The vertical "karaoke" fade is in `spot lyrics` (full screen). The statusline is one line, so it shows just the current lyric.
- lrclib rate-limits rapid requests — one fetch per track (normal use) is fine.
- Not every track has synced lyrics; those fall back to `🎵 Artist – Song`.

## License

MIT
