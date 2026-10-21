# 要約の作成手順・ルール（Bot用）

## 手順
1. `data/transcripts/<動画ID>.txt` を読む（字幕がない動画は要約しない。推測で書かない）
2. 通常の要約を `summaries.json` に書く：`{動画ID: {summary_ja, points:[...]}}`
3. `data/detail_requests.json` にある動画は、詳しい要約を `summaries_detail.json` に書く：`{動画ID: {detail}}`、書いたらリクエストの status を `done` にする
4. 投稿日は `fetch_meta.py`（yt-dlp）で `data/video_meta.json` に取得する（推測しない）
5. `python3 build.py` で `data/data.json` を作り直してコミット

## 通常要約の長さ（2026-10-22 改訂：従来の約半分・より簡潔に）
- `summary_ja`：**2文・80〜130字程度**。何の動画か＋一番の主張だけ
- `points`：**3つまで、各40字以内**。数字・固有名詞など具体的なものを優先
- 前置き（「この動画では〜」）や感想は書かない。字幕にない情報は足さない

## 詳しい要約（リクエストされた動画のみ）
- 600〜1200字程度。流れに沿って見出しなしの段落で。具体例・数字・結論を含める
- 字幕にない情報は書かない
