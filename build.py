#!/usr/bin/env python3
"""data/wl.json + summaries.json + summaries_detail.json + data/captions_status.json + data/video_meta.json
   + data/archive.json → data/data.json
- 並び順は data/wl.json（後で見るの並び順）を wl_index として保持
- 後で見るから消えた動画は削除せず data/archive.json に保存し、data.json では removed: true を付けて残す
  （data/wl_meta.json の complete が true のときだけ「消えた」と判定。不完全な一覧で誤ってアーカイブしない）
- アーカイブ済みの動画が後で見るに戻ったら復帰させる"""
import json, os, datetime
H = os.path.dirname(os.path.abspath(__file__))
def ld(f, d):
    p = os.path.join(H, f)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else d
def save(f, obj):
    json.dump(obj, open(os.path.join(H, f), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
wl, sm, sd = ld('data/wl.json', []), ld('summaries.json', {}), ld('summaries_detail.json', {})
st, meta = ld('data/captions_status.json', {}), ld('data/video_meta.json', {})
archive, prev, wlm = ld('data/archive.json', {}), ld('data/data.json', []), ld('data/wl_meta.json', {})
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
cur = {it['videoId'] for it in wl}
BASE = ('videoId', 'title', 'channel', 'duration', 'url')

# 前回の data.json にあって今の一覧に無い動画 → アーカイブ（一覧が完全なときだけ）
if wlm.get('complete'):
    for row in prev:
        v = row['videoId']
        if v not in cur and v not in archive:
            archive[v] = {'item': {k: row.get(k, '') for k in BASE}, 'removed_at': row.get('removed_at') or now,
                          'reason': row.get('removed_reason') or 'not_in_wl'}
# 後で見るに戻った動画はアーカイブから外す
for v in list(archive):
    if v in cur: del archive[v]

def make(it, i, arc=None):
    v = it['videoId']; s = sm.get(v, {}); m = meta.get(v, {})
    row = {**{k: it.get(k, '') for k in BASE}, 'wl_index': i, 'thumbnail': f'https://i.ytimg.com/vi/{v}/mqdefault.jpg',
           'summary_ja': s.get('summary_ja', ''), 'points': s.get('points', []),
           'captions': st.get(v, {}).get('status', 'unknown')}
    if m.get('upload_date'): row['upload_date'] = m['upload_date']
    if sd.get(v, {}).get('detail'): row['detail'] = sd[v]['detail']
    if arc: row.update(removed=True, removed_at=arc.get('removed_at', ''), removed_reason=arc.get('reason', ''))
    return row
out = [make(it, i) for i, it in enumerate(wl)]
for j, (v, a) in enumerate(sorted(archive.items(), key=lambda kv: kv[1].get('removed_at', ''), reverse=True)):
    out.append(make(a.get('item') or {'videoId': v, 'url': f'https://www.youtube.com/watch?v={v}'}, len(wl) + j, a))
save('data/archive.json', archive)
save('data/data.json', out)
print(f'{len(out)} 件 → data/data.json（後で見る {len(wl)} / アーカイブ {len(archive)} / 要約 {sum(1 for o in out if o["summary_ja"])} / 投稿日 {sum(1 for o in out if o.get("upload_date"))} / 詳細 {sum(1 for o in out if o.get("detail"))}）'
      + ('' if wlm.get('complete') else '  ※ wl_meta.json が complete でないため新規アーカイブ判定はスキップ'))
