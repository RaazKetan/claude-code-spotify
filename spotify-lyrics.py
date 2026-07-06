#!/usr/bin/env python3
# spot lyrics — live synced lyrics from lrclib, fading as the song plays.
# ponytail: lrclib (no key) + Spotify AppleScript position. Stdlib only.
import re, sys, time, json, subprocess, urllib.parse, urllib.request

LRC = re.compile(r'\[(\d+):(\d+(?:\.\d+)?)\]')

def parse_lrc(text):
    """LRC -> sorted [(seconds, line)]. Lines may carry multiple stamps."""
    out = []
    for raw in text.splitlines():
        stamps = LRC.findall(raw)
        words = LRC.sub('', raw).strip()
        for m, s in stamps:
            out.append((int(m) * 60 + float(s), words))
    return sorted(out, key=lambda x: x[0])

def osa(cmd):
    try:
        return subprocess.run(['osascript', '-e', f'tell application "Spotify" to {cmd}'],
                              capture_output=True, text=True, timeout=3).stdout.strip()
    except Exception:
        return ''

def fetch(artist, title):
    q = urllib.parse.urlencode({'artist_name': artist, 'track_name': title})
    req = urllib.request.Request(f'https://lrclib.net/api/get?{q}',
                                 headers={'User-Agent': 'spot-lyrics/1.0'})  # lrclib rejects default UA
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.load(r).get('syncedLyrics') or ''
    except Exception:
        return ''

def gray(level):  # 0..1 -> ANSI 256 grayscale (232 dark .. 255 light)
    return f'\033[38;5;{232 + max(0, min(23, round(level * 23)))}m'

WHITE = '\033[1;97m'
RESET = '\033[0m'
WIN = 4  # lines shown above/below current

def render(lines, idx, cols):
    buf = ['\033[H\033[2J']  # home + clear
    for off in range(-WIN, WIN + 1):
        i = idx + off
        if 0 <= i < len(lines):
            if off == 0:
                color = WHITE
            elif off < 0:            # already sung -> fade toward black going up
                color = gray(0.55 * (1 + off / (WIN + 1)))
            else:                    # upcoming -> steady dim
                color = gray(0.35)
            text = lines[i][1] or '♪'
            buf.append(f'{color}{text[:cols]}{RESET}')
        else:
            buf.append('')
    sys.stdout.write('\n'.join(buf) + '\n')
    sys.stdout.flush()

def current_track():
    name = osa('name of current track')
    artist = osa('artist of current track')
    return artist, name

def main():
    cols = 100
    sys.stdout.write('\033[?25l')  # hide cursor
    key = None
    lines = []
    try:
        while True:
            if osa('player state') != 'playing':
                sys.stdout.write('\033[H\033[2J⏸  paused\n'); sys.stdout.flush()
                time.sleep(1); continue
            artist, title = current_track()
            if (artist, title) != key:
                key = (artist, title)
                lines = parse_lrc(fetch(artist, title))
                if not lines:
                    sys.stdout.write(f'\033[H\033[2Jno synced lyrics for {artist} – {title}\n')
                    sys.stdout.flush()
            if lines:
                try:
                    pos = float(osa('player position') or 0)
                except ValueError:
                    pos = 0
                idx = 0
                for i, (t, _) in enumerate(lines):
                    if t <= pos:
                        idx = i
                    else:
                        break
                render(lines, idx, cols)
            time.sleep(0.3)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write('\033[?25h\033[0m\n')  # restore cursor

def spotify_now():
    """One osascript for (state, artist, title, position) — fast path for statusline.
    Returns None if Spotify isn't running (and does NOT launch it)."""
    script = ('if application "Spotify" is running then tell application "Spotify" to '
              'return ((player state as text) & tab & (artist of current track) & tab & '
              '(name of current track) & tab & (player position as text))')
    try:
        out = subprocess.run(['osascript', '-e', script],
                             capture_output=True, text=True, timeout=3).stdout.strip()
    except Exception:
        return None
    p = out.split('\t')  # ponytail: tab delim; track names never contain tabs
    if len(p) < 4:
        return None
    try:
        pos = float(p[3])
    except ValueError:
        pos = 0.0
    return p[0], p[1], p[2], pos

def line_mode():
    """Print ONE current lyric line, for the statusline. Caches LRC per track."""
    import os, hashlib
    GRN = '\033[38;2;29;185;84m'  # Spotify green #1DB954
    now = spotify_now()
    if not now:
        print(f'{GRN}🎵 Spotify\033[0m'); return
    state, artist, title, pos = now
    if state != 'playing':
        print(f'{GRN}⏸ {title}\033[0m \033[2m— {artist}\033[0m'); return
    fallback = f'{GRN}🎵 {title}\033[0m \033[2m— {artist}\033[0m'
    cdir = '/tmp/spot-lrc'; os.makedirs(cdir, exist_ok=True)
    key = hashlib.md5(f'{artist}\t{title}'.encode()).hexdigest()
    cf = os.path.join(cdir, key)
    # NEVER fetch inline (network can block ~10s and the statusline gets cancelled).
    # On a miss: reserve the slot, fetch in the background, show the song name now.
    text = open(cf).read() if os.path.exists(cf) else None
    if not text:
        stale = (text is None) or (time.time() - os.path.getmtime(cf) >= 30)
        if stale:
            open(cf, 'w').write('')            # reserve slot; 30s cooldown from now
            subprocess.Popen(['python3', os.path.abspath(__file__), '--fetch', artist, title],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)  # detached bg fetch fills cache
        print(fallback); return
    lines = parse_lrc(text)
    if not lines:
        print(fallback); return
    cur = ''
    for t, ln in lines:
        if t <= pos:
            cur = ln
        else:
            break
    reset = '\033[0m'
    print(f'{GRN}🎵 {title}{reset} \033[1;97m{cur or artist}{reset}')  # green song, bright lyric

if __name__ == '__main__':
    if '--selftest' in sys.argv:
        p = parse_lrc('[00:35.18] one\n[00:43.56] two\n[01:00.00] three')
        assert p == [(35.18, 'one'), (43.56, 'two'), (60.0, 'three')], p
        assert parse_lrc('[00:10.0][00:20.0] echo') == [(10.0, 'echo'), (20.0, 'echo')]
        print('ok'); sys.exit(0)
    if '--fetch' in sys.argv:  # background: fetch lyrics, overwrite cache only on success
        import os, hashlib
        artist, title = sys.argv[2], sys.argv[3]
        text = fetch(artist, title)
        if text:
            cf = os.path.join('/tmp/spot-lrc', hashlib.md5(f'{artist}\t{title}'.encode()).hexdigest())
            open(cf, 'w').write(text)
        sys.exit(0)
    if '--line' in sys.argv:
        line_mode(); sys.exit(0)
    main()
