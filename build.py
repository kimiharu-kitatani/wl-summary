#!/usr/bin/env python3
"""data/wl.json + summaries.json + data/captions_status.json → data/data.json"""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
def ld(f, d):
    p = os.path.join(H, f)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else d
wl, sm, st = ld('data/wl.json', []), ld('summaries.json', {}), ld('data/captions_status.json', {})
out = []
for it in wl:
    v = it['videoId']; s = sm.get(v, {})
    out.append({**it, 'thumbnail': f'https://i.ytimg.com/vi/{v}/mqdefault.jpg',
                'summary_ja': s.get('summary_ja', ''), 'points': s.get('points', []),
                'captions': st.get(v, {}).get('status', 'unknown')})
json.dump(out, open(os.path.join(H, 'data/data.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'{len(out)} 件 → data/data.json（要約あり {sum(1 for o in out if o["summary_ja"])} 件）')
