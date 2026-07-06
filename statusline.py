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

DIM, R, CY, YL = '\033[2m', '\033[0m', '\033[36m', '\033[33m'
p = []
if sid:            p.append(f'{DIM}◈ {sid}{R}')
p.append(f'{CY}{model}{R}')
p.append(f'{DIM}📁 {folder}{R}')
if branch:         p.append(f'⎇ {branch}')
if pr:             p.append(f'{YL}PR#{pr}{R}')
if isinstance(tok, int):
    p.append(f'⛁ {tok/1000:.0f}k' + (f' {pct}%' if pct is not None else ''))
elif pct is not None:
    p.append(f'⛁ {pct}%')

line = f' {DIM}·{R} '.join(p)
if lyric:
    line += f'   {lyric}'
print(line)
