# 🎵 claude-spotify-statusline

Control Spotify from your terminal **and** show the live, synced lyric in your
[Claude Code](https://claude.com/claude-code) statusline — Spotify-green themed,
updating with the music.

```
◈ a1b2c3d4 · Opus 4.8 · 📁 CODE · ⎇ main · PR#42 · ⛁ 16k 8%   🎵 Beautiful Things  But I'm up at night thinkin'
```

The statusline shows: **session id · model · folder · git branch · PR · context tokens · now-playing lyric**.

> **macOS only** — playback control uses AppleScript against the Spotify **desktop app** (must be installed & running). Lyrics come from [lrclib.net](https://lrclib.net) (free, no key).

---

## What you get

- **`spot`** — a tiny CLI: `play` `pause` `stop` `next` `prev` `vol N` `search <song>` `lyrics` `current`
- **`spotify-lyrics.py`** — full-screen karaoke-style fading lyrics + the one-line statusline mode
- **`statusline.py`** — the composed Claude Code statusline

## Install

```bash
git clone https://github.com/RaazKetan/claude-spotify-statusline.git
cd claude-spotify-statusline
./install.sh
```

The installer copies the scripts to `~/.claude/`, adds a `spot` shell alias, wires
the `statusLine` into `~/.claude/settings.json`, and (optionally) stores your
Spotify API creds. **Restart Claude Code afterward.**

### Manual install

1. Copy the three scripts to `~/.claude/` and `chmod +x` them.
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
3. (Optional) alias: `echo 'alias spot="$HOME/.claude/spot"' >> ~/.zshrc`
4. Restart Claude Code.

## Spotify search (optional)

`spot search <song>` and typing a song to auto-play need a free Spotify API app —
**only search uses it; playback control and lyrics do not.**

1. Go to <https://developer.spotify.com/dashboard> → **Create app** (any name/redirect).
2. Copy the **Client ID** and **Client Secret**.
3. Either re-run `./install.sh`, or create `~/.claude/.spotify-creds` (chmod 600):
   ```
   SPOTIFY_ID=your_client_id
   SPOTIFY_SECRET=your_client_secret
   ```

Search uses the **Client Credentials** flow (app-only, no browser login). It finds
the top match and plays it through the desktop app.

## Usage

```bash
spot                 # now playing
spot play / pause / stop
spot next / prev
spot vol 50          # volume 0–100
spot search <song>   # search + play top result
spot lyrics          # full-screen fading synced lyrics (Ctrl-C to exit)
```

The statusline updates every second (`refreshInterval: 1`) and follows track
changes automatically.

## How it works

- **Playback** — one batched `osascript` (AppleScript) call to the Spotify app.
- **Lyrics** — fetched from lrclib, cached per-track in `/tmp/spot-lrc/`. The
  statusline **never** blocks on the network: on a cache miss it shows the song
  name and fetches in a detached background process that fills the cache for the
  next tick. This keeps each render well under the 1-second refresh window (~0.2s),
  so Claude Code never cancels it mid-run.
- **Statusline fields** — session/model/tokens/PR come straight from the JSON
  Claude Code pipes to the command; branch is a local `git` call.

## Notes / limits

- Vertical "karaoke" fade lives in `spot lyrics` (full screen). The statusline is
  a single line, so it shows just the current lyric.
- lrclib rate-limits rapid requests — normal use (one fetch per track) is fine.
- Not every song has synced lyrics; those fall back to `🎵 Song — Artist`.

## License

MIT
