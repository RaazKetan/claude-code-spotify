#!/usr/bin/env python3
# Claude Code statusline: session · model · folder · branch · PR · tokens · 🎵 lyric
# All fields from the stdin JSON except branch (local git) and lyric (spotify-lyrics.py).
import sys, json, os, subprocess

def sh(args):
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=2).stdout.strip()
    except Exception:
        return ''

try:
    d = json.load(sys.stdin)
except Exception:
    d = {}

cwd = d.get('cwd') or d.get('workspace', {}).get('current_dir') or os.getcwd()
sid = (d.get('session_id') or '')[:8]
model = d.get('model', {}).get('display_name', '?')
folder = os.path.basename(cwd.rstrip('/')) or cwd
branch = sh(['git', '-C', cwd, 'branch', '--show-current'])  # '' if not a repo / detached
pr = (d.get('pr') or {}).get('number')
cw = d.get('context_window', {})
pct = cw.get('used_percentage')
tok = cw.get('total_input_tokens')
lyric = sh(['python3', os.path.expanduser('~/.claude/spotify-lyrics.py'), '--line'])

def rgb(r, g, b): return f'\033[38;2;{r};{g};{b}m'
R, DIM, B = '\033[0m', '\033[2m', '\033[1m'
GREEN  = rgb(29, 185, 84)    # Spotify green
BLUE   = rgb(88, 166, 255)
PURPLE = rgb(190, 149, 255)
ORANGE = rgb(255, 167, 38)
RED    = rgb(248, 81, 73)
GRAY   = rgb(139, 148, 158)
SEP    = f' {GRAY}{DIM}•{R} '  # dim bullet, safe in any font

p = []
if sid:      p.append(f'{GRAY}◈ {sid}{R}')          # session  ◈
p.append(f'{PURPLE}{B}✦ {model}{R}')                # model    ✦
p.append(f'{BLUE}\U0001f4c1 {folder}{R}')                # folder   📁
if branch:   p.append(f'{GREEN}⎇ {branch}{R}')      # branch   ⎇
if pr:       p.append(f'{ORANGE}⇅ #{pr}{R}')        # PR       ⇅

if isinstance(tok, int) or pct is not None:
    pc = pct if pct is not None else 0
    tcol = RED if pc >= 80 else ORANGE if pc >= 50 else GREEN
    filled = max(0, min(5, round(pc / 20)))
    bar = tcol + '▰' * filled + f'{GRAY}{DIM}' + '▱' * (5 - filled) + R  # ▰▱
    label = f'{tok/1000:.0f}k' if isinstance(tok, int) else f'{pc}%'
    p.append(f'{bar} {tcol}{label}{R}')

line = SEP.join(p)
if lyric:
    line += f'   {DIM}{GRAY}│{R} {lyric}'  # │ divider before music
print(line)
