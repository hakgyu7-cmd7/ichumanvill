#!/usr/bin/env python3
"""outliers.py - 경쟁 채널에서 '평소보다 몇 배 터진 영상'을 찾고, 터진 제목들의 공통 단어를 뽑는다.

1) 수집 (yt-dlp 필요, 내 PC에서 실행):
    python outliers.py collect "https://www.youtube.com/@채널1" "https://www.youtube.com/@채널2" -o data.json
    python outliers.py collect channels.txt -o data.json        # 한 줄에 채널 주소 하나
2) 분석:
    python outliers.py rank data.json                 # 2배 이상 터진 영상
    python outliers.py rank data.json --min 3 --json

조회수 자체는 채널 크기를 잴 뿐이다. 그래서 영상마다 '그 채널 최근 영상 조회수 중앙값의 몇 배인지'로 순위를 매긴다.
채널당 영상이 6개 미만이면 중앙값이 의미 없어 건너뛴다. 공개된 목록만 읽고 로그인하지 않는다.
"""
from __future__ import annotations

import json
import os
import re
import statistics
import sys

MIN_VIDEOS = 6

# 수면용 옛날이야기 제목에서 자주 보이는 요소. 터진 영상에 얼마나 더 자주 나오는지(배율)를 본다.
FEATURES = {
    "용도(잠/수면)": r"잠|수면|잠들|잘\s*때|불면",
    "길이 명시(○시간)": r"\d+\s*시간",
    "몰아듣기/모음": r"몰아|모음|연속|정주행",
    "광고 없음": r"광고\s*없",
    "민담/야담/전래": r"민담|야담|전래|설화|전설",
    "옛날이야기": r"옛날\s*이야기|옛이야기",
    "어르신 대상": r"어르신|노인|부모님",
    "가족 갈등(시어머니·며느리 등)": r"시어머니|며느리|시아버지|계모|의붓|형제|효자|효녀|불효",
    "약자·반전(과부·머슴·거지 등)": r"과부|머슴|거지|노비|종|가난|나무꾼",
    "부자·양반·벼슬": r"부자|양반|정승|원님|사또|임금|벼슬|대감",
    "신비(도깨비·여우·신선)": r"도깨비|여우|구미호|신선|산신|용|호랑이|귀신",
    "보은·복": r"은혜|보답|복|횡재|금덩이|보물",
    "숫자(년·살·명)": r"\d+\s*(년|살|명|번)",
    "질문형(?)": r"\?",
}


def read_targets(args: list[str]) -> list[str]:
    targets = []
    for a in args:
        if os.path.exists(a):
            with open(a, encoding="utf-8-sig") as fh:
                targets += [l.strip() for l in fh if l.strip() and not l.startswith("#")]
        else:
            targets.append(a)
    return targets


def collect(targets: list[str], out: str, limit: int) -> None:
    try:
        import yt_dlp
    except ImportError:
        sys.exit("yt-dlp가 필요합니다: pip install yt-dlp")
    rows = []
    opts = {"extract_flat": True, "quiet": True, "no_warnings": True, "playlistend": limit}
    with yt_dlp.YoutubeDL(opts) as ydl:
        for url in targets:
            url = url.rstrip("/")
            if "/@" in url and not url.endswith(("/videos", "/streams", "/shorts")):
                url += "/videos"  # 롱폼 목록만 (숏폼은 조회수 성격이 달라 섞지 않음)
            print(f"  수집 중: {url}")
            try:
                info = ydl.extract_info(url, download=False)
            except Exception as e:
                print(f"    ✗ 실패: {e}")
                continue
            channel = info.get("channel") or info.get("uploader") or info.get("title") or url
            n = 0
            for e in info.get("entries") or []:
                if not e or e.get("view_count") is None:
                    continue
                rows.append({"channel": channel, "title": e.get("title", ""), "views": e["view_count"],
                             "duration": e.get("duration"),
                             "url": e.get("url") or f"https://www.youtube.com/watch?v={e.get('id')}"})
                n += 1
            print(f"    ✓ {channel}: 영상 {n}개")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=1)
    print(f"\n  저장: {out} (영상 {len(rows)}개)\n  다음: python outliers.py rank {out}")


def rank(path: str, lo: float, as_json: bool) -> None:
    rows = json.load(open(path, encoding="utf-8-sig"))
    by: dict[str, list[dict]] = {}
    for r in rows:
        by.setdefault(r.get("channel", "?"), []).append(r)

    scored, thin = [], []
    for ch, vids in by.items():
        if len(vids) < MIN_VIDEOS:
            thin.append((ch, len(vids)))
            continue
        med = statistics.median(float(v.get("views") or 0) for v in vids) or 1
        for v in vids:
            scored.append({**v, "channel": ch, "median": int(med),
                           "multiple": round(float(v.get("views") or 0) / med, 2)})

    out = sorted((r for r in scored if r["multiple"] >= lo), key=lambda r: -r["multiple"])

    # 터진 영상 제목에 각 요소가 나오는 비율 vs 전체 영상에서 나오는 비율
    def share(items: list[dict], pat: str) -> float:
        return sum(1 for r in items if re.search(pat, r.get("title", ""))) / len(items) if items else 0
    features = []
    for name, pat in FEATURES.items():
        s_out, s_all = share(out, pat), share(scored, pat)
        if s_out > 0:
            features.append({"feature": name, "outliers": round(s_out * 100), "all": round(s_all * 100),
                             "lift": round(s_out / s_all, 2) if s_all else None})
    features.sort(key=lambda f: -(f["lift"] or 99))

    lengths = [r["duration"] / 3600 for r in out if r.get("duration")]
    result = {"outliers": out, "features": features, "skipped_channels": thin,
              "outlier_median_hours": round(statistics.median(lengths), 1) if lengths else None}
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return

    print(f"\n  채널 {len(by)}개, 영상 {len(rows)}개 중 평소의 {lo}배 이상 터진 영상 {len(out)}개")
    if thin:
        print("  건너뜀(영상 수 부족): " + ", ".join(f"{c}({n}개)" for c, n in thin))
    print()
    for r in out[:20]:
        hours = f"{r['duration'] / 3600:.1f}시간" if r.get("duration") else ""
        print(f"  {r['multiple']:5.1f}배  {r['views']:>10,}회 (평소 {r['median']:,})  {hours:>6}  [{r['channel'][:14]}] {r['title'][:60]}")
    if result["outlier_median_hours"]:
        print(f"\n  터진 영상의 길이 중앙값: {result['outlier_median_hours']}시간")
    print("\n  터진 제목에 자주 나온 요소 (배율 = 터진 영상 비율 ÷ 전체 비율, 1보다 클수록 터진 쪽에 몰림)")
    for f in features:
        lift = f"{f['lift']}배" if f["lift"] else "새 요소"
        print(f"    {f['feature']:<24} 터진 영상 {f['outliers']:>3}%  전체 {f['all']:>3}%  → {lift}")
    print("\n  ※ 제목 단어 분석은 '무엇이 같이 나왔나'일 뿐, 그 단어 때문에 터졌다는 증명은 아닙니다.")


def main() -> None:
    a = sys.argv[1:]
    if not a or a[0] not in ("collect", "rank"):
        print(__doc__)
        sys.exit(1)
    cmd, a = a[0], a[1:]
    as_json = "--json" in a
    a = [x for x in a if x != "--json"]
    if cmd == "collect":
        out = a[a.index("-o") + 1] if "-o" in a else "data.json"
        limit = int(a[a.index("--limit") + 1]) if "--limit" in a else 60
        targets = read_targets([x for x in a if x not in ("-o", out, "--limit", str(limit))])
        if not targets:
            sys.exit("채널 주소를 넣어주세요.")
        collect(targets, out, limit)
    else:
        lo = float(a[a.index("--min") + 1]) if "--min" in a else 2.0
        files = [x for x in a if not x.startswith("--") and x != str(lo) and os.path.exists(x)]
        if not files:
            sys.exit("data.json 파일을 지정하세요.")
        rank(files[0], lo, as_json)


if __name__ == "__main__":
    main()
