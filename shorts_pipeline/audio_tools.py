#!/usr/bin/env python3
"""
audio_tools.py - 4단계 "음성" 도구

  process_voice : 원본 TTS 음성 -> 무음(숨소리) 제거 + 1.2배속 -> voice.mp3  (ffmpeg 필요)
  probe_duration: 길이(초) 확인 (45초 규격 점검)
  synth_edge_tts: (선택) edge-tts 로 대본에서 바로 음성 생성 - pip install edge-tts (네트워크 필요, 로컬 TTS 대안)

Pinokio Qwen3-TTS 같은 로컬 TTS 는 각자 UI 에서 음성을 만든 뒤 input/voice_raw.* 로 저장하면 된다.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Dict, List, Optional

AUDIO_EXTS = (".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac")
EDGE_VOICES = {"ko": "ko-KR-SunHiNeural", "en": "en-US-AriaNeural", "ja": "ja-JP-NanamiNeural", "zh": "zh-TW-HsiaoChenNeural"}


class AudioError(RuntimeError):
    pass


def have_ffmpeg() -> bool:
    return bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def probe_duration(path: Path) -> Optional[float]:
    if not shutil.which("ffprobe") or not Path(path).exists():
        return None
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
                       capture_output=True, text=True)
    try:
        return float(json.loads(r.stdout)["format"]["duration"])
    except (ValueError, KeyError, json.JSONDecodeError):
        return None


def _encoders() -> str:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True)
    return r.stdout


def build_filter(speed: float = 1.2, remove_silence: bool = True, threshold_db: float = -45.0, min_silence: float = 0.15) -> str:
    parts: List[str] = []
    if remove_silence:
        # 앞쪽 무음 제거 + 중간의 min_silence 이상 무음 구간 전부 제거
        parts.append(f"silenceremove=start_periods=1:start_duration=0:start_threshold={threshold_db}dB:"
                     f"stop_periods=-1:stop_duration={min_silence}:stop_threshold={threshold_db}dB")
    if abs(speed - 1.0) > 1e-3:
        s = speed
        while s > 2.0:  # atempo 는 0.5~2.0 범위
            parts.append("atempo=2.0")
            s /= 2.0
        parts.append(f"atempo={s:g}")
    return ",".join(parts) if parts else "anull"


def _run(cmd: List[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise AudioError("ffmpeg 오류: " + r.stderr.strip()[-400:])


def process_voice(src: Path, dst: Path, speed: float = 1.2, remove_silence: bool = True,
                  threshold_db: float = -45.0, min_silence: float = 0.15,
                  fit_seconds: Optional[float] = None) -> Dict[str, Optional[float]]:
    """원본 음성 -> (무음 제거) -> 속도 변경 -> dst.
    fit_seconds 를 주면 무음 제거 후 길이를 측정해 정확히 그 길이가 되도록 속도를 자동 계산한다(0.5~2.0배 범위로 제한)."""
    if not have_ffmpeg():
        raise AudioError("ffmpeg/ffprobe 가 설치되어 있지 않습니다 (winget install Gyan.FFmpeg).")
    src, dst = Path(src), Path(dst)
    if not src.exists():
        raise AudioError(f"원본 음성이 없습니다: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    before = probe_duration(src)
    base_len, clamped, speed_used = before, False, speed
    if fit_seconds:
        if fit_seconds <= 0:
            raise AudioError("목표 길이는 0보다 커야 합니다.")
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "base.wav"
            _run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vn", "-af", build_filter(1.0, remove_silence, threshold_db, min_silence), str(tmp)])
            base_len = probe_duration(tmp)
        if not base_len:
            raise AudioError("음성 길이를 읽을 수 없습니다.")
        want = base_len / fit_seconds
        speed_used = max(0.5, min(2.0, want))
        clamped = abs(speed_used - want) > 1e-6
    enc = _encoders()
    if dst.suffix.lower() == ".mp3" and "libmp3lame" in enc:
        codec = ["-c:a", "libmp3lame", "-q:a", "2"]
    elif dst.suffix.lower() == ".mp3":
        raise AudioError("이 ffmpeg 에는 mp3 인코더가 없습니다. 출력 확장자를 .m4a 로 바꾸세요.")
    else:
        codec = ["-c:a", "aac", "-b:a", "192k"]
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vn", "-af", build_filter(speed_used, remove_silence, threshold_db, min_silence), *codec, str(dst)])
    return {"before": before, "after": probe_duration(dst), "speed": round(speed_used, 3), "base_len": base_len, "fit_clamped": clamped}


def check_voice(path: Path, target: float = 45.0, tolerance: float = 3.0) -> Dict[str, object]:
    d = probe_duration(path)
    if d is None:
        return {"ok": False, "duration": None, "msg": "길이를 읽을 수 없습니다"}
    ok = abs(d - target) <= tolerance
    return {"ok": ok, "duration": round(d, 2), "msg": f"{d:.1f}초 (목표 {target:g}±{tolerance:g}초)" + ("" if ok else " - 대본 글자수 또는 속도를 점검하세요")}


def synth_edge_tts(text: str, out: Path, lang: str = "ko", voice: Optional[str] = None, rate: str = "+20%") -> Path:
    """edge-tts 로 음성 생성 (rate +20% = 1.2배속). 미검증 선택 기능: pip install edge-tts, 인터넷 필요."""
    try:
        import asyncio
        import edge_tts  # type: ignore
    except ImportError as e:
        raise AudioError("edge-tts 가 필요합니다: pip install edge-tts") from e

    async def run() -> None:
        await edge_tts.Communicate(text, voice or EDGE_VOICES.get(lang, EDGE_VOICES["ko"]), rate=rate).save(str(out))
    try:
        asyncio.run(run())
    except Exception as e:  # 네트워크/서비스 오류
        raise AudioError(f"edge-tts 실패: {e}") from e
    return Path(out)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="TTS 음성 -> 무음 제거 + 1.2배속")
    ap.add_argument("src"); ap.add_argument("dst", nargs="?", default="input/voice.mp3")
    ap.add_argument("--speed", type=float, default=1.2); ap.add_argument("--keep-silence", action="store_true")
    ap.add_argument("--fit", type=float, help="목표 길이(초)에 맞춰 속도 자동 계산 (예: --fit 45)")
    a = ap.parse_args()
    res = process_voice(Path(a.src), Path(a.dst), a.speed, not a.keep_silence, fit_seconds=a.fit)
    print(res, check_voice(Path(a.dst))["msg"])
