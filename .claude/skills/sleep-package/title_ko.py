#!/usr/bin/env python3
"""title_ko.py - 수면용 옛날이야기 채널의 제목·썸네일 문구 검사기 (한국어 전용).

    python title_ko.py --title "제목" --thumb "썸네일 문구"
    python title_ko.py titles.txt                 # 한 줄에 제목 하나, 점수순 정렬
    python title_ko.py titles.txt --json

한글은 영문보다 화면에서 약 2배 넓게 차지하므로 '표시 폭'(한글 2, 영문·숫자·공백 1)으로 잰다.
점수는 판단을 돕는 참고값이다. 최종 선택은 사람이 한다.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata

# 휴대폰 홈 피드에서 앞부분만 보이는 지점, 데스크톱 검색 결과에서 잘리는 지점 (표시 폭 기준, 대략값)
FRONT_WIDTH = 40
CUT_WIDTH = 70

USE = r"잠|수면|잠들|잠이\s*솔솔|잠\s*안\s*올|자기\s*전|잘\s*때|불면"
GENRE = r"옛날\s*이야기|옛이야기|민담|야담|전래\s*동화|설화|전설|고전"
LENGTH = r"\d+\s*시간|\d+\s*분|몰아\s*듣기|연속|모음|정주행"
ADS = r"중간\s*광고\s*없|광고\s*없"
LOUD = r"[!?]{2,}|충격|경악|소름|발칵|미쳤|ㄷㄷ|대박"  # 수면 채널에 맞지 않는 자극 표현
EMOJI = re.compile(r"[\U0001F300-\U0001FAFF☀-➿]")


def width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def cut(text: str, limit: int) -> str:
    out, w = "", 0
    for ch in text:
        w += 2 if unicodedata.east_asian_width(ch) in "WF" else 1
        if w > limit:
            return out + "…"
        out += ch
    return out


def check(title: str, thumb: str | None = None) -> dict:
    notes: list[tuple[str, str]] = []
    score = 100
    w = width(title)
    front = cut(title, FRONT_WIDTH)

    if w > CUT_WIDTH:
        score -= 15
        notes.append(("주의", f"표시 폭 {w} — 검색 결과에서 '{cut(title, CUT_WIDTH)}'까지만 보임"))
    else:
        notes.append(("통과", f"표시 폭 {w} (검색 결과에서 잘리지 않음)"))

    for name, pat, pts, why in [
        ("용도", USE, 20, "'잠잘 때', '잠 안 올 때' 같은 용도 단어가 없음 — 수면 채널 시청자가 찾는 첫 단어"),
        ("장르", GENRE, 15, "'옛날이야기·민담·야담' 같은 장르 단어가 없음"),
        ("길이", LENGTH, 10, "'3시간', '몰아듣기' 같은 길이 정보가 없음 — 밤새 틀어둘 사람에게 중요"),
    ]:
        m = re.search(pat, title)
        if not m:
            score -= pts
            notes.append(("부족", why))
        elif not re.search(pat, front):
            score -= pts // 2
            notes.append(("주의", f"{name} 단어('{m.group(0)}')가 앞부분({FRONT_WIDTH}폭) 밖에 있음 — 휴대폰 홈에서 안 보일 수 있음"))
        else:
            notes.append(("통과", f"{name}: '{m.group(0)}'"))

    if re.search(ADS, title):
        notes.append(("확인", "'광고 없음'을 썼다면 실제로 중간광고를 껐는지 꼭 확인 (거짓이면 신뢰를 잃음)"))
    loud = re.findall(LOUD, title)
    if loud:
        score -= 10
        notes.append(("주의", f"자극적인 표현 {loud} — 잠들려는 시청자에게는 역효과일 수 있음"))
    if len(EMOJI.findall(title)) > 2:
        score -= 5
        notes.append(("주의", "이모지가 3개 이상 — 1~2개면 충분"))

    if thumb:
        tw = len(thumb.split())
        if tw > 4:
            score -= 10
            notes.append(("주의", f"썸네일 문구 {tw}단어 — TV·휴대폰 작은 화면에서는 2~4단어가 한계"))
        shared = set(re.findall(r"[가-힣]{2,}", thumb)) & set(re.findall(r"[가-힣]{2,}", title))
        if shared:
            score -= 5
            notes.append(("주의", f"썸네일과 제목이 같은 말 {sorted(shared)}을 반복 — 다른 단어로 같은 약속을"))
        else:
            notes.append(("통과", "썸네일과 제목이 서로 다른 단어"))

    return {"title": title, "thumb": thumb, "width": w, "front": front, "score": max(score, 0), "notes": notes}


def show(r: dict) -> None:
    print(f"\n  {r['title']}")
    print(f"  점수 {r['score']}/100   표시 폭 {r['width']}   휴대폰 앞부분: {r['front']}")
    for tag, msg in r["notes"]:
        print(f"    [{tag}] {msg}")


def main() -> None:
    a = sys.argv[1:]
    as_json = "--json" in a
    a = [x for x in a if x != "--json"]
    thumb = a[a.index("--thumb") + 1] if "--thumb" in a else None
    if "--title" in a:
        rows = [check(a[a.index("--title") + 1], thumb)]
    elif a and not a[0].startswith("--"):
        with open(a[0], encoding="utf-8-sig") as fh:
            rows = [check(line.strip(), thumb) for line in fh if line.strip()]
        rows.sort(key=lambda r: -r["score"])
    else:
        print(__doc__)
        sys.exit(1)
    if as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
    else:
        for r in rows:
            show(r)


if __name__ == "__main__":
    main()
