#!/usr/bin/env python3
"""시니어 롱폼 「잘 된 영상」 찾기.

리드어세상 6화 분석 기준표(01_분석기준표.md)를 그대로 코드로 옮겼다.
채널마다 평소 조회수(중앙값)를 구하고, 영상마다 성과 배수를 계산해
잘 됨 / 평범 / 보류 / 제외로 판정한 뒤, 구간별 표본 15편을 골라 준다.

자료 받는 방법 두 가지:
  1) YouTube Data API (API 키 필요, 무료 할당량 안에서 충분)
       python3 find_hits.py --api-key KEY --channels 채널목록.txt
       python3 find_hits.py --api-key KEY --search "야담,사연,시니어 사연"
  2) 직접 모은 CSV (API 키 없이)
       python3 find_hits.py --from-csv 내가_모은_영상.csv

API 키는 환경 변수 YOUTUBE_API_KEY로 줘도 된다.
표준 라이브러리만 쓴다. 파이썬 3.9 이상.
"""
import argparse
import csv
import json
import os
import re
import statistics
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

API = "https://www.googleapis.com/youtube/v3/"

# 분석 기준표 2장: 채널 크기 구간. 1만~3만, 7만~8만은 일부러 비워 둔다.
TIERS = [
    ("소형", 1_000, 10_000, 10_000),
    ("중형", 30_000, 70_000, 50_000),
    ("대형", 80_000, 150_000, 100_000),
]
LONGFORM_SECONDS = 8 * 60       # 1장: 롱폼은 8분 이상
WINDOW_DAYS = 92                # 3장: 수집일 직전 3개월
MIN_AGE_DAYS = 14               # 3장: 업로드 후 14일 지난 영상만 판정
HIT_RATIO = 5.0                 # 4장: 평소의 5배 이상
NORMAL_RANGE = (0.5, 1.5)       # 4장: 평범한 영상
AD_LIKE_FACTOR = 1 / 3          # 4장: 좋아요율이 채널 중앙값의 1/3 미만이면 광고 유입 의심
MIN_VIDEOS_PER_CHANNEL = 6      # 5장: 판정 대상 6편 이상인 채널만
CHANNELS_PER_TIER = 3           # 5장: 구간당 채널 3개
PAIRS_PER_TIER = 2              # 5장: 평범한 영상 2편


# ---------------------------------------------------------------- 자료 모으기

class YouTube:
    def __init__(self, key):
        self.key = key
        self.units = 0  # 쓴 할당량 (하루 무료 10,000)

    def get(self, path, cost=1, **params):
        params["key"] = self.key
        url = API + path + "?" + urllib.parse.urlencode(params)
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                self.units += cost
                return json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            try:
                msg = json.loads(body)["error"]["message"]
            except (ValueError, KeyError):
                msg = body[:300]
            sys.exit(f"YouTube API 오류 {e.code}: {msg}")

    def search_channels(self, query, pages=1):
        ids, token = [], None
        for _ in range(pages):
            params = dict(part="snippet", q=query, type="channel", regionCode="KR",
                          relevanceLanguage="ko", maxResults=50)
            if token:
                params["pageToken"] = token
            res = self.get("search", cost=100, **params)
            ids += [it["snippet"]["channelId"] for it in res.get("items", [])]
            token = res.get("nextPageToken")
            if not token:
                break
        return ids

    def channel(self, ref):
        """채널 ID(UC...), @핸들, 채널 주소 무엇이든 받는다."""
        ref = ref.strip()
        m = re.search(r"(UC[\w-]{22})", ref)
        if m:
            params = {"id": m.group(1)}
        else:
            m = re.search(r"@([^/?\s]+)", ref)
            handle = m.group(1) if m else ref.lstrip("@")
            params = {"forHandle": "@" + urllib.parse.unquote(handle)}
        res = self.get("channels", part="snippet,statistics,contentDetails", **params)
        items = res.get("items") or []
        return items[0] if items else None

    def recent_uploads(self, uploads_playlist, since):
        """since 이후 올라온 영상 ID. 업로드 목록은 최신순이라 since보다 오래되면 멈춘다."""
        ids, token = [], None
        while True:
            params = dict(part="contentDetails", playlistId=uploads_playlist, maxResults=50)
            if token:
                params["pageToken"] = token
            res = self.get("playlistItems", **params)
            stop = False
            for it in res.get("items", []):
                published = parse_time(it["contentDetails"].get("videoPublishedAt"))
                if published and published.date() < since:
                    stop = True
                    break
                ids.append(it["contentDetails"]["videoId"])
            token = res.get("nextPageToken")
            if stop or not token:
                return ids

    def videos(self, ids):
        out = []
        for i in range(0, len(ids), 50):
            res = self.get("videos", part="snippet,contentDetails,statistics,liveStreamingDetails",
                           id=",".join(ids[i:i + 50]))
            out += res.get("items", [])
        return out


def parse_time(s):
    if not s:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def parse_duration(s):
    """ISO 8601 길이(PT1H2M3S)를 초로."""
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    if not m:
        return 0
    d, h, mi, se = (int(x or 0) for x in m.groups())
    return ((d * 24 + h) * 60 + mi) * 60 + se


def collect_from_api(yt, channel_refs, today):
    since = today - timedelta(days=WINDOW_DAYS)
    channels, videos = [], []
    for ref in channel_refs:
        ch = yt.channel(ref)
        if not ch:
            print(f"  찾지 못함: {ref}", file=sys.stderr)
            continue
        stats = ch["statistics"]
        if stats.get("hiddenSubscriberCount"):
            print(f"  구독자 수 비공개라 뺌: {ch['snippet']['title']}", file=sys.stderr)
            continue
        info = {
            "channel_id": ch["id"],
            "channel": ch["snippet"]["title"],
            "channel_url": f"https://www.youtube.com/channel/{ch['id']}",
            "subscribers": int(stats.get("subscriberCount", 0)),
        }
        if tier_of(info["subscribers"]) is None:
            print(f"  구간 밖이라 뺌: {info['channel']} (구독자 {info['subscribers']:,})", file=sys.stderr)
            continue
        channels.append(info)
        ids = yt.recent_uploads(ch["contentDetails"]["relatedPlaylists"]["uploads"], since)
        for v in yt.videos(ids):
            sn, st = v["snippet"], v.get("statistics", {})
            videos.append({
                **info,
                "video_id": v["id"],
                "url": f"https://youtu.be/{v['id']}",
                "title": sn["title"],
                "published": parse_time(sn["publishedAt"]).date().isoformat(),
                "seconds": parse_duration(v["contentDetails"].get("duration")),
                "views": int(st.get("viewCount", 0)),
                "likes": int(st["likeCount"]) if "likeCount" in st else None,
                "comments": int(st["commentCount"]) if "commentCount" in st else None,
                "is_live": "liveStreamingDetails" in v or sn.get("liveBroadcastContent") != "none",
            })
        print(f"  {info['channel']}: 구독자 {info['subscribers']:,}, 최근 영상 {len(ids)}편", file=sys.stderr)
    return videos


def collect_from_csv(path):
    """직접 모은 표. 열 이름은 README의 CSV 양식을 따른다."""
    need = ["channel", "subscribers", "title", "published", "seconds", "views"]
    out = []
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if rows:
        missing = [c for c in need if c not in rows[0]]
        if missing:
            sys.exit(f"CSV에 없는 열: {', '.join(missing)}")
    for i, r in enumerate(rows, 2):
        try:
            out.append({
                "channel_id": r.get("channel_id") or r["channel"],
                "channel": r["channel"],
                "channel_url": r.get("channel_url", ""),
                "subscribers": to_int(r["subscribers"]),
                "video_id": r.get("video_id") or r.get("url") or f"row{i}",
                "url": r.get("url", ""),
                "title": r["title"],
                "published": r["published"].strip()[:10],
                "seconds": to_seconds(r["seconds"]),
                "views": to_int(r["views"]),
                "likes": to_int(r["likes"]) if r.get("likes", "").strip() else None,
                "comments": to_int(r["comments"]) if r.get("comments", "").strip() else None,
                "is_live": r.get("is_live", "").strip().lower() in ("1", "true", "y", "yes", "예"),
            })
        except (ValueError, KeyError) as e:
            sys.exit(f"CSV {i}번째 줄을 읽지 못함: {e}")
    return out


def to_int(s):
    s = str(s).replace(",", "").strip()
    m = re.fullmatch(r"([\d.]+)\s*(만|천)?", s)
    if not m:
        raise ValueError(f"숫자가 아님: {s!r}")
    n = float(m.group(1)) * {"만": 10_000, "천": 1_000, None: 1}[m.group(2)]
    return int(round(n))


def to_seconds(s):
    """'734', '12:14', '1:02:03' 모두 받는다."""
    parts = [int(p) for p in str(s).strip().split(":")]
    sec = 0
    for p in parts:
        sec = sec * 60 + p
    return sec


# ---------------------------------------------------------------- 판정

def tier_of(subscribers):
    for name, lo, hi, min_views in TIERS:
        if lo <= subscribers <= hi:
            return name, min_views
    return None


def judge(videos, today):
    """기준표 3~4장. 영상마다 status, ratio, like_rate를 채운다."""
    oldest = today - timedelta(days=WINDOW_DAYS)
    newest = today - timedelta(days=MIN_AGE_DAYS)
    by_channel = {}
    for v in videos:
        v["age_days"] = (today - date.fromisoformat(v["published"])).days
        v["ratio"] = v["like_rate"] = None
        tier = tier_of(v["subscribers"])
        v["tier"] = tier[0] if tier else "구간 밖"
        if tier is None:
            v["status"] = "제외: 구간 밖"
        elif v["seconds"] < LONGFORM_SECONDS:
            v["status"] = "제외: 8분 미만"
        elif v["is_live"]:
            v["status"] = "제외: 라이브"
        elif not oldest <= date.fromisoformat(v["published"]) <= newest:
            v["status"] = "제외: 기간 밖" if v["age_days"] > WINDOW_DAYS else "제외: 14일 안 됨"
        else:
            v["status"] = "판정 대상"
            by_channel.setdefault(v["channel_id"], []).append(v)

    channels = {}
    for cid, vs in by_channel.items():
        baseline = statistics.median(v["views"] for v in vs)
        rates = [v["likes"] / v["views"] for v in vs if v["likes"] is not None and v["views"]]
        like_median = statistics.median(rates) if rates else None
        eligible = len(vs) >= MIN_VIDEOS_PER_CHANNEL and baseline > 0
        channels[cid] = {"channel": vs[0]["channel"], "tier": vs[0]["tier"],
                         "subscribers": vs[0]["subscribers"], "channel_url": vs[0]["channel_url"],
                         "baseline": baseline, "like_median": like_median,
                         "videos": len(vs), "eligible": eligible}
        min_views = tier_of(vs[0]["subscribers"])[1]
        for v in vs:
            v["baseline"] = baseline
            if not eligible:
                v["status"] = f"제외: 채널 영상 {len(vs)}편뿐"
                continue
            v["ratio"] = v["views"] / baseline
            if v["likes"] is not None and v["views"]:
                v["like_rate"] = v["likes"] / v["views"]
            if like_median and v["like_rate"] is not None and v["like_rate"] < like_median * AD_LIKE_FACTOR:
                v["status"] = "제외: 광고 유입 의심"
            elif v["ratio"] >= HIT_RATIO and v["views"] >= min_views:
                v["status"] = "잘 됨"
            elif NORMAL_RANGE[0] <= v["ratio"] <= NORMAL_RANGE[1]:
                v["status"] = "평범"
            else:
                v["status"] = "보류"
    return channels


def pick_sample(videos, channels):
    """기준표 5장. 구간마다 채널 3개에서 잘 된 영상 1편씩, 그중 배수 높은 2편에 평범한 영상 짝."""
    sample, notes = [], []
    for tier, _, _, _ in TIERS:
        best = {}
        for v in videos:
            if v["tier"] == tier and v["status"] == "잘 됨":
                cur = best.get(v["channel_id"])
                if cur is None or v["ratio"] > cur["ratio"]:
                    best[v["channel_id"]] = v
        hits = sorted(best.values(), key=lambda v: v["ratio"], reverse=True)[:CHANNELS_PER_TIER]
        if len(hits) < CHANNELS_PER_TIER:
            notes.append(f"{tier}: 잘 된 영상이 있는 채널이 {len(hits)}개뿐입니다. "
                         f"기준을 낮추지 말고 후보 채널을 늘리세요(구간당 10개에서 20개로).")
        for v in hits:
            sample.append({**v, "role": "잘 됨"})
        paired = 0
        for h in hits:
            if paired == PAIRS_PER_TIER:
                break
            day = date.fromisoformat(h["published"])
            normals = [v for v in videos if v["channel_id"] == h["channel_id"] and v["status"] == "평범"]
            if not normals:
                notes.append(f"{tier}: {h['channel']}에 짝지을 평범한 영상이 없어 다음 채널로 넘어갑니다.")
                continue
            n = min(normals, key=lambda v: abs((date.fromisoformat(v["published"]) - day).days))
            sample.append({**n, "role": f"평범 (짝: {h['title'][:20]})"})
            paired += 1
        if hits and paired < PAIRS_PER_TIER:
            notes.append(f"{tier}: 평범한 영상 짝이 {paired}편뿐입니다.")
    return sample, notes


# ---------------------------------------------------------------- 내보내기

VIDEO_COLUMNS = [
    ("tier", "구간"), ("channel", "채널"), ("subscribers", "구독자"), ("baseline", "채널 기준선"),
    ("title", "제목"), ("url", "영상 주소"), ("published", "업로드일"), ("age_days", "경과일"),
    ("seconds", "길이(초)"), ("views", "조회수"), ("likes", "좋아요"), ("comments", "댓글"),
    ("ratio", "성과 배수"), ("like_rate", "좋아요율"), ("status", "판정"),
]


def fmt(key, value):
    if value is None:
        return ""
    if key == "ratio":
        return f"{value:.2f}"
    if key == "like_rate":
        return f"{value * 100:.2f}%"
    if key == "baseline":
        return f"{value:.0f}"
    return value


def write_csv(path, rows, columns):
    # utf-8-sig: 엑셀에서 한글이 깨지지 않게
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow([label for _, label in columns])
        for r in rows:
            w.writerow([fmt(k, r.get(k)) for k, _ in columns])


def write_report(path, today, videos, channels, sample, notes):
    counts = {}
    for v in videos:
        counts[v["status"]] = counts.get(v["status"], 0) + 1
    lines = [
        "# 잘 된 영상 찾기 결과", "",
        f"수집일: {today}  ",
        f"판정 대상 업로드일: {today - timedelta(days=WINDOW_DAYS)} ~ {today - timedelta(days=MIN_AGE_DAYS)}  ",
        f"기준: 성과 배수 = 조회수 ÷ 채널 판정 대상 영상의 조회수 중앙값. "
        f"잘 됨은 {HIT_RATIO:.0f}배 이상이면서 최소 조회수(소형 1만, 중형 5만, 대형 10만) 이상, "
        f"평범은 {NORMAL_RANGE[0]}~{NORMAL_RANGE[1]}배.", "",
        "## 표본 (구간별 잘 됨 3편 + 평범 2편)", "",
        "| 구간 | 역할 | 채널 | 제목 | 조회수 | 배수 | 업로드일 | 주소 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for s in sample:
        title = s["title"].replace("|", "/")
        lines.append(f"| {s['tier']} | {s['role']} | {s['channel']} | {title} | {s['views']:,} | "
                     f"{s['ratio']:.2f} | {s['published']} | {s['url']} |")
    if not sample:
        lines.append("| | 표본 없음 | | | | | | |")
    lines += ["", f"표본 {len(sample)}편 (목표 15편)", ""]
    if notes:
        lines += ["## 알림", ""] + [f"- {n}" for n in notes] + [""]
    lines += ["## 채널", "", "| 구간 | 채널 | 구독자 | 판정 대상 영상 | 기준선(중앙값) | 자격 |", "|---|---|---|---|---|---|"]
    for c in sorted(channels.values(), key=lambda c: (c["tier"], -c["subscribers"])):
        lines.append(f"| {c['tier']} | {c['channel']} | {c['subscribers']:,} | {c['videos']} | "
                     f"{c['baseline']:,.0f} | {'O' if c['eligible'] else '영상 6편 미만'} |")
    lines += ["", "## 판정 집계", ""] + [f"- {k}: {n}편" for k, n in sorted(counts.items())]
    lines += ["", "## 주의", "",
              "- 표본은 15편입니다. 결과는 「법칙」이 아니라 「이 표본에서는 이렇게 보인다」로 읽습니다.",
              "- 결과를 말하거나 올릴 때 남의 채널 이름과 실제 제목은 A1, B2처럼 번호로 바꿉니다.",
              "- 남의 썸네일과 장면은 분석에만 쓰고 내 영상에 넣지 않습니다.",
              "- 멤버십 전용 영상은 API로 가려내지 못합니다. 표본에 섞였으면 직접 빼세요.", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ---------------------------------------------------------------- 실행

def main(argv=None):
    p = argparse.ArgumentParser(description="시니어 롱폼 잘 된 영상 찾기 (리드어세상 6화 분석 기준표)")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--channels", help="채널 목록 파일. 한 줄에 하나(채널 주소, @핸들, UC로 시작하는 ID)")
    src.add_argument("--search", help="쉼표로 나눈 검색어. 채널을 찾아 구간에 맞는 것만 씀 (검색 한 번에 할당량 100)")
    src.add_argument("--from-csv", help="직접 모은 영상 표 CSV (API 키 없이)")
    p.add_argument("--api-key", default=os.environ.get("YOUTUBE_API_KEY"), help="YouTube Data API 키 (또는 YOUTUBE_API_KEY)")
    p.add_argument("--date", help="수집일 YYYY-MM-DD (기본: 오늘)")
    p.add_argument("--out", default="분석결과", help="결과 폴더 (기본: 분석결과)")
    a = p.parse_args(argv)

    today = date.fromisoformat(a.date) if a.date else datetime.now(timezone(timedelta(hours=9))).date()

    if a.from_csv:
        videos = collect_from_csv(a.from_csv)
    else:
        if not a.api_key:
            p.error("--api-key 또는 환경 변수 YOUTUBE_API_KEY가 필요합니다 (API 키 없이 하려면 --from-csv)")
        yt = YouTube(a.api_key)
        if a.channels:
            with open(a.channels, encoding="utf-8-sig") as f:
                refs = [ln.strip() for ln in f if ln.strip() and not ln.lstrip().startswith("#")]
        else:
            refs = []
            for q in [q.strip() for q in a.search.split(",") if q.strip()]:
                refs += [r for r in yt.search_channels(q) if r not in refs]
            print(f"검색으로 찾은 채널 {len(refs)}개", file=sys.stderr)
        videos = collect_from_api(yt, refs, today)
        print(f"쓴 API 할당량: {yt.units} (하루 무료 10,000)", file=sys.stderr)

    channels = judge(videos, today)
    sample, notes = pick_sample(videos, channels)

    os.makedirs(a.out, exist_ok=True)
    write_csv(os.path.join(a.out, "전체영상.csv"), videos, VIDEO_COLUMNS)
    write_csv(os.path.join(a.out, "표본15편.csv"), sample, [("role", "역할")] + VIDEO_COLUMNS)
    write_report(os.path.join(a.out, "결과.md"), today, videos, channels, sample, notes)

    hits = sum(v["status"] == "잘 됨" for v in videos)
    print(f"영상 {len(videos)}편 중 잘 됨 {hits}편, 표본 {len(sample)}편 → {a.out}/결과.md")
    for n in notes:
        print("  - " + n)


if __name__ == "__main__":
    main()
