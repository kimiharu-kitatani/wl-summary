#!/usr/bin/env python3
"""Collect delete requests: open GitHub issues labelled delete-request + data/delete_requests.json.
Prints a JSON list of {videoId,title,issue,setVideoId,inWL}."""
import json, os, re, urllib.request
REPO = "kimiharu-kitatani/wl-summary"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ID = re.compile(r"^([A-Za-z0-9_-]{11})(?:\t(.*))?$")

def load(p, d):
    try:
        with open(os.path.join(ROOT, p), encoding="utf-8") as f: return json.load(f)
    except Exception: return d

def issues():
    out, page = [], 1
    while True:
        u = f"https://api.github.com/repos/{REPO}/issues?labels=delete-request&state=open&per_page=100&page={page}"
        req = urllib.request.Request(u, headers={"Accept": "application/vnd.github+json", "User-Agent": "wl-summary"})
        tok = os.environ.get("GITHUB_TOKEN")
        if tok: req.add_header("Authorization", "Bearer " + tok)
        with urllib.request.urlopen(req, timeout=30) as r: batch = json.load(r)
        out += [i for i in batch if "pull_request" not in i]
        if len(batch) < 100: return out
        page += 1

def main():
    wl = {v["videoId"]: v for v in load("data/wl.json", []) if isinstance(v, dict) and v.get("videoId")}
    res = {}
    for it in issues():
        for line in (it.get("body") or "").splitlines():
            m = ID.match(line.strip("\r").rstrip())
            if m and m.group(1) not in res:
                res[m.group(1)] = {"title": (m.group(2) or "").strip(), "issue": it["number"]}
    for vid, v in (load("data/delete_requests.json", {}) or {}).items():
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", vid) and vid not in res:
            res[vid] = {"title": (v or {}).get("title", ""), "issue": None}
    out = []
    for vid, r in res.items():
        w = wl.get(vid)
        out.append({"videoId": vid, "title": r["title"] or (w or {}).get("title", ""), "issue": r["issue"],
                    "setVideoId": (w or {}).get("setVideoId"), "inWL": bool(w)})
    print(json.dumps(out, ensure_ascii=False, indent=1))

if __name__ == "__main__": main()
