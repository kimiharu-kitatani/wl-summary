#!/usr/bin/env python3
"""data/wl.json + summaries.json + summaries_detail.json + data/captions_status.json + data/video_meta.json → data/data.json
並び順は data/wl.json（後で見るの並び順）をそのまま wl_index として保持します。"""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
def ld(f, d):
    p = os.path.join(H, f)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else d
wl, sm, sd = ld('data/wl.json', []), ld('summaries.json', {}), ld('summaries_detail.json', {})
st, meta = ld('data/captions_status.json', {}), ld('data/video_meta.json', {})
out = []
for i, it in enumerate(wl):
    v = it['videoId']; s = sm.get(v, {}); m = meta.get(v, {})
    row = {**it, 'wl_index': i, 'thumbnail': f'https://i.ytimg.com/vi/{v}/mqdefault.jpg',
           'summary_ja': s.get('summary_ja', ''), 'points': s.get('points', []),
           'captions': st.get(v, {}).get('status', 'unknown')}
    if m.get('upload_date'): row['upload_date'] = m['upload_date']
    if sd.get(v, {}).get('detail'): row['detail'] = sd[v]['detail']
    out.append(row)
json.dump(out, open(os.path.join(H, 'data/data.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'{len(out)} 件 → data/data.json（要約 {sum(1 for o in out if o["summary_ja"])} / 投稿日 {sum(1 for o in out if o.get("upload_date"))} / 詳細 {sum(1 for o in out if o.get("detail"))}）')
