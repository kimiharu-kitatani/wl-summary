#!/usr/bin/env python3
"""data/wl.json の各動画の投稿日を yt-dlp で取得し data/video_meta.json に保存（取得済みはスキップ）。
使い方: python3 fetch_meta.py <repoディレクトリ>"""
import json, os, sys, subprocess, time
R = sys.argv[1] if len(sys.argv) > 1 else '.'
Y = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv/bin/yt-dlp')
mp = os.path.join(R, 'data/video_meta.json')
meta = json.load(open(mp)) if os.path.exists(mp) else {}
for it in json.load(open(os.path.join(R, 'data/wl.json'), encoding='utf-8')):
    v = it['videoId']
    if meta.get(v, {}).get('upload_date'): continue
    r = subprocess.run([Y, '--skip-download', '--no-warnings', '--print', '%(upload_date)s', f'https://www.youtube.com/watch?v={v}'], capture_output=True, text=True, timeout=120)
    d = r.stdout.strip()
    if len(d) == 8 and d.isdigit():
        meta[v] = {'upload_date': f'{d[:4]}-{d[4:6]}-{d[6:]}', 'source': 'yt-dlp'}
    print(v, d or ('ERR ' + r.stderr.strip()[-120:]), flush=True)
    json.dump(meta, open(mp, 'w'), ensure_ascii=False, indent=1)
    time.sleep(1.5)
