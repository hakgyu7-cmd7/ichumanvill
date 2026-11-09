#!/usr/bin/env python3
"""
source_tools.py - 1단계 "소재 발굴 & 역설계" 도구 (표준 라이브러리만 필수)

 1) search_outliers : YouTube Data API v3 로 'V/S 배율(조회수 / 구독자수)' 떡상 영상 탐색
 2) fetch_transcript: 영상 URL -> 대본 텍스트 (youtube-transcript-api -> yt-dlp 자막 -> faster-whisper 순서로 시도)
 3) vs_ratio / classify_ratio : 떡상 지수 계산기

외부 호출 함수(search_outliers)는 fetch 인자로 HTTP 함수를 주입할 수 있어 네트워크 없이 테스트됩니다.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

YT_API = "https://www.googleapis.com/youtube/v3"
UA = "Mozilla/5.0 (compatible; ShortsPipeline/3.0)"


class SourceError(RuntimeError):
    pass


# --------------------------------------------------------------------------- URL / ratio
_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def extract_video_id(url_or_id: str) -> Optional[str]:
    s = (url_or_id or "").strip()
    if _ID_RE.match(s):
        return s
    try:
        u = urllib.parse.urlparse(s)
    except ValueError:
        return None
    host = (u.hostname or "").lower().replace("www.", "").replace("m.", "")
    if host == "youtu.be":
        cand = u.path.strip("/").split("/")[0]
        return cand if _ID_RE.match(cand) else None
    if host.endswith("youtube.com"):
        if u.path == "/watch":
            cand = urllib.parse.parse_qs(u.query).get("v", [""])[0]
            return cand if _ID_RE.match(cand) else None
        m = re.match(r"^/(shorts|embed|live|v)/([A-Za-z0-9_-]{11})", u.path)
        if m:
            return m.group(2)
    return None


def vs_ratio(views: int, subscribers: int) -> Optional[float]:
    """떡상 지수 = 조회수 / 구독자수. 구독자 비공개(0)면 None."""
    if not subscribers or subscribers <= 0:
        return None
    return round(views / subscribers, 2)


def classify_ratio(ratio: Optional[float]) -> Dict[str, str]:
    if ratio is None:
        return {"grade": "unknown", "label": "구독자 비공개/0명 - 판별 불가"}
    if ratio < 1:
        return {"grade": "normal", "label": "일반 영상 (수집 제외)"}
    if ratio < 5:
        return {"grade": "ok", "label": "구독자 수준 이상 (1배 이상)"}
    if ratio < 10:
        return {"grade": "good", "label": "알고리즘 간택 (1차 후보, 5배 이상)"}
    return {"grade": "viral", "label": "초특급 벤치마킹 타깃 (10배 이상)"}


def parse_iso_duration(s: str) -> int:
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    if not m:
        return 0
    d, h, mi, se = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + se


# --------------------------------------------------------------------------- YouTube outliers
def _http_json(url: str, timeout: int = 20) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:300]
        raise SourceError(f"YouTube API HTTP {e.code}: {body}") from e
    except OSError as e:
        raise SourceError(f"네트워크 오류: {e}") from e


def _api(endpoint: str, params: Dict[str, Any], fetch: Callable[[str], Dict[str, Any]]) -> Dict[str, Any]:
    return fetch(f"{YT_API}/{endpoint}?{urllib.parse.urlencode(params)}")


def search_outliers(
    api_key: str,
    query: str,
    days: int = 30,
    min_ratio: float = 10.0,
    max_results: int = 50,
    region: Optional[str] = None,
    language: Optional[str] = None,
    max_duration_sec: int = 180,
    fetch: Optional[Callable[[str], Dict[str, Any]]] = None,
    now: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """최근 N일 내 키워드 영상 중 V/S 배율이 min_ratio 이상인 숏폼을 배율 내림차순으로 반환.

    API 쿼터: search.list 100 + videos.list 1 + channels.list 1 = 약 102 유닛/호출 (일 10,000 무료).
    """
    if not api_key:
        raise SourceError("YouTube Data API 키가 없습니다 (환경변수 YOUTUBE_API_KEY 또는 대시보드 입력).")
    if not query.strip():
        raise SourceError("검색 키워드를 입력하세요.")
    fetch = fetch or _http_json
    now = now or datetime.now(timezone.utc)
    after = (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    params: Dict[str, Any] = {
        "part": "snippet", "type": "video", "q": query, "maxResults": min(50, max(1, max_results)),
        "order": "viewCount", "videoDuration": "short", "publishedAfter": after, "key": api_key,
    }
    if region:
        params["regionCode"] = region
    if language:
        params["relevanceLanguage"] = language
    found = _api("search", params, fetch)
    ids = [it["id"]["videoId"] for it in found.get("items", []) if it.get("id", {}).get("videoId")]
    if not ids:
        return []
    vids = _api("videos", {"part": "snippet,contentDetails,statistics", "id": ",".join(ids), "key": api_key}, fetch).get("items", [])
    chan_ids = sorted({v["snippet"]["channelId"] for v in vids})
    subs: Dict[str, int] = {}
    for i in range(0, len(chan_ids), 50):
        chunk = chan_ids[i:i + 50]
        for ch in _api("channels", {"part": "statistics", "id": ",".join(chunk), "key": api_key}, fetch).get("items", []):
            st = ch.get("statistics", {})
            subs[ch["id"]] = 0 if st.get("hiddenSubscriberCount") else int(st.get("subscriberCount", 0) or 0)
    out: List[Dict[str, Any]] = []
    for v in vids:
        dur = parse_iso_duration(v.get("contentDetails", {}).get("duration", ""))
        if dur and dur > max_duration_sec:
            continue
        views = int(v.get("statistics", {}).get("viewCount", 0) or 0)
        sub = subs.get(v["snippet"]["channelId"], 0)
        ratio = vs_ratio(views, sub)
        if ratio is None or ratio < min_ratio:
            continue
        sn = v["snippet"]
        out.append({
            "platform": "YouTube", "video_id": v["id"], "url": f"https://www.youtube.com/shorts/{v['id']}",
            "title": sn.get("title", ""), "channel": sn.get("channelTitle", ""), "views": views, "subscribers": sub,
            "ratio": ratio, "grade": classify_ratio(ratio)["grade"], "duration": dur,
            "published": sn.get("publishedAt", ""), "thumbnail": (sn.get("thumbnails", {}).get("medium") or {}).get("url", ""),
        })
    out.sort(key=lambda x: x["ratio"], reverse=True)
    return out


# --------------------------------------------------------------------------- transcript
def parse_vtt(text: str) -> str:
    """WebVTT(자동자막 포함) -> 중복 제거된 순수 텍스트."""
    lines: List[str] = []
    last = ""
    for raw in text.splitlines():
        s = raw.strip()
        if not s or s.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")) or "-->" in s or re.fullmatch(r"\d+", s):
            continue
        s = re.sub(r"<[^>]+>", "", s)
        s = re.sub(r"&nbsp;|&amp;|&lt;|&gt;", lambda m: {"&nbsp;": " ", "&amp;": "&", "&lt;": "<", "&gt;": ">"}[m.group(0)], s).strip()
        if not s or s == last or last.endswith(s):
            continue
        lines.append(s)
        last = s
    return " ".join(lines)


def _via_transcript_api(vid: str, langs: List[str]) -> Optional[Dict[str, str]]:
    try:
        import youtube_transcript_api as yta  # type: ignore
    except ImportError:
        return None
    try:
        api_cls = yta.YouTubeTranscriptApi
        if hasattr(api_cls, "get_transcript"):  # 구버전 (<1.0)
            segs = api_cls.get_transcript(vid, languages=langs)
            text = " ".join(s["text"].replace("\n", " ") for s in segs)
        else:  # 1.x
            fetched = api_cls().fetch(vid, languages=langs)
            text = " ".join(getattr(s, "text", "") for s in fetched)
        text = re.sub(r"\s+", " ", text).strip()
        return {"text": text, "method": "youtube-transcript-api"} if text else None
    except Exception:
        return None


def _ytdlp_cmd() -> Optional[List[str]]:
    exe = shutil.which("yt-dlp")
    if exe:
        return [exe]
    try:
        import yt_dlp  # type: ignore  # noqa: F401
        return [sys.executable, "-m", "yt_dlp"]
    except ImportError:
        return None


def _via_ytdlp_subs(url: str, langs: List[str]) -> Optional[Dict[str, str]]:
    cmd = _ytdlp_cmd()
    if not cmd:
        return None
    with tempfile.TemporaryDirectory() as td:
        pat = ",".join(f"{l}.*" for l in langs) + "," + ",".join(langs)
        args = cmd + ["--skip-download", "--write-subs", "--write-auto-subs", "--sub-langs", pat, "--sub-format", "vtt",
                      "--no-warnings", "-o", os.path.join(td, "%(id)s"), url]
        try:
            subprocess.run(args, capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired):
            return None
        def lang_rank(p: Path) -> int:
            return next((i for i, l in enumerate(langs) if f".{l}" in p.name), len(langs))
        files = sorted(Path(td).glob("*.vtt"), key=lang_rank)
        for f in files:
            text = parse_vtt(f.read_text(encoding="utf-8", errors="replace"))
            if text:
                return {"text": text, "method": "yt-dlp 자막"}
    return None


def _via_whisper(url: str, langs: List[str], model_size: str = "small") -> Optional[Dict[str, str]]:
    cmd = _ytdlp_cmd()
    if not cmd:
        return None
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except ImportError:
        return None
    with tempfile.TemporaryDirectory() as td:
        try:
            subprocess.run(cmd + ["-x", "--audio-format", "mp3", "--no-warnings", "-o", os.path.join(td, "a.%(ext)s"), url],
                           capture_output=True, text=True, timeout=300, check=True)
            audio = next(Path(td).glob("a.*"))
            model = WhisperModel(model_size, device="auto", compute_type="int8")
            segs, info = model.transcribe(str(audio), language=None)
            text = " ".join(s.text.strip() for s in segs).strip()
            return {"text": text, "method": f"faster-whisper({info.language})"} if text else None
        except Exception:
            return None


def fetch_transcript(url: str, langs: Optional[List[str]] = None, use_whisper: bool = True) -> Dict[str, str]:
    """영상 URL -> {'text', 'method', 'video_id'}. 모두 실패하면 SourceError (수동 붙여넣기 안내 포함)."""
    langs = langs or ["ko", "en"]
    vid = extract_video_id(url)
    if not vid:
        raise SourceError("유효한 YouTube 링크가 아닙니다 (youtu.be / youtube.com/watch / shorts 지원).")
    for fn in (lambda: _via_transcript_api(vid, langs), lambda: _via_ytdlp_subs(url, langs),
               (lambda: _via_whisper(url, langs)) if use_whisper else (lambda: None)):
        res = fn()
        if res:
            res["video_id"] = vid
            return res
    raise SourceError(
        "자막을 자동으로 가져오지 못했습니다. 아래 중 하나를 사용하세요:\n"
        "  1) pip install youtube-transcript-api yt-dlp  (자동 자막 추출)\n"
        "  2) 유튜브 영상 > 설명 더보기 > 스크립트 표시 후 텍스트를 직접 복사해서 붙여넣기\n"
        "  3) pip install faster-whisper  (음성 인식, 자막 없는 영상)")


def tool_status() -> Dict[str, Any]:
    def mod(n: str) -> bool:
        try:
            __import__(n)
            return True
        except ImportError:
            return False
    return {
        "youtube_api_key": bool(os.environ.get("YOUTUBE_API_KEY")),
        "youtube_transcript_api": mod("youtube_transcript_api"),
        "yt_dlp": bool(_ytdlp_cmd()),
        "faster_whisper": mod("faster_whisper"),
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="소재 발굴 도구")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("outliers"); a.add_argument("query"); a.add_argument("--days", type=int, default=30)
    a.add_argument("--min-ratio", type=float, default=10); a.add_argument("--region"); a.add_argument("--lang")
    b = sub.add_parser("transcript"); b.add_argument("url")
    args = ap.parse_args()
    try:
        if args.cmd == "outliers":
            for r in search_outliers(os.environ.get("YOUTUBE_API_KEY", ""), args.query, args.days, args.min_ratio, region=args.region, language=args.lang):
                print(f"{r['ratio']:>7}x  {r['views']:>10,}/{r['subscribers']:<9,} {r['title'][:50]}  {r['url']}")
        else:
            print(fetch_transcript(args.url)["text"])
    except SourceError as e:
        print("오류:", e, file=sys.stderr)
        sys.exit(1)
