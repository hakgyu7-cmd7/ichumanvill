#!/usr/bin/env python3
"""
shorts_stitcher.py - 5단계 "합성": 6개 클립 + 음성 + 자막 -> 1080x1920 쇼츠 (FFmpeg 필요)

  1) 클립 6개를 씬 순서대로 이어 붙이기 (클립마다 규격을 먼저 통일 -> 해상도/프레임이 달라도 안전)
  2) 워터마크 크롭: 1.06배 확대 후 중앙 크롭 (구글 플로우 우측 하단 워터마크를 화면 밖으로 밀어냄)
  3) 1080x1920 레터박스: 상단 240px 검정 바(노란 타이틀) / 중앙 1280px 영상 / 하단 400px 검정 바(앱 UI 보호존)
  4) 자막: 씬 대사를 2.5초 비트 단위(씬당 3개)로 순차 표시, 하단 검정 바 바로 위(y=1500)에 아래 정렬
  5) 음성 합성 (길이가 달라도 영상 길이에 맞춰 잘리거나 무음 패딩)

사용:  python shorts_stitcher.py --project projects/my.json          (대시보드에서 내보낸/저장한 프로젝트)
       python shorts_stitcher.py --project samples/ramen_bgrade.json --dry-run   (FFmpeg 명령만 출력)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import prompt_engine as pe

BASE = Path(__file__).resolve().parent
VIDEO_EXTS = (".mp4", ".mov", ".webm", ".mkv")
AUDIO_EXTS = (".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac")
FPS = 30
LANG_WIDTH_MULT = {"en": 1.9}  # 영문은 글자 폭이 좁아 한 줄에 더 많이 들어간다


class StitchError(RuntimeError):
    pass


# --------------------------------------------------------------------------- file discovery
def find_clip(input_dir: Path, n: int) -> Optional[Path]:
    for stem in (f"scene{n}", f"scene_{n:02d}", f"scene{n:02d}", f"scene_{n}"):
        for ext in VIDEO_EXTS:
            p = Path(input_dir) / f"{stem}{ext}"
            if p.exists():
                return p
    return None


def find_voice(input_dir: Path) -> Optional[Path]:
    for stem in ("voice", "voice_final"):
        for ext in AUDIO_EXTS:
            p = Path(input_dir) / f"{stem}{ext}"
            if p.exists():
                return p
    return None


FONT_CANDIDATES = {
    "black": ["Pretendard-Black.ttf", "Pretendard-ExtraBold.ttf", "Pretendard-Bold.ttf", "Pretendard-Black.otf", "Pretendard-Bold.otf"],
    "bold": ["Pretendard-Bold.ttf", "Pretendard-SemiBold.ttf", "Pretendard-Medium.ttf", "Pretendard-Bold.otf"],
}
SYSTEM_FONTS = [
    "C:/Windows/Fonts/malgunbd.ttf", "C:/Windows/Fonts/malgun.ttf",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc", "/Library/Fonts/AppleGothic.ttf", "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
    "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf", "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def find_font(assets_dir: Path, weight: str = "bold") -> Tuple[Optional[Path], bool]:
    """(폰트 경로, Pretendard 여부). assets/ 의 Pretendard -> assets 안의 아무 폰트 -> 시스템 한글 폰트 순."""
    assets_dir = Path(assets_dir)
    for name in FONT_CANDIDATES[weight]:
        if (assets_dir / name).exists():
            return assets_dir / name, True
    if assets_dir.exists():
        for ext in ("*.ttf", "*.otf", "*.ttc"):
            for f in sorted(assets_dir.glob(ext)):
                return f, False
    for s in SYSTEM_FONTS:
        if Path(s).exists():
            return Path(s), False
    return None, False


FONT_EXTS = (".ttf", ".otf", ".ttc")


def system_font_dirs() -> List[Path]:
    dirs: List[Path] = []
    win = os.environ.get("WINDIR") or os.environ.get("SystemRoot")
    if win:
        dirs.append(Path(win) / "Fonts")
    dirs += [Path("C:/Windows/Fonts"), Path.home() / "AppData/Local/Microsoft/Windows/Fonts", Path("/System/Library/Fonts"),
             Path("/Library/Fonts"), Path.home() / "Library/Fonts", Path("/usr/share/fonts"), Path("/usr/local/share/fonts"),
             Path.home() / ".fonts", Path.home() / ".local/share/fonts"]
    seen, out = set(), []
    for d in dirs:
        if d.exists() and str(d.resolve()) not in seen:
            seen.add(str(d.resolve()))
            out.append(d)
    return out


def _walk_fonts(base: Path, depth: int = 4):
    base_parts = len(base.parts)
    for root, dirnames, files in os.walk(base):
        if len(Path(root).parts) - base_parts >= depth:
            dirnames[:] = []
        for f in files:
            if f.lower().endswith(FONT_EXTS):
                yield Path(root) / f


def find_system_font(name: str) -> Optional[Path]:
    low = Path(name).name.lower()
    for d in system_font_dirs():
        for f in _walk_fonts(d):
            if f.name.lower() == low:
                return f
    return None


def resolve_font(spec: Optional[str], assets_dir: Path, weight: str = "bold") -> Tuple[Optional[Path], bool]:
    """폰트 지정(spec) -> (경로, Pretendard 여부). spec: '' = 자동 / 'assets:파일명' / 'system:파일명'.
    지정한 폰트를 못 찾으면 자동 선택으로 대체한다."""
    spec = (spec or "").strip()
    if spec.startswith("assets:"):
        f = Path(assets_dir) / Path(spec[7:]).name
        if f.exists() and f.suffix.lower() in FONT_EXTS:
            return f, f.name.lower().startswith("pretendard")
    elif spec.startswith("system:"):
        f = find_system_font(spec[7:])
        if f:
            return f, False
    return find_font(assets_dir, weight)


def list_fonts(assets_dir: Path, limit: int = 500) -> List[Dict[str, str]]:
    """선택 가능한 폰트 목록 [{spec, name, group}] (assets/ 먼저, 그다음 시스템 폰트)."""
    out: List[Dict[str, str]] = []
    seen = set()
    ad = Path(assets_dir)
    if ad.exists():
        for f in sorted(ad.iterdir(), key=lambda x: x.name.lower()):
            if f.suffix.lower() in FONT_EXTS:
                out.append({"spec": f"assets:{f.name}", "name": f.stem, "group": "assets"})
                seen.add(f.name.lower())
    sysf = []
    for d in system_font_dirs():
        for f in _walk_fonts(d):
            if f.name.lower() not in seen:
                seen.add(f.name.lower())
                sysf.append(f)
    for f in sorted(sysf, key=lambda x: x.name.lower())[: max(0, limit - len(out))]:
        out.append({"spec": f"system:{f.name}", "name": f.stem, "group": "system"})
    return out


# --------------------------------------------------------------------------- text helpers
def wrap_text(text: str, width: int) -> str:
    """공백 단위 그리디 줄바꿈, 공백이 없거나 단어가 길면 width 글자마다 강제 분할."""
    text = " ".join((text or "").split())
    if width <= 0 or len(text) <= width:
        return text
    lines: List[str] = []
    cur = ""
    for tok in text.split(" "):
        while len(tok) > width:  # 공백 없는 긴 문장(일/중문)
            if cur:
                lines.append(cur)
                cur = ""
            lines.append(tok[:width])
            tok = tok[width:]
        if not cur:
            cur = tok
        elif len(cur) + 1 + len(tok) <= width:
            cur += " " + tok
        else:
            lines.append(cur)
            cur = tok
    if cur:
        lines.append(cur)
    return "\n".join(lines)


def ff_escape(path: str) -> str:
    """필터 옵션 값(fontfile/textfile)용 경로 이스케이프: 역슬래시->슬래시, ':' 와 따옴표 이스케이프."""
    p = str(path).replace("\\", "/")
    return p.replace(":", "\\:").replace("'", "\\'")


def rel_or_abs(p: Path, base: Path) -> str:
    try:
        return Path(p).resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return Path(p).resolve().as_posix()


# --------------------------------------------------------------------------- timeline
def build_timeline(scenes: List[Dict[str, Any]], durations: List[float], wrap: int) -> List[Tuple[float, float, str]]:
    """씬 beats(3개) -> 클립 실제 길이를 3등분한 자막 이벤트 [(start, end, text)]."""
    events: List[Tuple[float, float, str]] = []
    t0 = 0.0
    for sc, dur in zip(scenes, durations):
        seg = dur / 3.0
        for j, b in enumerate(sc["beats"][:3]):
            b = (b or "").strip()
            if b:
                events.append((round(t0 + j * seg, 3), round(t0 + (j + 1) * seg, 3), wrap_text(b, wrap)))
        t0 += dur
    return events


# --------------------------------------------------------------------------- ffmpeg command
HEX_RE = re.compile(r"^#?([0-9a-fA-F]{6})$")


def _hex(v: Any, default: str) -> str:
    m = HEX_RE.match(str(v if v is not None else "").strip())
    return (m.group(1) if m else str(default)).upper()


def _num(v: Any, default: Any, lo: float, hi: float) -> float:
    try:
        x = float(v)
    except (TypeError, ValueError):
        x = float(default)
    return max(lo, min(hi, x))


def render_settings(cfg: Dict[str, Any], project: Dict[str, Any]) -> Dict[str, Any]:
    """project.render + config.layout 기본값 -> 검증/보정된 합성 설정 (레터박스, 타이틀, 자막 스타일)."""
    lay, r = cfg["layout"], project["render"]
    W, H = lay["width"], lay["height"]
    top = int(_num(r.get("top_bar"), lay["top_bar"], 0, 800))
    bottom = int(_num(r.get("bottom_bar"), lay["bottom_bar"], 0, 800))
    video_h = H - top - bottom
    if video_h < 400:
        raise StitchError(f"레터박스가 너무 큽니다: 상단 {top}px + 하단 {bottom}px 이면 영상 높이가 {video_h}px 입니다 (최소 400px).")
    box = bool(r.get("sub_box", lay["sub_box"]))
    border = int(_num(r.get("sub_box_border"), lay["sub_box_border"], 0, 60)) if box else 0
    sub_bottom = int(_num(r.get("sub_bottom"), 0, 0, H)) or (H - bottom - int(_num(r.get("sub_bottom_gap"), lay["sub_bottom_gap"], 0, 400)))
    return {
        "W": W, "H": H, "top": top, "bottom": bottom, "video_h": video_h, "bar": _hex(r.get("bar_color"), lay["bar_color"]),
        "zoom": _num(r.get("crop_scale"), cfg["spec"]["crop_scale"], 1.0, 1.5), "fit": r.get("fit", "cover"),
        "title_size": int(_num(r.get("title_size"), lay["title_size"], 12, 200)), "title_color": _hex(r.get("title_color"), lay["title_color"]),
        "title_outline": int(_num(r.get("title_outline"), lay["title_outline"], 0, 20)), "title_outline_color": _hex(r.get("title_outline_color"), lay["title_outline_color"]),
        "title_y": int(_num(r.get("title_y"), 0, -600, 600)), "title_chars": int(_num(r.get("title_chars_per_line"), lay["title_chars_per_line"], 4, 60)),
        "sub_size": int(_num(r.get("sub_size"), lay["sub_size"], 12, 200)), "sub_color": _hex(r.get("sub_color"), lay["sub_color"]),
        "sub_outline": int(_num(r.get("sub_outline"), lay["sub_outline"], 0, 20)), "sub_outline_color": _hex(r.get("sub_outline_color"), lay["sub_outline_color"]),
        "sub_box": box, "sub_box_color": _hex(r.get("sub_box_color"), lay["sub_box_color"]), "sub_box_alpha": _num(r.get("sub_box_alpha"), lay["sub_box_alpha"], 0, 1),
        "sub_border": border, "sub_gap": int(_num(r.get("sub_gap"), lay["sub_gap"], 0, 60)), "sub_bottom": sub_bottom,
        "sub_chars": int(_num(r.get("sub_chars_per_line"), lay["sub_chars_per_line"], 4, 80)),
    }


def build_command(
    clips: List[Path], voice: Optional[Path], project: Dict[str, Any], cfg: Dict[str, Any], durations: List[float],
    font_title: Optional[Path], font_sub: Optional[Path], out_path: Path, tmp_rel: str = "output/_tmp",
) -> Tuple[List[str], Dict[str, str]]:
    """(ffmpeg 인자 리스트, {상대경로: 파일내용}) 반환. 텍스트는 textfile 로 넘겨 따옴표/콜론/% 이스케이프 문제를 원천 차단."""
    S = render_settings(cfg, project)
    W, H, TOP, VH = S["W"], S["H"], S["top"], S["video_h"]
    zoom, fit = S["zoom"], S["fit"]
    mult = LANG_WIDTH_MULT.get(project["meta"]["language"], 1.0)
    sub_w, title_w = int(S["sub_chars"] * mult), int(S["title_chars"] * mult)

    files: Dict[str, str] = {}
    n = len(clips)
    zw, zh = round(W * zoom), round(VH * zoom)
    norm = []
    for i in range(n):
        if fit == "contain":
            f = (f"scale=w={zw}:h={zh}:force_original_aspect_ratio=decrease,crop='min(iw,{W})':'min(ih,{VH})',"
                 f"pad={W}:{VH}:(ow-iw)/2:(oh-ih)/2:color=black")
        else:  # cover: 화면을 꽉 채우고 중앙 크롭 (검은 기둥 없음)
            f = f"scale=w={zw}:h={zh}:force_original_aspect_ratio=increase,crop={W}:{VH}"
        norm.append(f"[{i}:v]{f},setsar=1,fps={FPS},format=yuv420p[v{i}]")
    chain = [";".join(norm), "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[cat]"]

    draw: List[str] = [f"pad={W}:{H}:0:{TOP}:color=0x{S['bar']}"]
    gap = 8  # 타이틀 줄 간격(px). drawtext 는 줄별 중앙정렬이 없어 한 줄씩 따로 그린다.

    def line_filters(font: Path, tag: str, text: str, size: int, color: str, y_expr: Callable[[int, int], str],
                     extra: str, enable: str = "") -> List[str]:
        lines = text.split("\n")
        out = []
        for k, ln in enumerate(lines):
            rel = f"{tmp_rel}/{tag}_{k}.txt"
            files[rel] = ln
            out.append(
                f"drawtext=fontfile='{ff_escape(rel_or_abs(font, BASE))}':textfile='{ff_escape(rel)}':expansion=none:"
                f"fontsize={size}:fontcolor=0x{color}:{extra}x=(w-text_w)/2:y={y_expr(k, len(lines))}{enable}")
        return out

    title = (project["meta"].get("top_title") or "").strip()
    if title and font_title:
        outline = f"borderw={S['title_outline']}:bordercolor=0x{S['title_outline_color']}:" if S["title_outline"] > 0 else ""
        ty = S["title_y"]
        if TOP > 0:
            y_title = lambda k, nn: f"({TOP}-({nn}*text_h+{nn - 1}*{gap}))/2+{k}*(text_h+{gap})+{ty}"  # noqa: E731
        else:  # 상단 바가 없으면 영상 위 상단에 겹쳐 그린다
            y_title = lambda k, nn: f"40+{k}*(text_h+{gap})+{ty}"  # noqa: E731
        draw += line_filters(font_title, "title", wrap_text(title, title_w), S["title_size"], S["title_color"], y_title, outline)
    if font_sub:
        border, sb, sgap = S["sub_border"], S["sub_bottom"], S["sub_gap"]
        extra = (f"borderw={S['sub_outline']}:bordercolor=0x{S['sub_outline_color']}:" if S["sub_outline"] > 0 else "")
        if S["sub_box"]:
            extra += f"box=1:boxcolor=0x{S['sub_box_color']}@{S['sub_box_alpha']:g}:boxborderw={border}:"
        for k, (a, b, text) in enumerate(build_timeline(project["scenes"], durations, sub_w)):
            draw += line_filters(
                font_sub, f"sub{k:02d}", text, S["sub_size"], S["sub_color"],
                lambda j, nn: f"{sb}-{border}-{nn - j}*text_h-{nn - j - 1}*{sgap}", extra,
                f":enable='gte(t,{a})*lt(t,{b})'")
    chain.append("[cat]" + ",".join(draw) + "[outv]")

    total = sum(durations)
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-nostats", "-progress", "pipe:1"]
    for c in clips:
        cmd += ["-i", str(c)]
    if voice:
        cmd += ["-i", str(voice)]
    cmd += ["-filter_complex", ";".join(chain), "-map", "[outv]"]
    if voice:
        cmd += ["-map", f"{n}:a", "-af", "apad", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            "-t", f"{total:.3f}", str(out_path)]
    return cmd, files


# --------------------------------------------------------------------------- run
def probe_duration(path: Path) -> Optional[float]:
    if not shutil.which("ffprobe"):
        return None
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)], capture_output=True, text=True)
    try:
        return float(json.loads(r.stdout)["format"]["duration"])
    except (ValueError, KeyError, json.JSONDecodeError):
        return None


def preflight(input_dir: Path, assets_dir: Path, n_scenes: int = 6) -> Dict[str, Any]:
    clips = {i: find_clip(input_dir, i) for i in range(1, n_scenes + 1)}
    voice = find_voice(input_dir)
    fb, pretendard = find_font(assets_dir, "black")
    return {
        "ffmpeg": bool(shutil.which("ffmpeg") and shutil.which("ffprobe")),
        "clips": {i: (p.name if p else None) for i, p in clips.items()},
        "missing_clips": [i for i, p in clips.items() if not p],
        "voice": voice.name if voice else None,
        "font": fb.name if fb else None, "pretendard": pretendard,
    }


def render(
    project: Dict[str, Any], input_dir: Path = BASE / "input", output_dir: Path = BASE / "output", assets_dir: Path = BASE / "assets",
    out_name: str = "final_shorts.mp4", partial: bool = False, dry_run: bool = False,
    log: Callable[[str], None] = print, on_progress: Optional[Callable[[float], None]] = None, cfg: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    cfg = cfg or pe.load_config()
    project = pe.normalize_project(project, cfg)
    input_dir, output_dir, assets_dir = Path(input_dir), Path(output_dir), Path(assets_dir)
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        raise StitchError("ffmpeg/ffprobe 를 찾을 수 없습니다. 설치: winget install Gyan.FFmpeg (설치 후 새 터미널에서 ffmpeg -version 확인)")
    idx = list(range(1, len(project["scenes"]) + 1))
    found = {i: find_clip(input_dir, i) for i in idx}
    missing = [i for i, p in found.items() if not p]
    if missing and not partial and not dry_run:
        raise StitchError("씬 클립이 없습니다: " + ", ".join(f"scene{i}.mp4" for i in missing) + f"  (폴더: {input_dir})")
    # dry-run 은 클립이 없어도 명령 구조를 보여준다(자리표시 경로 사용)
    use = idx if (dry_run and not partial) else [i for i in idx if found[i]]
    if not use:
        raise StitchError(f"렌더할 클립이 하나도 없습니다 ({input_dir}).")
    clips = [found[i] or input_dir / f"scene{i}.mp4" for i in use]
    if dry_run and missing and not partial:
        log(f"[dry-run] 없는 클립은 자리표시 경로로 표시합니다: {', '.join(f'scene{i}.mp4' for i in missing)}")
    scenes = [project["scenes"][i - 1] for i in use]
    durations = []
    for c in clips:
        d = probe_duration(c) if c.exists() else None
        durations.append(d if d and d > 0.5 else cfg["spec"]["scene_seconds"])
    voice = find_voice(input_dir)
    rnd = project["render"]
    font_title, pre_t = resolve_font(rnd.get("title_font"), assets_dir, "black")
    font_sub, pre_s = resolve_font(rnd.get("sub_font"), assets_dir, "bold")
    if not font_title or not font_sub:
        raise StitchError("한글 폰트를 찾지 못했습니다. assets/ 폴더에 Pretendard-Black.ttf, Pretendard-Bold.ttf 를 넣거나 대시보드에서 글꼴을 선택해 주세요.")
    if not (pre_t and pre_s) and not (rnd.get("title_font") or rnd.get("sub_font")):
        log(f"[알림] Pretendard 폰트가 없어 대체 폰트({font_title.name})를 사용합니다. assets/ 에 Pretendard 를 넣으면 디자인이 정확해집니다.")
    if not voice:
        log("[경고] input/voice.mp3 가 없어 무음 영상으로 렌더합니다.")
    total = sum(durations)
    if voice:
        ad = probe_duration(voice)
        if ad and abs(ad - total) > 1.5:
            log(f"[경고] 음성 {ad:.1f}초 / 영상 {total:.1f}초 - 길이 차이가 큽니다. " + ("음성이 길면 끝이 잘립니다." if ad > total else "음성이 짧으면 끝이 무음입니다."))
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / out_name
    cmd, files = build_command(clips, voice, project, cfg, durations, font_title, font_sub, out_path)
    if dry_run:
        return {"dry_run": True, "command": cmd, "files": files, "clips": [c.name for c in clips], "duration": total}
    tmp = BASE / "output" / "_tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    for rel, content in files.items():
        p = BASE / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    log(f"▶ 렌더링 시작: 클립 {len(clips)}개 / {total:.1f}초 / 자막 {sum(1 for r in files if '/sub' in r and r.endswith('_0.txt'))}개")
    tail: List[str] = []
    try:
        with subprocess.Popen(cmd, cwd=str(BASE), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace") as proc:
            assert proc.stdout is not None
            for line in proc.stdout:
                line = line.strip()
                m = re.match(r"out_time_us=(\d+)", line)
                if m and on_progress:
                    on_progress(min(0.99, int(m.group(1)) / 1e6 / max(total, 0.1)))
                elif line and not re.match(r"(frame|fps|stream_|bitrate|total_size|out_time|dup_frames|drop_frames|speed|progress)=", line):
                    tail.append(line)
            rc = proc.wait()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if rc != 0:
        raise StitchError("ffmpeg 렌더 실패:\n" + "\n".join(tail[-12:]))
    if on_progress:
        on_progress(1.0)
    log(f"★ 렌더링 완료: {out_path}")
    return {"output": str(out_path), "duration": probe_duration(out_path), "clips": [c.name for c in clips]}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="쇼츠 합성 렌더러 (6클립 + 음성 + 자막 -> 1080x1920)")
    ap.add_argument("--project", required=True, help="프로젝트 JSON (대시보드 저장/내보내기 파일 또는 samples/*.json)")
    ap.add_argument("--input", default=str(BASE / "input")); ap.add_argument("--output", default=str(BASE / "output"))
    ap.add_argument("--assets", default=str(BASE / "assets")); ap.add_argument("--out-name", default="final_shorts.mp4")
    ap.add_argument("--fit", choices=["cover", "contain"], help="cover=꽉 채움(기본), contain=원본 비율 유지(좌우 검은 기둥)")
    ap.add_argument("--crop", type=float, help="워터마크 크롭 배율 (기본 1.06)")
    ap.add_argument("--title", help="상단 타이틀 덮어쓰기")
    ap.add_argument("--top-bar", type=int, help="상단 검정 바 높이(px)"); ap.add_argument("--bottom-bar", type=int, help="하단 검정 바 높이(px)")
    ap.add_argument("--partial", action="store_true", help="있는 클립만으로 미리보기 렌더")
    ap.add_argument("--dry-run", action="store_true", help="실행하지 않고 FFmpeg 명령만 출력")
    a = ap.parse_args(argv)
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    proj = json.loads(Path(a.project).read_text(encoding="utf-8"))
    proj = pe.normalize_project(proj)
    if a.fit:
        proj["render"]["fit"] = a.fit
    if a.crop:
        proj["render"]["crop_scale"] = a.crop
    if a.title:
        proj["meta"]["top_title"] = a.title
    if a.top_bar is not None:
        proj["render"]["top_bar"] = a.top_bar
    if a.bottom_bar is not None:
        proj["render"]["bottom_bar"] = a.bottom_bar
    try:
        res = render(proj, Path(a.input), Path(a.output), Path(a.assets), a.out_name, a.partial, a.dry_run,
                     on_progress=lambda p: print(f"\r  진행 {p * 100:5.1f}%", end="", flush=True))
    except StitchError as e:
        print("\n오류:", e, file=sys.stderr)
        return 1
    if a.dry_run:
        print(" ".join(f'"{c}"' if " " in c or "[" in c or ";" in c else c for c in res["command"]))
        print(f"\n(텍스트 파일 {len(res['files'])}개는 실행 시 output/_tmp 에 생성됨)")
    else:
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
