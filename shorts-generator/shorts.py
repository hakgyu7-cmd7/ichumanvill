#!/usr/bin/env python3
"""YouTube 롱폼 → 숏폼 자동 추출기.

파이프라인:
  1. 입력          : 내 영상 파일 (YouTube URL도 가능 — yt-dlp 설치 시)
  2. faster-whisper: 음성 → 텍스트 (단어 단위 타임스탬프)
  3. Claude        : 자막을 읽고 숏폼으로 쓸 하이라이트 구간 선정
  4. OpenCV        : 얼굴 위치를 찾아 9:16 세로 크롭 위치 결정
  5. ffmpeg        : 구간 자르기 + 세로 변환 + 자막 입히기
  6. YouTube API   : 자동 업로드 / 예약 공개 (선택, upload.py)

사용 예:
  python shorts.py 내영상.mp4 --clips 3 --min 20 --max 45
  python shorts.py 내영상.mp4 --upload --schedule 2026-11-01T18:00     # 추출 + 하루 1개씩 예약 업로드
  python shorts.py --watch inbox --upload                              # inbox 폴더에 넣은 영상 자동 처리
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path

OUT_W, OUT_H = 1080, 1920


@dataclass
class Word:
    start: float
    end: float
    text: str


@dataclass
class Segment:
    start: float
    end: float
    text: str
    words: list[Word]


@dataclass
class Clip:
    start: float
    end: float
    title: str
    hook: str
    reason: str
    score: int
    hashtags: list[str]


# ---------------------------------------------------------------- 1. 다운로드

def download(source: str, workdir: Path) -> Path:
    if Path(source).exists():
        return Path(source).resolve()

    if not re.match(r"https?://", source):
        sys.exit(f"파일을 찾을 수 없습니다: {source}")
    try:
        import yt_dlp
    except ImportError:
        sys.exit("URL을 받으려면 yt-dlp가 필요합니다: pip install yt-dlp")

    out = workdir / "source.mp4"
    if out.exists():
        print(f"[1/5] 다운로드 건너뜀 (이미 있음): {out}")
        return out

    print(f"[1/5] 다운로드 중: {source}")
    opts = {
        "format": "bv*[height<=1080]+ba/b[height<=1080]/b",
        "merge_output_format": "mp4",
        "outtmpl": str(out),
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([source])
    return out


def probe(video: Path) -> tuple[int, int, float]:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height:format=duration",
         "-of", "json", str(video)],
        capture_output=True, text=True, check=True,
    )
    info = json.loads(result.stdout)
    stream = info["streams"][0]
    return int(stream["width"]), int(stream["height"]), float(info["format"]["duration"])


# ---------------------------------------------------------------- 2. 받아쓰기

def add_nvidia_dll_dirs() -> None:
    """Windows에서 pip로 설치한 nvidia-cublas/cudnn의 DLL 폴더를 검색 경로에 추가한다."""
    if os.name != "nt":
        return
    try:
        import nvidia
    except ImportError:
        return
    for base in nvidia.__path__:
        for bin_dir in Path(base).glob("*/bin"):
            os.add_dll_directory(str(bin_dir))
            os.environ["PATH"] = str(bin_dir) + os.pathsep + os.environ.get("PATH", "")

def transcribe(video: Path, workdir: Path, model_size: str, language: str | None,
               device: str = "auto") -> list[Segment]:
    cache = workdir / "transcript.json"
    if cache.exists():
        print(f"[2/5] 받아쓰기 건너뜀 (캐시 사용): {cache}")
        data = json.loads(cache.read_text(encoding="utf-8"))
        return [Segment(s["start"], s["end"], s["text"], [Word(**w) for w in s["words"]]) for s in data]

    import numpy as np
    add_nvidia_dll_dirs()
    from faster_whisper import WhisperModel

    print(f"[2/5] 받아쓰기 중 (whisper {model_size}) — 영상 길이에 따라 오래 걸릴 수 있습니다")
    # faster-whisper 내장 디코더(PyAV)는 버전 호환 문제가 잦아서 ffmpeg로 16kHz 모노 오디오를 직접 뽑아 넘긴다
    pcm = subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(video),
         "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
        capture_output=True, check=True,
    ).stdout
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0

    def run(device: str):
        model = WhisperModel(model_size, device=device, compute_type="int8" if device == "cpu" else "auto")
        raw_segments, info = model.transcribe(
            audio, language=language, word_timestamps=True, vad_filter=True,
        )
        segments: list[Segment] = []
        for s in raw_segments:
            words = [Word(w.start, w.end, w.word.strip()) for w in (s.words or []) if w.word.strip()]
            segments.append(Segment(s.start, s.end, s.text.strip(), words))
            print(f"      {fmt_ts(s.start)} {s.text.strip()[:60]}", end="\r")
        return segments, info

    try:
        segments, info = run(device)
    except RuntimeError as e:
        # NVIDIA GPU는 있는데 CUDA 라이브러리(cuBLAS/cuDNN)가 없으면 받아쓰기 도중에 실패한다 → CPU로 다시
        if device == "cpu" or not re.search(r"cublas|cudnn|cuda", str(e), re.I):
            raise
        print(f"\n      ⚠ GPU 사용 불가({e}) → CPU로 다시 받아쓰기합니다 (조금 더 느림)")
        segments, info = run("cpu")
    print(f"\n      언어: {info.language}, 구간 {len(segments)}개")

    cache.write_text(json.dumps([asdict(s) for s in segments], ensure_ascii=False, indent=1), encoding="utf-8")
    return segments


# ---------------------------------------------------------------- 3. 구간 선정

# --preset으로 고르는 구간 선정 기준 (--prompt를 직접 주면 그쪽이 우선)
PRESETS = {
    "story": (
        "이 영상은 시니어가 잠들기 전 듣는 옛날이야기·민담 낭독이다. 숏폼은 새 시청자를 롱폼으로 데려오는 예고편 역할이다. "
        "첫인사·끝인사·구독 요청 구간은 제외하고, 이야기 속에서 인물의 처지가 바뀌는 순간, 반전, 궁금증이 생기는 장면을 고른다. "
        "구간은 사건이 시작되는 문장에서 시작하고, 결말은 다 보여주지 말고 '그래서 어떻게 됐을까' 싶은 지점에서 끝낸다. "
        "title은 이야기 속 인물과 사건이 드러나게 짓는다 (예: '장터에서 쫓겨난 과부의 삼십 년 뒤')."
    ),
}

SYSTEM_PROMPT = """당신은 YouTube Shorts / 릴스 / 틱톡 전문 편집자입니다.
긴 영상의 타임스탬프 자막을 읽고, 그 자체로 완결되어 숏폼으로 올렸을 때 반응이 좋을 구간을 고릅니다.

좋은 구간의 기준:
- 첫 3초 안에 시청자를 붙잡는 훅(질문, 반전, 강한 주장, 감정이 터지는 순간)으로 시작
- 앞뒤 맥락 없이도 이해되는 하나의 완결된 이야기·정보·웃음
- 문장 중간에서 시작하거나 끊기지 않음 (자막 줄의 시작/끝 시각에 맞출 것)
- 인사, 광고, 구독 요청, 잡담 구간은 제외
- 구간끼리 겹치지 않음

title은 숏폼 제목으로 바로 쓸 수 있게 짧고 궁금증을 유발하도록, 영상과 같은 언어로 작성하세요."""


def select_clips(segments: list[Segment], duration: float, n: int, min_len: int, max_len: int,
                 model: str, extra: str | None) -> list[Clip]:
    import anthropic

    print(f"[3/5] Claude({model})로 하이라이트 구간 선정 중")
    transcript = "\n".join(f"[{s.start:.1f}-{s.end:.1f}] {s.text}" for s in segments)
    user = (
        f"영상 길이: {duration:.0f}초\n"
        f"숏폼 {n}개를 골라주세요. 각 구간은 {min_len}~{max_len}초 사이여야 합니다.\n"
        f"start/end는 아래 자막의 초 단위 시각을 사용하세요. score는 1~100 (바이럴 가능성).\n"
        + (f"추가 요청: {extra}\n" if extra else "")
        + f"\n<transcript>\n{transcript}\n</transcript>"
    )
    schema = {
        "type": "object",
        "properties": {
            "clips": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "number"},
                        "end": {"type": "number"},
                        "title": {"type": "string"},
                        "hook": {"type": "string", "description": "첫 문장 / 훅 요약"},
                        "reason": {"type": "string", "description": "이 구간을 고른 이유"},
                        "score": {"type": "integer"},
                        "hashtags": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["start", "end", "title", "hook", "reason", "score", "hashtags"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["clips"],
        "additionalProperties": False,
    }

    client = anthropic.Anthropic()
    response = client.beta.messages.create(
        model=model,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user}],
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": schema}},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if response.stop_reason == "refusal":
        sys.exit("Claude가 요청을 거절했습니다. 자막 내용을 확인해주세요.")
    if response.stop_reason == "max_tokens":
        sys.exit("응답이 잘렸습니다. --clips 수를 줄여서 다시 시도해주세요.")

    text = next(b.text for b in response.content if b.type == "text")
    clips = [Clip(**c) for c in json.loads(text)["clips"]]
    return [c for c in (snap(c, segments, duration, min_len, max_len) for c in clips) if c]


def snap(clip: Clip, segments: list[Segment], duration: float, min_len: int, max_len: int) -> Clip | None:
    """구간 경계를 자막 줄 경계에 맞추고 길이를 검증한다."""
    starts = [s.start for s in segments if s.start <= clip.start + 0.5]
    ends = [s.end for s in segments if s.end >= clip.end - 0.5]
    start = max(starts) if starts else clip.start
    end = min(ends) if ends else clip.end
    start, end = max(0.0, start - 0.15), min(duration, end + 0.3)
    if end - start > max_len + 5:
        end = start + max_len
    if end - start < min_len * 0.6:
        print(f"      ⚠ 너무 짧아 제외: {clip.title} ({end - start:.1f}s)")
        return None
    clip.start, clip.end = round(start, 2), round(end, 2)
    return clip


# ---------------------------------------------------------------- 4. 크롭 위치

YUNET_URL = ("https://media.githubusercontent.com/media/opencv/opencv_zoo/main/"
             "models/face_detection_yunet/face_detection_yunet_2023mar.onnx")
SAMPLE_STEP = 0.25  # 얼굴/장면 전환 검사 간격(초)


def load_face_detector():
    """얼굴 검출 함수(frame → [(cx, 면적), ...])를 돌려준다. YuNet(정확, 옆얼굴도 잡음) → Haar(기본) 순."""
    import cv2
    import numpy as np

    # OpenCV는 Windows에서 한글 등 비ASCII 경로의 파일을 못 열므로 모델은 전부 Python으로 읽어 메모리에서 로드한다
    model = Path(__file__).resolve().parent / "models" / "face_detection_yunet_2023mar.onnx"
    try:
        if not model.exists():
            import urllib.request
            print("      얼굴 인식 모델(YuNet) 내려받는 중 (처음 한 번)")
            model.parent.mkdir(exist_ok=True)
            data = urllib.request.urlopen(YUNET_URL, timeout=30).read()
            if len(data) < 100_000:
                raise ValueError("모델 다운로드 실패")
            model.write_bytes(data)
        yunet = cv2.FaceDetectorYN.create("onnx", np.frombuffer(model.read_bytes(), np.uint8),
                                          np.array([], np.uint8), (320, 320), 0.6)

        def detect(frame):
            h, w = frame.shape[:2]
            scale = 640 / w
            small = cv2.resize(frame, (640, int(h * scale)))
            yunet.setInputSize((small.shape[1], small.shape[0]))
            _, faces = yunet.detect(small)
            if faces is None:
                return []
            return [((f[0] + f[2] / 2) / scale, f[2] * f[3] / scale ** 2) for f in faces]
        return detect
    except Exception as e:
        print(f"      ⚠ YuNet 사용 불가({e}) → 기본 얼굴 인식 사용")

    xml = (Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml").read_text(encoding="utf-8")
    fs = cv2.FileStorage(xml, cv2.FILE_STORAGE_READ | cv2.FILE_STORAGE_MEMORY)
    cascade = cv2.CascadeClassifier()
    cascade.read(fs.getFirstTopLevelNode())
    fs.release()

    def detect(frame):
        gray = cv2.cvtColor(cv2.resize(frame, None, fx=0.5, fy=0.5), cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(30, 30))
        return [((x + w / 2) * 2, w * h * 4) for x, y, w, h in faces]
    return detect


def track_faces(video: Path, start: float, end: float, width: int, detect) -> list[tuple[float, float]]:
    """장면(컷)마다 주인공 얼굴 위치를 찾는다. 반환: [(클립 기준 장면 시작 초, 얼굴 중심 x), ...]"""
    import cv2

    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        return [(0.0, width / 2)]
    scenes: list[tuple[float, list[float]]] = []  # (장면 시작, 그 장면에서 찾은 얼굴 x들)
    prev_hist = None
    t = start
    while t < end:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if not ok:
            break
        hsv = cv2.cvtColor(cv2.resize(frame, (160, 90)), cv2.COLOR_BGR2HSV)
        hist = cv2.normalize(cv2.calcHist([hsv], [0, 1], None, [32, 32], [0, 180, 0, 256]), None).flatten()
        if prev_hist is None or cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL) < 0.6:
            scenes.append((t - start, []))  # 화면이 크게 바뀜 = 새 장면
        prev_hist = hist
        faces = detect(frame)
        if faces:
            scenes[-1][1].append(max(faces, key=lambda f: f[1])[0])  # 가장 큰 얼굴 = 주인공
        t += SAMPLE_STEP
    cap.release()

    result: list[tuple[float, float]] = []
    last_x = width / 2
    for i, (st, xs) in enumerate(scenes):
        # 얼굴이 없는 장면은 직전 위치 유지 (풍경·소품 컷에서 화면이 튀지 않게)
        x = statistics.median(xs) if xs else last_x
        if result and abs(x - result[-1][1]) < width * 0.03:
            continue  # 거의 같은 위치면 합침
        result.append((round(st, 2), x))
        last_x = x
    return result or [(0.0, width / 2)]


def crop_filter(video: Path, clip: Clip, width: int, height: int, layout: str, detect=None) -> str:
    if width / height <= OUT_W / OUT_H + 0.01:  # 이미 세로 영상
        return f"scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=decrease,pad={OUT_W}:{OUT_H}:(ow-iw)/2:(oh-ih)/2"
    if layout == "fit":  # 원본 전체를 가운데에, 위아래는 흐린 배경 (인물이 잘리지 않음)
        return (f"split[a][b];[a]scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=increase,"
                f"crop={OUT_W}:{OUT_H},boxblur=25:3,eq=brightness=-0.15[bg];"
                f"[b]scale={OUT_W}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2")

    crop_w = int(height * OUT_W / OUT_H) // 2 * 2
    points = [(0.0, width / 2)]
    if layout == "face" and detect:
        try:
            points = track_faces(video, clip.start, clip.end, width, detect)
        except Exception as e:  # 얼굴 인식이 실패해도 렌더링은 계속
            print(f"      ⚠ 얼굴 인식 실패({e}) → 가운데 크롭")
    xs = [int(min(max(cx - crop_w / 2, 0), width - crop_w)) for _, cx in points]
    # 장면이 바뀔 때마다 크롭 위치를 바꾸는 ffmpeg 식: if(lt(t,2.5),x0,if(lt(t,6.0),x1,x2))
    expr = str(xs[-1])
    for (t_next, _), x in zip(reversed(points[1:]), reversed(xs[:-1])):
        expr = f"if(lt(t,{t_next}),{x},{expr})"
    return f"crop={crop_w}:{height}:'{expr}':0,scale={OUT_W}:{OUT_H}"


# ---------------------------------------------------------------- 5. 자막 + 렌더링

def font_family(path: Path) -> str | None:
    """TTF/OTF 파일 안에 적힌 글꼴 이름(name table의 family)을 읽는다. 자막에 그 이름을 써야 해당 글꼴이 쓰인다."""
    import struct
    data = path.read_bytes()
    if data[:4] == b"ttcf":  # 글꼴 묶음 파일은 첫 번째 글꼴만
        data_off = struct.unpack(">I", data[12:16])[0]
    else:
        data_off = 0
    num = struct.unpack(">H", data[data_off + 4:data_off + 6])[0]
    for i in range(num):
        tag, _, off, _ = struct.unpack(">4sIII", data[data_off + 12 + 16 * i:data_off + 28 + 16 * i])
        if tag != b"name":
            continue
        _, count, str_off = struct.unpack(">HHH", data[off:off + 6])
        names = {}
        for j in range(count):
            pid, eid, lang, nid, length, noff = struct.unpack(">6H", data[off + 6 + 12 * j:off + 18 + 12 * j])
            if nid not in (1, 16):
                continue
            raw = data[off + str_off + noff:off + str_off + noff + length]
            text = raw.decode("utf-16-be", "ignore") if pid in (0, 3) else raw.decode("latin-1", "ignore")
            names[(nid, pid == 3 and lang == 0x409)] = text
        for key in [(16, True), (1, True), (16, False), (1, False)]:
            if names.get(key):
                return names[key]
    return None


def ass_color(hex_rgb: str) -> str:
    """'FFE400' 같은 RGB 색을 ASS 자막 색 형식(&H00BBGGRR)으로."""
    h = hex_rgb.lstrip("#")
    return f"&H00{h[4:6]}{h[2:4]}{h[0:2]}".upper()


def ass_time(t: float) -> str:
    t = max(t, 0)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def write_ass(path: Path, clip: Clip, segments: list[Segment], font: str, words_per_line: int,
              font_size: int, sub_y: int, title: bool, color: str = "FFE400", center: bool = True,
              cta: dict | None = None) -> None:
    words = [w for s in segments for w in s.words if w.end > clip.start and w.start < clip.end]
    lines: list[tuple[float, float, str]] = []
    for i in range(0, len(words), words_per_line):
        chunk = words[i:i + words_per_line]
        lines.append((chunk[0].start - clip.start, chunk[-1].end - clip.start, " ".join(w.text for w in chunk)))
    # 다음 줄이 나올 때까지 자막 유지 (깜빡임 방지)
    lines = [(s, min(lines[i + 1][0], e + 0.6) if i + 1 < len(lines) else e, txt)
             for i, (s, e, txt) in enumerate(lines)]

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {OUT_W}
PlayResY: {OUT_H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},{font_size},{ass_color(color)},&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{max(5, font_size // 12)},3,{5 if center else 2},70,70,{0 if center else sub_y},1
Style: Title,{font},{min(110, int(font_size * 0.8))},&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{max(5, font_size // 14)},3,8,60,60,300,1
Style: Cta,{font},96,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,1,0,0,0,1
Style: Arrow,{font},20,{ass_color(color)},&H0000FFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,6,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    def clean(txt: str) -> str:
        return txt.replace("{", "(").replace("}", ")")

    body = "".join(f"Dialogue: 0,{ass_time(s)},{ass_time(e)},Default,,0,0,0,,{clean(txt)}\n" for s, e, txt in lines)
    if title:  # fit 레이아웃: 위쪽 빈 공간에 제목 고정
        body += f"Dialogue: 0,{ass_time(0)},{ass_time(clip.end - clip.start)},Title,,0,0,0,,{clean(clip.title)}\n"
    if cta:
        body += cta_events(clip.end - clip.start, **cta)
    path.write_text(header + body, encoding="utf-8")


# 아래를 가리키는 화살표 (ASS 벡터 그림, 폭 165 x 높이 225). 글꼴과 상관없이 그려진다
ARROW = "m 48 0 l 117 0 l 117 123 l 165 123 l 82 225 l 0 123 l 48 123"
ARROW_W, ARROW_H = 165, 225


def cta_events(duration: float, text: str, x: int, y: int, seconds: float) -> str:
    """끝부분에 '원본 보기' 문구와 위아래로 움직이는 화살표를 넣는다.
    (x, y)는 화살표 끝이 가리킬 지점 = Shorts 화면에서 '관련 동영상' 링크가 뜨는 자리 (왼쪽 아래)."""
    start = max(0.0, duration - seconds)
    top, left = y - ARROW_H, x - ARROW_W // 2  # 화살표 그림의 왼쪽 위
    events = f"Dialogue: 1,{ass_time(start)},{ass_time(duration)},Cta,,0,0,0,,{{\\pos({left},{top - 50})\\fad(300,0)}}{text}\n"
    t, down, step, bounce = start, True, 0.35, 40
    while t < duration:
        y1, y2 = (top - bounce, top) if down else (top, top - bounce)
        end = min(duration, t + step)
        events += (f"Dialogue: 1,{ass_time(t)},{ass_time(end)},Arrow,,0,0,0,,"
                   f"{{\\move({left},{y1},{left},{y2})\\p1}}{ARROW}{{\\p0}}\n")
        t, down = end, not down
    return events


def render(video: Path, clip: Clip, vf: str, out: Path, ass: Path | None, fontsdir: str | None = None) -> None:
    if ass:
        vf += f",subtitles={ass.name}"  # cwd를 출력 폴더로 두어 경로 이스케이프 문제를 피함
        if fontsdir:
            vf += f":fontsdir={fontsdir}"
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-ss", f"{clip.start:.2f}", "-i", str(video.resolve()), "-t", f"{clip.end - clip.start:.2f}",
        "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
        out.name,
    ]
    subprocess.run(cmd, check=True, cwd=out.parent)


# ---------------------------------------------------------------- main

def fmt_ts(t: float) -> str:
    return f"{int(t // 60):02d}:{int(t % 60):02d}"


def slugify(text: str) -> str:
    return re.sub(r"[^\w가-힣]+", "_", text).strip("_")[:40] or "clip"


VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}


def process(source: str, args: argparse.Namespace) -> Path:
    name = Path(source).stem if Path(source).exists() else slugify(source)[-20:]
    out = Path(args.out) / name  # 영상마다 폴더를 따로 두어 받아쓰기 캐시가 섞이지 않게 함
    out.mkdir(parents=True, exist_ok=True)

    video = download(source, out)
    width, height, duration = probe(video)
    segments = transcribe(video, out, args.whisper_model, args.lang, args.device)
    if not segments:
        print("음성을 찾지 못했습니다.")
        return out

    clips_file = out / "clips.json"
    if args.reuse_clips and clips_file.exists():
        print("[3/5] 이전에 고른 구간 재사용 (clips.json)")
        fields = Clip.__dataclass_fields__
        clips = [Clip(**{k: v for k, v in c.items() if k in fields}) for c in json.loads(clips_file.read_text(encoding="utf-8"))]
    else:
        prompt = args.prompt or PRESETS.get(args.preset or "")
        clips = select_clips(segments, duration, args.clips, args.min_len, args.max_len, args.model, prompt)
    clips.sort(key=lambda c: c.score, reverse=True)
    for i, c in enumerate(clips, 1):
        print(f"      #{i} [{fmt_ts(c.start)}~{fmt_ts(c.end)}, {c.end - c.start:.0f}s, {c.score}점] {c.title}")

    results = []
    if not args.dry_run:
        print(f"[4-5/5] 세로 크롭 + 자막 렌더링 ({len(clips)}개, 레이아웃: {args.layout})")
        detect = load_face_detector() if args.layout == "face" else None
        # fit 레이아웃은 영상이 화면 가운데(약 656~1264px)에 오므로 자막을 영상 바로 아래 흐린 영역에 둔다
        sub_y = args.sub_y if args.sub_y is not None else (620 if args.layout == "fit" else 560)
        font, fontsdir = args.font, None
        if args.font_file and not args.no_subs:
            ff = Path(args.font_file)
            if not ff.exists():
                ff = Path(__file__).resolve().parent / args.font_file  # 상대 경로는 스크립트 폴더 기준으로도 찾기
            if ff.exists():
                (out / "fonts").mkdir(exist_ok=True)
                shutil.copy(ff, out / "fonts" / ff.name)  # 한글 경로 문제를 피하려고 출력 폴더 안으로 복사
                font, fontsdir = font_family(ff) or args.font, "fonts"
                print(f"      자막 글꼴: {font} ({ff.name})")
            else:
                print(f"      ⚠ 글꼴 파일을 찾지 못했습니다: {args.font_file} → '{args.font}' 사용")
        for i, c in enumerate(clips, 1):
            name = f"short_{i:02d}_{slugify(c.title)}"
            ass = None
            if not args.no_subs:
                ass = out / f"{name}.ass"
                write_ass(ass, c, segments, font, args.words_per_line, args.font_size, sub_y,
                          title=args.layout == "fit" and not args.no_title, color=args.sub_color,
                          center=args.sub_pos == "center",
                          cta=None if args.no_cta else {"text": args.cta_text, "x": args.cta_x,
                                                        "y": args.cta_y, "seconds": args.cta_seconds})
            vf = crop_filter(video, c, width, height, args.layout, detect)
            mp4 = out / f"{name}.mp4"
            render(video, c, vf, mp4, ass, fontsdir)
            print(f"      ✓ {mp4}")
            results.append({"file": mp4.name, **asdict(c)})
    else:
        results = [asdict(c) for c in clips]

    clips_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"완료! 결과: {out.resolve()} (제목·해시태그는 clips.json 참고)")

    if args.upload and not args.dry_run:
        from upload import upload_clips
        upload_clips(out, args.privacy, args.schedule, args.interval, args.footer)
    return out


def watch(inbox: Path, args: argparse.Namespace) -> None:
    """inbox 폴더를 감시하다가 새 영상이 들어오면 처리하고 inbox/done으로 옮긴다."""
    done = inbox / "done"
    done.mkdir(parents=True, exist_ok=True)
    sizes: dict[Path, int] = {}
    print(f"📂 {inbox.resolve()} 폴더를 감시 중입니다. 영상을 넣으면 자동으로 처리합니다. (종료: Ctrl+C)")
    while True:
        for f in sorted(inbox.iterdir()):
            if not f.is_file() or f.suffix.lower() not in VIDEO_EXTS:
                continue
            size = f.stat().st_size
            if sizes.get(f) != size:  # 복사가 끝날 때까지(크기가 변하지 않을 때까지) 대기
                sizes[f] = size
                continue
            print(f"\n▶ 새 영상: {f.name}")
            try:
                process(str(f), args)
                shutil.move(str(f), done / f.name)
            except Exception as e:  # 한 영상이 실패해도 감시는 계속
                print(f"      ✗ 실패: {e}")
                f.rename(f.with_suffix(f.suffix + ".failed"))
            sizes.pop(f, None)
        time.sleep(args.poll)


def main() -> None:
    from upload import add_upload_args

    p = argparse.ArgumentParser(description="롱폼 영상에서 숏폼 자동 추출 (+ YouTube 자동 업로드)")
    p.add_argument("source", nargs="?", help="내 영상 파일 (또는 YouTube URL)")
    p.add_argument("--watch", type=Path, metavar="DIR", help="이 폴더에 들어오는 영상을 계속 자동 처리")
    p.add_argument("--poll", type=int, default=30, help="--watch 확인 간격(초) (기본: 30)")
    p.add_argument("-o", "--out", default="output", help="출력 폴더 (영상별 하위 폴더 생성, 기본: output)")
    p.add_argument("-n", "--clips", type=int, default=5, help="뽑을 숏폼 개수 (기본: 5)")
    p.add_argument("--min", dest="min_len", type=int, default=20, help="최소 길이(초)")
    p.add_argument("--max", dest="max_len", type=int, default=59, help="최대 길이(초)")
    p.add_argument("--lang", default=None, help="음성 언어 코드 (예: ko, en). 생략 시 자동 감지")
    p.add_argument("--whisper-model", default="small", help="tiny/base/small/medium/large-v3 (기본: small)")
    p.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto",
                   help="받아쓰기 장치 (기본: auto — GPU가 안 되면 자동으로 CPU)")
    p.add_argument("--model", default="claude-opus-5-5", help="구간 선정에 쓸 Claude 모델")
    p.add_argument("--prompt", default=None, help="구간 선정 추가 지시 (예: '웃긴 장면 위주로')")
    p.add_argument("--preset", choices=sorted(PRESETS), default=None,
                   help="채널 유형별 구간 선정 기준 (story: 옛날이야기·민담 낭독 채널)")
    p.add_argument("--font", default="NanumGothic", help="자막 폰트 이름 (시스템에 설치된 폰트)")
    p.add_argument("--font-file", default=None, help="자막 글꼴 파일 (.ttf/.otf). 예: fonts/BMJUA_ttf.ttf")
    p.add_argument("--font-size", type=int, default=140, help="자막 글자 크기 (기본: 140)")
    p.add_argument("--sub-color", default="FFE400", help="자막 글자 색 RGB (기본: FFE400 노란색, 흰색은 FFFFFF)")
    p.add_argument("--no-cta", action="store_true", help="끝부분 '원본 보기' 화살표 넣지 않기")
    p.add_argument("--cta-text", default="전체 이야기 보러 가기", help="화살표 위 문구")
    p.add_argument("--cta-x", type=int, default=150, help="화살표 끝 x 위치 (1080 기준, 관련 동영상 링크 자리)")
    p.add_argument("--cta-y", type=int, default=1560, help="화살표 끝 y 위치 (1920 기준, 클수록 아래)")
    p.add_argument("--cta-seconds", type=float, default=6, help="끝에서 몇 초 동안 화살표를 보일지 (기본: 6)")
    p.add_argument("--sub-pos", choices=["center", "bottom"], default="center",
                   help="자막 위치 (기본: center — 화면 정중앙. Shorts 아래쪽은 제목·버튼에 가려짐)")
    p.add_argument("--sub-y", type=int, default=None, help="--sub-pos bottom일 때 화면 아래쪽에서의 높이(px, 1920 기준)")
    p.add_argument("--words-per-line", type=int, default=2, help="자막 한 번에 표시할 단어 수")
    p.add_argument("--no-subs", action="store_true", help="자막 입히지 않기")
    p.add_argument("--layout", choices=["face", "center", "fit"], default="face",
                   help="face: 장면마다 인물 따라 크롭 / center: 가운데 크롭 / fit: 원본 전체 + 흐린 배경 (기본: face)")
    p.add_argument("--no-face", dest="layout", action="store_const", const="center", help="--layout center와 같음")
    p.add_argument("--no-title", action="store_true", help="fit 레이아웃에서 상단 제목 숨기기")
    p.add_argument("--reuse-clips", action="store_true",
                   help="이전에 고른 구간(clips.json)을 그대로 쓰고 다시 렌더링만 하기")
    p.add_argument("--dry-run", action="store_true", help="구간만 고르고 렌더링하지 않기")
    p.add_argument("--upload", action="store_true", help="추출 후 YouTube에 자동 업로드")
    add_upload_args(p)
    args = p.parse_args()

    if args.watch:
        watch(args.watch, args)
    elif args.source:
        process(args.source, args)
    else:
        p.error("영상 파일 또는 --watch 폴더를 지정하세요.")


if __name__ == "__main__":
    main()
