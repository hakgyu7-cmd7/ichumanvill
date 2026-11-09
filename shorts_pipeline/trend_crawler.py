#!/usr/bin/env python3
"""
trend_crawler.py - 소재 트렌드 수집기 (쿠팡 / 틱톡 / 레딧 / 유튜브)

정직한 동작 원칙
  * 실제 수집에 성공한 항목만 live=True 로 표시한다.
  * 실패/차단/키 없음이면 data/trends_seed.json 샘플로 대체하되 live=False + 사유(note)를 함께 반환한다.
  * 쿠팡은 봇 차단(403), 틱톡 크리에이티브 센터는 공식 API가 없어 '실시간 수집이 막힐 수 있음'이 기본 전제다.
    -> 대시보드의 [직접 추가](붙여넣기) + 수동 링크를 함께 쓰는 하이브리드 방식을 권장한다.
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import source_tools

BASE = Path(__file__).resolve().parent
SEED_PATH = BASE / "data" / "trends_seed.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
COUPANG_URL = os.environ.get("COUPANG_BEST_URL", "https://www.coupang.com/np/best100")


def load_seed() -> Dict[str, Any]:
    with open(SEED_PATH, encoding="utf-8") as f:
        return json.load(f)


def _get(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 12) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


class TrendCrawler:
    # ------------------------------------------------------------------ seed
    @staticmethod
    def seed_items(platforms: Optional[List[str]] = None, cat: Optional[str] = None) -> List[Dict[str, Any]]:
        out = []
        for it in load_seed()["items"]:
            if platforms and it["platform"] not in platforms:
                continue
            if cat and cat != "general" and it["cat"] != cat:
                continue
            out.append({**it, "live": False, "sample": True})
        return out

    # ------------------------------------------------------------------ coupang
    @staticmethod
    def parse_coupang(page: str, limit: int = 20) -> List[Dict[str, Any]]:
        names = re.findall(r'class="[^"]*(?:name|title)[^"]*"[^>]*>\s*([^<]{4,120}?)\s*<', page)
        seen, items = set(), []
        for n in names:
            n = html.unescape(n).strip()
            if n and n not in seen:
                seen.add(n)
                items.append({"platform": "쿠팡", "title": n, "keyword": " ".join(n.split()[:3]), "cat": "shopping", "live": True})
            if len(items) >= limit:
                break
        return items

    @classmethod
    def get_coupang_best(cls, live: bool = True, limit: int = 20, fetch: Optional[Callable[[str], str]] = None) -> Dict[str, Any]:
        if live:
            try:
                items = cls.parse_coupang((fetch or _get)(COUPANG_URL), limit)
                if items:
                    return {"items": items, "live": True, "note": "쿠팡 페이지 수집 성공 (구조 변경 시 파싱이 깨질 수 있음)"}
                note = "페이지는 열렸지만 상품명을 찾지 못했습니다 (페이지 구조 변경/로그인·봇 검증 페이지)"
            except urllib.error.HTTPError as e:
                note = f"쿠팡 접근 거부(HTTP {e.code}) - 봇 차단. 직접 확인한 상품을 [직접 추가]로 넣어 주세요"
            except OSError as e:
                note = f"네트워크 오류: {e}"
        else:
            note = "오프라인 모드"
        return {"items": cls.seed_items(["쿠팡"]), "live": False, "note": note + " -> 샘플 목록으로 대체"}

    # ------------------------------------------------------------------ tiktok
    @classmethod
    def get_tiktok_trends(cls, live: bool = True) -> Dict[str, Any]:
        # 공식 API 없음. 비공식 스크래핑은 계정/IP 차단 및 약관 위험이 있어 자동 수집을 하지 않는다.
        return {"items": cls.seed_items(["틱톡"]), "live": False,
                "note": "TikTok 크리에이티브 센터는 공식 수집 API가 없습니다. 수동 링크로 확인한 키워드/URL을 [직접 추가]로 넣어 주세요 (샘플 표시 중)"}

    # ------------------------------------------------------------------ reddit
    @classmethod
    def parse_reddit(cls, data: Dict[str, Any], sub: str, cat: str, limit: int) -> List[Dict[str, Any]]:
        items = []
        for ch in (data.get("data", {}).get("children") or []):
            d = ch.get("data", {})
            if d.get("stickied") or d.get("over_18") or not d.get("title"):
                continue
            items.append({"platform": f"레딧 r/{sub}", "title": d["title"].strip(), "keyword": d["title"].strip()[:40], "cat": cat,
                          "url": "https://www.reddit.com" + d.get("permalink", ""), "score": d.get("score", 0),
                          "comments": d.get("num_comments", 0), "live": True})
            if len(items) >= limit:
                break
        return items

    @classmethod
    def get_reddit_topics(cls, cat: str = "history", period: str = "week", limit: int = 10, live: bool = True,
                          fetch: Optional[Callable[[str], str]] = None) -> Dict[str, Any]:
        seed = load_seed()
        subs = seed["reddit_subs"].get(cat) or ["todayilearned"]
        if not live:
            return {"items": cls.seed_items(["토픽"], cat), "live": False, "note": "오프라인 모드 -> 샘플 토픽"}
        items: List[Dict[str, Any]] = []
        notes = []
        for sub in subs:
            try:
                raw = (fetch or _get)(f"https://www.reddit.com/r/{sub}/top.json?t={period}&limit=25")
                items += cls.parse_reddit(json.loads(raw), sub, cat, limit)
            except urllib.error.HTTPError as e:
                notes.append(f"r/{sub}: HTTP {e.code}")
            except (OSError, ValueError) as e:
                notes.append(f"r/{sub}: {e}")
        if items:
            items.sort(key=lambda x: x.get("score", 0), reverse=True)
            seen, uniq = set(), []
            for it in items:  # 서브레딧 간 크로스포스트 중복 제거
                key = it["title"].lower()
                if key not in seen:
                    seen.add(key)
                    uniq.append(it)
            items = uniq
            return {"items": items[:limit], "live": True, "note": "레딧 공개 JSON 수집 성공 (영문 원문, 번역/재구성 필요)"}
        return {"items": cls.seed_items(["토픽"], cat), "live": False, "note": "레딧 수집 실패(" + "; ".join(notes) + ") -> 샘플 토픽으로 대체"}

    # ------------------------------------------------------------------ youtube
    @classmethod
    def get_youtube_outliers(cls, query: str, days: int = 30, min_ratio: float = 10.0, api_key: Optional[str] = None,
                             region: Optional[str] = None, fetch: Optional[Callable[[str], Dict[str, Any]]] = None) -> Dict[str, Any]:
        key = api_key or os.environ.get("YOUTUBE_API_KEY", "")
        if not key:
            return {"items": [], "live": False, "note": "YouTube API 키가 없습니다 (YOUTUBE_API_KEY). console.cloud.google.com 에서 Data API v3 키를 무료 발급"}
        try:
            res = source_tools.search_outliers(key, query, days, min_ratio, region=region, fetch=fetch)
        except source_tools.SourceError as e:
            return {"items": [], "live": False, "note": str(e)}
        items = [{"platform": "YouTube", "title": r["title"], "keyword": query, "cat": "", "url": r["url"], "live": True,
                  "score": r["ratio"], "views": r["views"], "subscribers": r["subscribers"], "channel": r["channel"], "grade": r["grade"]} for r in res]
        return {"items": items, "live": True, "note": f"V/S {min_ratio:g}배 이상 {len(items)}건"}

    # ------------------------------------------------------------------ aggregate
    @classmethod
    def get_all_trends(cls, sources: Optional[List[str]] = None, live: bool = True, cat: str = "history") -> Dict[str, Any]:
        sources = sources or ["coupang", "tiktok", "reddit"]
        items: List[Dict[str, Any]] = []
        status: Dict[str, Any] = {}
        for s in sources:
            if s == "coupang":
                r = cls.get_coupang_best(live)
            elif s == "tiktok":
                r = cls.get_tiktok_trends(live)
            elif s == "reddit":
                r = cls.get_reddit_topics(cat, live=live)
            else:
                continue
            items += r["items"]
            status[s] = {"live": r["live"], "note": r["note"], "count": len(r["items"])}
        return {"items": items, "status": status, "manual_links": load_seed()["manual_links"]}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="트렌드 수집")
    ap.add_argument("--sources", default="coupang,tiktok,reddit")
    ap.add_argument("--offline", action="store_true", help="네트워크 없이 샘플만")
    ap.add_argument("--cat", default="history", help="레딧 수집 카테고리")
    a = ap.parse_args()
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    res = TrendCrawler.get_all_trends([x for x in a.sources.split(",") if x], live=not a.offline, cat=a.cat)
    for k, v in res["status"].items():
        print(f"[{k}] live={v['live']} count={v['count']} - {v['note']}")
    for it in res["items"]:
        print(f"  [{'LIVE' if it.get('live') else '샘플'}] [{it['platform']}] {it['title']}")
