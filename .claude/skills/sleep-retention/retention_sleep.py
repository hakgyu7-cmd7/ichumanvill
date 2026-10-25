#!/usr/bin/env python3
"""retention_sleep.py - 수면용 영상의 시청 지속(Audience retention) 데이터 읽기.

    python retention_sleep.py retention.csv --duration 3:02:15
    python retention_sleep.py retention.csv --duration 10935 --transcript transcript.srt
    python retention_sleep.py retention.csv --duration 3:02:15 --json

retention.csv: YouTube Studio → 콘텐츠 → 영상 → 분석 → 참여도 → '시청자 유지율' 그래프의
다운로드 버튼으로 받은 파일. 열 두 개(영상 위치, 시청 중인 비율)만 있으면 된다.
--transcript: SRT/VTT 자막 파일 또는 shorts.py가 만든 transcript.json. 이탈 지점에서 무슨 말을 했는지 보여준다.

수면 영상은 일반 영상과 읽는 법이 다르다.
  - 초반(첫 1~3분)에 빠지는 사람 = '오늘 이 영상으로 잘지' 고르다 떠난 사람 → 제목·썸네일·첫인사·목소리 문제
  - 그 뒤 완만하게 줄어드는 것 = 잠든 뒤 기기 타이머·화면 꺼짐 등 → 정상, 오히려 길게 버틸수록 좋음
  - 초반 이후의 급격한 절벽 = 깰 만한 무언가(큰 소리, 광고, 갑작스러운 장면) → 해당 지점을 확인
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys

CHECKPOINTS = [30, 60, 180, 600, 1800, 3600, 7200]


def parse_duration(s: str) -> float:
    if ":" not in s:
        return float(s)
    parts = [float(p) for p in s.split(":")]
    sec = 0.0
    for p in parts:
        sec = sec * 60 + p
    return sec


def load_csv(path: str) -> list[tuple[float, float]]:
    rows = []
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as fh:
        for r in csv.reader(fh):
            nums = []
            for c in r:
                c = c.strip().replace("%", "").replace(",", "")
                if re.fullmatch(r"\d+:\d+(:\d+)?", c):
                    nums.append(parse_duration(c))
                    continue
                try:
                    nums.append(float(c))
                except ValueError:
                    pass
            if len(nums) >= 2:
                rows.append((nums[0], nums[1]))
    return rows


def load_transcript(path: str) -> list[tuple[float, float, str]]:
    raw = open(path, encoding="utf-8-sig", errors="replace").read()
    if path.endswith(".json"):
        data = json.loads(raw)
        segs = data.get("segments", data) if isinstance(data, dict) else data
        return [(float(s["start"]), float(s["end"]), s["text"].strip()) for s in segs]
    cues, cur = [], None
    for line in raw.splitlines():
        m = re.match(r"\s*(\d[\d:.,]+)\s*-->\s*(\d[\d:.,]+)", line)
        if m:
            cur = [parse_duration(m.group(1).replace(",", ".")), parse_duration(m.group(2).replace(",", ".")), []]
            cues.append(cur)
        elif cur is not None and line.strip() and not line.strip().isdigit():
            cur[2].append(line.strip())
    return [(a, b, " ".join(t)) for a, b, t in cues]


def fmt(sec: float) -> str:
    sec = int(round(sec))
    h, m, s = sec // 3600, sec % 3600 // 60, sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def main() -> None:
    a = sys.argv[1:]
    as_json = "--json" in a
    a = [x for x in a if x != "--json"]
    dur = parse_duration(a[a.index("--duration") + 1]) if "--duration" in a else None
    tr = a[a.index("--transcript") + 1] if "--transcript" in a else None
    files = [x for x in a if not x.startswith("--") and x not in (tr, a[a.index("--duration") + 1] if dur else None)]
    if not files or not os.path.exists(files[0]):
        print(__doc__)
        sys.exit(1)

    rows = sorted(load_csv(files[0]))
    if len(rows) < 8:
        sys.exit("CSV에서 데이터를 8개 이상 읽지 못했습니다. Studio에서 받은 원본 파일인지 확인하세요.")
    pct_axis = rows[-1][0] <= 100.5
    if pct_axis and not dur:
        sys.exit("이 파일은 위치가 %로 되어 있어 영상 길이가 필요합니다. --duration 3:02:15 처럼 넣어주세요.")
    pts = [((x / 100 * dur) if pct_axis else x, y) for x, y in rows]
    total = dur or pts[-1][0]
    start = pts[0][1] or 100.0

    def at(sec: float) -> float | None:
        if sec > total:
            return None
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x0 <= sec <= x1:
                return y0 + (y1 - y0) * ((sec - x0) / (x1 - x0) if x1 > x0 else 0)
        return pts[-1][1]

    def when_below(level: float) -> float | None:
        for x, y in pts:
            if y < level:
                return x
        return None

    checkpoints = {fmt(c): round(v, 1) for c in CHECKPOINTS if (v := at(c)) is not None}
    early_end = min(180.0, total * 0.1)
    early_loss = start - (at(early_end) or start)

    # 절벽 = 앞뒤 구간의 자연스러운 감소보다 유독 크게 떨어진 구간 (초반의 완만한 감소 곡선은 제외)
    steps = [(x0, y0 - y1, x1) for (x0, y0), (x1, y1) in zip(pts, pts[1:])]
    cand = []
    for i, (x0, d, x1) in enumerate(steps):
        if x0 < early_end or d <= 1.0:
            continue
        around = [s for j, (_, s, _) in enumerate(steps[max(0, i - 3):i + 4], start=max(0, i - 3)) if j != i]
        local = sorted(around)[len(around) // 2] if around else 0
        if d > max(local, 0) * 3:
            cand.append((d, x0, x1))
    cand.sort(reverse=True)
    cliffs = [{"at": f"{fmt(x0)}~{fmt(x1)}", "at_seconds": round(x0, 1), "until": round(x1, 1), "lost": round(d, 2)}
              for d, x0, x1 in cand[:5]]

    cues = load_transcript(tr) if tr and os.path.exists(tr) else []
    for c in cliffs:
        near = [t for s, e, t in cues if s <= c["until"] + 5 and e >= c["at_seconds"] - 20]
        if near:
            c["said"] = " / ".join(near)[:160]

    half = when_below(start / 2)
    report = {
        "duration": fmt(total),
        "start": round(start, 1),
        "checkpoints": checkpoints,
        "early_window": fmt(early_end),
        "early_loss": round(early_loss, 1),
        "half_point": fmt(half) if half is not None else "끝까지 50% 이상 유지",
        "end": round(pts[-1][1], 1),
        "cliffs": cliffs,
    }
    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
        return

    print(f"\n  영상 길이 {report['duration']}")
    print("  시점별 남은 비율: " + "  ".join(f"{k} {v}%" for k, v in checkpoints.items()))
    print(f"\n  [초반 이탈] 처음 {report['early_window']} 동안 {report['early_loss']}%p 빠짐", end="  ")
    print("→ 높음: 제목·썸네일과 첫인사가 기대와 다르거나, 목소리·배경음이 맞지 않음" if early_loss > 35
          else "→ 보통" if early_loss > 20 else "→ 좋음: 들어온 사람 대부분이 이 영상으로 잠들기로 함")
    print(f"  [절반 지점] {report['half_point']}  (수면 영상은 이 시점이 늦을수록 좋음)")
    print(f"  [마지막] 끝까지 {report['end']}% 재생")
    if cliffs:
        print("\n  [초반 이후 급격한 이탈] — 잠을 깨울 만한 요소(큰 소리, 광고, 갑작스러운 장면)가 있었는지 확인")
        for c in cliffs:
            print(f"    {c['at']}  -{c['lost']}%p" + (f"   «{c['said']}»" if c.get("said") else ""))
    else:
        print("\n  초반 이후 급격한 이탈 없음 — 잠든 시청자를 깨우는 구간이 없다는 뜻이라 좋음")


if __name__ == "__main__":
    main()
