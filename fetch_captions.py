#!/usr/bin/env python3
"""wl.json の各動画の字幕を取得し transcripts/<id>.txt に保存。字幕なしは captions_status.json に記録。
使い方: python3 fetch_captions.py wl.json"""
import json, sys, os, re, subprocess, glob, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
YTDLP = os.path.join(HERE, '.venv/bin/yt-dlp')
if not os.path.exists(YTDLP):
    subprocess.run([sys.executable, '-m', 'venv', os.path.join(HERE, '.venv')], check=True)
    subprocess.run([os.path.join(HERE, '.venv/bin/pip'), 'install', '-q', 'yt-dlp'], check=True)
TDIR = os.path.join(HERE, 'transcripts'); os.makedirs(TDIR, exist_ok=True)
STATUS = os.path.join(HERE, 'captions_status.json')

def vtt_to_text(path):
    lines, prev = [], None
    for l in open(path, encoding='utf-8'):
        l = l.strip()
        if not l or l == 'WEBVTT' or '-->' in l or l.startswith(('Kind:', 'Language:', 'NOTE')) or l.isdigit():
            continue
        l = re.sub(r'<[^>]+>', '', l).strip()
        if l and l != prev: lines.append(l); prev = l
    return '\n'.join(lines)

def attempt(vid, auto, langs, tmp):
    cmd = [YTDLP, '--skip-download', '--ignore-no-formats-error',
           '--extractor-args', 'youtube:player_client=web_embedded',  # 既定クライアントはbot判定されるため（cookie不使用）
           '--sub-format', 'vtt', '--sub-langs', langs,
           '-o', os.path.join(tmp, '%(id)s.%(ext)s'), '--no-warnings',
           '--write-auto-subs' if auto else '--write-subs', f'https://www.youtube.com/watch?v={vid}']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    files = glob.glob(os.path.join(tmp, f'{vid}*.vtt'))
    return files, r.stderr.strip()

def fetch(vid):
    tmp = tempfile.mkdtemp(); err = ''
    try:
        # 優先順: 手動ja → 自動ja → 手動en → 自動en
        for auto, langs, label in [(False, 'ja', 'ja'), (True, 'ja', 'ja-auto'), (False, 'en.*', 'en'), (True, 'en', 'en-auto')]:
            files, err = attempt(vid, auto, langs, tmp)
            if files:
                text = vtt_to_text(sorted(files)[0])
                if text:
                    open(os.path.join(TDIR, f'{vid}.txt'), 'w', encoding='utf-8').write(text)
                    return {'status': 'ok', 'lang': label, 'chars': len(text)}
        blocked = 'not a bot' in err or 'cookies' in err
        return {'status': 'blocked' if blocked else ('error' if 'ERROR' in err else 'no_captions'), 'detail': err[-300:]}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def main():
    items = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'wl.json', encoding='utf-8'))
    status = json.load(open(STATUS)) if os.path.exists(STATUS) else {}
    for it in items:
        vid = it['videoId']
        if status.get(vid, {}).get('status') == 'ok' and os.path.exists(os.path.join(TDIR, f'{vid}.txt')):
            continue
        status[vid] = fetch(vid)
        print(vid, status[vid]['status'], status[vid].get('lang', status[vid].get('detail', '')))
        json.dump(status, open(STATUS, 'w'), ensure_ascii=False, indent=2)
if __name__ == '__main__': main()
