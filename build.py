#!/usr/bin/env python3
"""data/wl.json + summaries.json + summaries_detail.json + data/captions_status.json + data/video_meta.json
   + data/archive.json → data/data.json
- 並び順は data/wl.json（後で見るの並び順）を wl_index として保持
- 後で見るから消えた動画は削除せず data/archive.json に保存し、data.json では removed: true を付けて残す
  （data/wl_meta.json の complete が true のときだけ「消えた」と判定。不完全な一覧で誤ってアーカイブしない）
- アーカイブ済みの動画が後で見るに戻ったら復帰させる
- last_summarized_at: summaries.json（と summaries_detail.json）を触った最新 git commit 時刻を +09:00 で
  data/summary_meta.json に記録（data.json は拡張が配列前提のため配列のまま）。ビューアが読んで表示。
  旧 data.json が {videos,last_summarized_at} でも読む"""
import json, os, datetime, subprocess
H = os.path.dirname(os.path.abspath(__file__))
JST = datetime.timezone(datetime.timedelta(hours=9))
def ld(f, d):
    p = os.path.join(H, f)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else d
def save(f, obj):
    json.dump(obj, open(os.path.join(H, f), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
def as_videos(raw):
    """data.json が配列（旧）でも {videos:...}（新）でも動画リストを返す。メタも返す。"""
    if isinstance(raw, dict):
        return list(raw.get('videos') or []), raw.get('last_summarized_at')
    if isinstance(raw, list):
        return raw, None
    return [], None
def to_jst_iso(s):
    """git %cI などを Asia/Tokyo の ISO（+09:00）に揃える。失敗時 None。"""
    if not s or not isinstance(s, str):
        return None
    try:
        t = s.strip().replace('Z', '+00:00')
        dt = datetime.datetime.fromisoformat(t)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=JST)
        return dt.astimezone(JST).isoformat(timespec='seconds')
    except Exception:
        return None
def git_commit_iso(*paths):
    """指定パスを触った最新コミットの committer date（JST ISO）。git が使えなければ None。"""
    best = None
    for path in paths:
        try:
            out = subprocess.check_output(
                ['git', 'log', '-1', '--format=%cI', '--', path],
                cwd=H, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            out = ''
        iso = to_jst_iso(out)
        if iso and (best is None or iso > best):
            best = iso
    return best
wl, sm, sd = ld('data/wl.json', []), ld('summaries.json', {}), ld('summaries_detail.json', {})
st, meta = ld('data/captions_status.json', {}), ld('data/video_meta.json', {})
archive, prev_raw, wlm = ld('data/archive.json', {}), ld('data/data.json', []), ld('data/wl_meta.json', {})
prev, prev_last = as_videos(prev_raw)
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

# 要約ファイルを触った最新コミット時刻。取れなければ前回値を維持（推測しない）
# data.json は拡張機能が配列前提のため配列のまま。時刻は data/summary_meta.json に記録し、
# ビューアが読む。将来拡張が {videos,last_summarized_at} に対応したら data.json 側にも載せられる。
last_sum = git_commit_iso('summaries.json', 'summaries_detail.json') or prev_last
# 前回がラッパー形式でも as_videos 済み。配列で保存（拡張互換）
save('data/archive.json', archive)
save('data/data.json', out)
save('data/summary_meta.json', {'last_summarized_at': last_sum})
print(f'{len(out)} 件 → data/data.json（後で見る {len(wl)} / アーカイブ {len(archive)} / 要約 {sum(1 for o in out if o["summary_ja"])} / 投稿日 {sum(1 for o in out if o.get("upload_date"))} / 詳細 {sum(1 for o in out if o.get("detail"))} / 最終要約 {last_sum or "不明"}）'
      + ('' if wlm.get('complete') else '  ※ wl_meta.json が complete でないため新規アーカイブ判定はスキップ'))
