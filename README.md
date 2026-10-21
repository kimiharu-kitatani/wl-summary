# 後で見る 要約一覧

YouTubeの「後で見る」を毎日自動で取り込み、字幕から作った日本語要約をスマホ・PCで見られるようにする仕組みです（すべて無料）。

> ⚠️ **注意：無料のGitHub Pagesは「公開（Public）リポジトリ」が必要です。**
> 後で見るの動画一覧・字幕テキスト・要約はインターネット上で誰でも見られる状態になります。気になる場合は公開しない運用（Pagesを使わない）を検討してください。

## 1. リポジトリを作る
1. GitHubにログイン →「New repository」
2. 名前を決める（例: `wl-summary`）、**Public** を選んで作成
3. このフォルダの中身（`index.html`, `viewer/`, `data/`, `build.py`, `summaries.json`, `README.md`）をアップロード（「Add file」→「Upload files」）

## 2. Fine-grained トークンを作る
1. GitHub 右上アイコン → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** →「Generate new token」
2. Repository access:「Only select repositories」で作ったリポジトリだけを選ぶ
3. Permissions → Repository permissions → **Contents: Read and write**
4. 有効期限を決めて作成し、表示されたトークンをコピー（期限が切れたら作り直して設定し直します）

## 3. 拡張機能を入れる
1. `extension.zip` を解凍
2. Chromeで `chrome://extensions` →「デベロッパー モード」をオン
3. 「パッケージ化されていない拡張機能を読み込む」→ 解凍したフォルダを選択

## 4. 拡張機能の設定
1. 拡張機能アイコン →「設定を開く」
2. GitHubユーザー名・リポジトリ名・ブランチ（通常 `main`）・トークンを入力して保存
3. ポップアップの「今すぐ同期」で動作確認。結果とログがポップアップに表示されます
4. 以降は1日1回自動で実行されます（Chromeが起動していてYouTubeにログインしている必要があります）

拡張機能は `data/wl.json`（一覧）、`data/transcripts/<動画ID>.txt`（字幕）、`data/captions_status.json`（字幕の取得状況）を保存します。

## 5. GitHub Pages を有効にする
1. リポジトリ → Settings → Pages
2. Source:「Deploy from a branch」、Branch: `main` / `/(root)` → Save
3. 数分後に `https://<ユーザー名>.github.io/<リポジトリ名>/` で要約一覧が見られます

## 要約について
要約はBotが字幕を読んで `summaries.json` に書き、`python3 build.py` で `data/data.json` を作り直します。字幕がない動画は「字幕がないため要約できません」と表示されます。
