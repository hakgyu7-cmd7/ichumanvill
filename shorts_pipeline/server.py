#!/usr/bin/env python3
"""
server.py - 로컬 대시보드 서버 (표준 라이브러리만 사용, 127.0.0.1 전용)

  python server.py            # http://127.0.0.1:8765 열기 (브라우저 자동 실행)
  python server.py --check    # 환경 점검(파이썬/FFmpeg/폰트/선택 모듈) 후 종료

대시보드(web_dashboard.html)는 이 서버 없이도 열려서 대본/프롬프트/메타데이터 작업은 가능하지만,
트렌드 수집·떡상 탐색·자막 추출·클립 업로드·음성 처리·렌더링은 서버가 있어야 한다.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

import audio_tools
import prompt_engine as pe
import shorts_stitcher as st
import source_tools
from trend_crawler import TrendCrawler

BASE = Path(__file__).resolve().parent
STATIC = {"/": "web_dashboard.html", "/web_dashboard.html": "web_dashboard.html", "/pipeline_core.js": "pipeline_core.js", "/config.js": "config.js"}
MAX_JSON = 8 * 1024 * 1024
MAX_UPLOAD = 2 * 1024 * 1024 * 1024
NAME_RE = re.compile(r"^[\w가-힣\-. ]{1,60}$")
mimetypes.add_type("text/javascript", ".js")  # Windows 레지스트리가 .js 를 text/plain 으로 돌려주는 문제 방지
mimetypes.add_type("video/mp4", ".mp4")


class ApiError(Exception):
    def __init__(self, msg: str, code: int = 400):
        super().__init__(msg)
        self.code = code


class AppState:
    def __init__(self, base: Path = BASE):
        self.base = Path(base)
        self.input_dir = self.base / "input"
        self.output_dir = self.base / "output"
        self.assets_dir = self.base / "assets"
        self.projects_dir = self.base / "projects"
        for d in (self.input_dir, self.output_dir, self.projects_dir):
            d.mkdir(parents=True, exist_ok=True)
        self.cfg = pe.load_config(self.base / "config.json")
        self.lock = threading.Lock()
        self.job: Dict[str, Any] = {"state": "idle", "progress": 0.0, "log": [], "output": None, "error": None}

    # ----------------------------------------------------------- status
    def status(self) -> Dict[str, Any]:
        ff = None
        if shutil.which("ffmpeg"):
            r = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
            ff = (r.stdout.splitlines() or [""])[0]
        black, pre_b = st.find_font(self.assets_dir, "black")
        bold, pre_n = st.find_font(self.assets_dir, "bold")
        return {
            "python": sys.version.split()[0], "ffmpeg": ff, "ffprobe": bool(shutil.which("ffprobe")),
            "font_title": black.name if black else None, "font_sub": bold.name if bold else None, "pretendard": bool(pre_b and pre_n),
            "claude_cli": bool(shutil.which("claude")), "tools": source_tools.tool_status(),
            "edge_tts": _has_module("edge_tts"), "version": self.cfg["version"],
        }

    def files(self) -> Dict[str, Any]:
        pf = st.preflight(self.input_dir, self.assets_dir, self.cfg["spec"]["scenes"])
        clips = {}
        for i in range(1, self.cfg["spec"]["scenes"] + 1):
            p = st.find_clip(self.input_dir, i)
            clips[i] = {"name": p.name, "size": p.stat().st_size, "duration": audio_tools.probe_duration(p)} if p else None
        voice = st.find_voice(self.input_dir)
        raw = next((p for e in audio_tools.AUDIO_EXTS for p in [self.input_dir / f"voice_raw{e}"] if p.exists()), None)
        out = self.output_dir / "final_shorts.mp4"
        return {
            "clips": clips, "missing_clips": pf["missing_clips"],
            "voice": {"name": voice.name, "duration": audio_tools.probe_duration(voice)} if voice else None,
            "voice_raw": raw.name if raw else None,
            "final": {"name": out.name, "size": out.stat().st_size} if out.exists() else None,
            "ffmpeg": pf["ffmpeg"], "font": pf["font"], "pretendard": pf["pretendard"],
        }

    # ----------------------------------------------------------- render job
    def start_render(self, body: Dict[str, Any]) -> None:
        with self.lock:
            if self.job["state"] == "running":
                raise ApiError("이미 렌더링 중입니다.", 409)
            self.job = {"state": "running", "progress": 0.0, "log": [], "output": None, "error": None}
        project = pe.normalize_project(body.get("project") or {}, self.cfg)
        if body.get("fit") in ("cover", "contain"):
            project["render"]["fit"] = body["fit"]
        if body.get("crop"):
            project["render"]["crop_scale"] = float(body["crop"])

        def log(msg: str) -> None:
            self.job["log"].append(msg)

        def run() -> None:
            try:
                res = st.render(project, self.input_dir, self.output_dir, self.assets_dir, partial=bool(body.get("partial")), log=log,
                                on_progress=lambda p: self.job.__setitem__("progress", p), cfg=self.cfg)
                self.job.update(state="done", output="final_shorts.mp4", progress=1.0, duration=res.get("duration"))
            except Exception as e:  # noqa: BLE001 - 사용자에게 그대로 보여준다
                self.job.update(state="error", error=str(e))

        threading.Thread(target=run, daemon=True).start()


def _has_module(name: str) -> bool:
    try:
        __import__(name)
        return True
    except ImportError:
        return False


def _safe_name(name: str) -> str:
    if not NAME_RE.match(name or "") or name.startswith("."):
        raise ApiError("프로젝트 이름은 한글/영문/숫자/공백/-_. 만 60자까지 가능합니다.")
    return name


class Handler(BaseHTTPRequestHandler):
    server_version = "ShortsPipeline/3.0"
    app: AppState  # set by make_server

    def log_message(self, fmt: str, *args: Any) -> None:  # 조용히
        if os.environ.get("SHORTS_SERVER_LOG"):
            super().log_message(fmt, *args)

    # ----------------------------------------------------------- helpers
    def _guard(self) -> None:
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]").lower()
        if host not in ("127.0.0.1", "localhost", "::1"):
            raise ApiError("허용되지 않은 Host 입니다.", 403)
        origin = self.headers.get("Origin")
        if origin and self.command == "POST":
            o = urlparse(origin)
            if (o.hostname or "").lower() not in ("127.0.0.1", "localhost", "::1") or o.port != self.server.server_address[1]:
                raise ApiError("허용되지 않은 Origin 입니다.", 403)

    def _json(self, obj: Any, code: int = 200) -> None:
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _body(self) -> Dict[str, Any]:
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_JSON:
            raise ApiError("요청이 너무 큽니다.", 413)
        raw = self.rfile.read(n) if n else b"{}"
        try:
            v = json.loads(raw.decode("utf-8") or "{}")
        except ValueError as e:
            raise ApiError(f"JSON 형식 오류: {e}")
        return v if isinstance(v, dict) else {}

    def _file(self, path: Path, ctype: Optional[str] = None) -> None:
        if not path.exists() or not path.is_file():
            raise ApiError("파일이 없습니다.", 404)
        size = path.stat().st_size
        ctype = ctype or mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        start, end, code = 0, size - 1, 200
        rng = self.headers.get("Range")
        if rng:
            m = re.match(r"bytes=(\d*)-(\d*)", rng)
            if m and (m.group(1) or m.group(2)):
                if m.group(1):
                    start = int(m.group(1))
                    end = int(m.group(2)) if m.group(2) else size - 1
                else:
                    start = max(0, size - int(m.group(2)))
                end = min(end, size - 1)
                if start > end:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.end_headers()
                    return
                code = 206
        self.send_response(code)
        self.send_header("Content-Type", ctype + ("; charset=utf-8" if ctype.startswith(("text/", "application/javascript")) else ""))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Cache-Control", "no-store")
        if code == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        with open(path, "rb") as f:
            f.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = f.read(min(1 << 20, left))
                if not chunk:
                    break
                self.wfile.write(chunk)
                left -= len(chunk)

    # ----------------------------------------------------------- GET
    def do_GET(self) -> None:  # noqa: N802
        try:
            self._guard()
            u = urlparse(self.path)
            q = {k: v[0] for k, v in parse_qs(u.query).items()}
            app = self.app
            if u.path in STATIC:
                return self._file(app.base / STATIC[u.path])
            if u.path == "/api/config":
                return self._json(app.cfg)
            if u.path == "/api/status":
                return self._json(app.status())
            if u.path == "/api/files":
                return self._json(app.files())
            if u.path == "/api/trends":
                srcs = [s for s in (q.get("sources") or "coupang,tiktok,reddit").split(",") if s]
                return self._json(TrendCrawler.get_all_trends(srcs, live=q.get("live", "1") != "0", cat=q.get("cat", "history")))
            if u.path == "/api/render/status":
                return self._json(app.job)
            if u.path == "/api/projects":
                return self._json({"projects": sorted(p.stem for p in app.projects_dir.glob("*.json"))})
            if u.path == "/api/project":
                p = app.projects_dir / f"{_safe_name(q.get('name', ''))}.json"
                if not p.exists():
                    raise ApiError("프로젝트가 없습니다.", 404)
                return self._json(json.loads(p.read_text(encoding="utf-8")))
            m = re.fullmatch(r"/media/(input|output)/([\w.\-]+)", u.path)
            if m:
                d = app.input_dir if m.group(1) == "input" else app.output_dir
                name = m.group(2)
                if not re.fullmatch(r"(scene[_\d]*|voice[\w]*|final_shorts)\.(mp4|mov|webm|mkv|mp3|wav|m4a|aac|ogg|flac)", name):
                    raise ApiError("허용되지 않은 파일입니다.", 403)
                return self._file(d / name)
            raise ApiError("없는 경로입니다.", 404)
        except ApiError as e:
            self._json({"error": str(e)}, e.code)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:  # noqa: BLE001
            self._json({"error": f"서버 오류: {e}"}, 500)

    # ----------------------------------------------------------- POST
    def do_POST(self) -> None:  # noqa: N802
        try:
            self._guard()
            u = urlparse(self.path)
            q = {k: v[0] for k, v in parse_qs(u.query).items()}
            app = self.app
            if u.path == "/api/upload":
                return self._json(self._upload(q))
            b = self._body()
            if u.path == "/api/build-prompt":
                proj = pe.normalize_project(b.get("project") or {}, app.cfg)
                kind = b.get("kind", "master")
                if kind == "metadata":
                    return self._json({"prompt": pe.build_metadata_prompt(app.cfg, proj, b.get("languages") or ["ko"])})
                if kind == "package":
                    return self._json({"prompt": pe.all_prompts_text(app.cfg, proj)})
                return self._json({"prompt": pe.build_master_prompt(app.cfg, proj), "model": pe.recommended_model(app.cfg, proj)})
            if u.path == "/api/validate":
                proj = pe.normalize_project(b.get("project") or {}, app.cfg)
                return self._json({"issues": pe.validate_project(app.cfg, proj), "total": pe.total_units(proj, app.cfg)})
            if u.path == "/api/outliers":
                key = b.get("api_key") or os.environ.get("YOUTUBE_API_KEY", "")
                try:
                    res = source_tools.search_outliers(key, str(b.get("query", "")), int(b.get("days", 30)), float(b.get("min_ratio", 10)),
                                                       region=b.get("region") or None, language=b.get("language") or None)
                except source_tools.SourceError as e:
                    raise ApiError(str(e), 502)
                return self._json({"items": res})
            if u.path == "/api/transcript":
                try:
                    return self._json(source_tools.fetch_transcript(str(b.get("url", ""))))
                except source_tools.SourceError as e:
                    raise ApiError(str(e), 422)
            if u.path == "/api/render":
                app.start_render(b)
                return self._json({"started": True})
            if u.path == "/api/audio/process":
                raw = next((p for e in audio_tools.AUDIO_EXTS for p in [app.input_dir / f"voice_raw{e}"] if p.exists()), None)
                if not raw:
                    raise ApiError("input/voice_raw.* (TTS 원본 음성)가 없습니다. 먼저 업로드하세요.")
                try:
                    res = audio_tools.process_voice(raw, app.input_dir / "voice.mp3", float(b.get("speed", 1.2)), bool(b.get("remove_silence", True)),
                                                    float(b.get("threshold_db", -45)), float(b.get("min_silence", 0.15)))
                except audio_tools.AudioError as e:
                    raise ApiError(str(e), 500)
                return self._json({**res, **audio_tools.check_voice(app.input_dir / "voice.mp3", app.cfg["spec"]["total_seconds"])})
            if u.path == "/api/tts":
                lang = b.get("language", "ko")
                text = str(b.get("text", "")).strip()
                if not text:
                    raise ApiError("대본 텍스트가 비어 있습니다.")
                try:
                    audio_tools.synth_edge_tts(text, app.input_dir / "voice_raw.mp3", lang)
                except audio_tools.AudioError as e:
                    raise ApiError(str(e), 501)
                return self._json({"ok": True})
            if u.path == "/api/claude":
                exe = shutil.which("claude")
                if not exe:
                    raise ApiError("claude CLI 가 설치되어 있지 않습니다 (Claude Code 설치 후 사용 가능).", 501)
                cmd = [exe, "-p"]
                if b.get("model") and re.fullmatch(r"[\w.\-\[\]]{1,60}", str(b["model"])):
                    cmd += ["--model", str(b["model"])]
                try:
                    r = subprocess.run(cmd, input=str(b.get("prompt", "")), capture_output=True, text=True, encoding="utf-8", timeout=600)
                except subprocess.TimeoutExpired:
                    raise ApiError("claude CLI 응답 시간 초과(10분)", 504)
                if r.returncode != 0:
                    raise ApiError("claude CLI 오류: " + (r.stderr or r.stdout)[-400:], 502)
                return self._json({"text": r.stdout})
            if u.path == "/api/project":
                name = _safe_name(str(b.get("name", "")))
                (app.projects_dir / f"{name}.json").write_text(json.dumps(b.get("project") or {}, ensure_ascii=False, indent=2), encoding="utf-8")
                return self._json({"saved": name})
            if u.path == "/api/delete-file":
                return self._json(self._delete(b))
            raise ApiError("없는 경로입니다.", 404)
        except ApiError as e:
            self._json({"error": str(e)}, e.code)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:  # noqa: BLE001
            self._json({"error": f"서버 오류: {e}"}, 500)

    # ----------------------------------------------------------- upload / delete
    def _upload(self, q: Dict[str, str]) -> Dict[str, Any]:
        app = self.app
        kind = q.get("kind", "")
        ext = Path(q.get("name", "")).suffix.lower()
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0 or n > MAX_UPLOAD:
            raise ApiError("파일 크기가 올바르지 않습니다 (최대 2GB).", 413)
        if kind == "clip":
            scene = int(q.get("scene", "0"))
            if not 1 <= scene <= app.cfg["spec"]["scenes"] or ext not in st.VIDEO_EXTS:
                raise ApiError("씬 번호(1~6)와 영상 확장자(mp4/mov/webm/mkv)를 확인하세요.")
            for e in st.VIDEO_EXTS:  # 기존 파일(다른 확장자/이름) 정리
                for stem in (f"scene{scene}", f"scene_{scene:02d}", f"scene{scene:02d}", f"scene_{scene}"):
                    (app.input_dir / f"{stem}{e}").unlink(missing_ok=True)
            dest = app.input_dir / f"scene{scene}{ext}"
        elif kind in ("voice", "voice_raw"):
            if ext not in audio_tools.AUDIO_EXTS:
                raise ApiError("음성 확장자(mp3/wav/m4a/aac/ogg/flac)를 확인하세요.")
            for e in audio_tools.AUDIO_EXTS:
                (app.input_dir / f"{kind}{e}").unlink(missing_ok=True)
            dest = app.input_dir / f"{kind}{ext}"
        else:
            raise ApiError("kind 는 clip / voice / voice_raw 중 하나여야 합니다.")
        tmp = dest.with_suffix(dest.suffix + ".part")
        left = n
        with open(tmp, "wb") as f:
            while left > 0:
                chunk = self.rfile.read(min(1 << 20, left))
                if not chunk:
                    break
                f.write(chunk)
                left -= len(chunk)
        if left:
            tmp.unlink(missing_ok=True)
            raise ApiError("업로드가 중간에 끊겼습니다.")
        tmp.replace(dest)
        return {"saved": dest.name, "size": n}

    def _delete(self, b: Dict[str, Any]) -> Dict[str, Any]:
        app = self.app
        kind = b.get("kind")
        removed = []
        if kind == "clip":
            s = int(b.get("scene", 0))
            for e in st.VIDEO_EXTS:
                for stem in (f"scene{s}", f"scene_{s:02d}", f"scene{s:02d}", f"scene_{s}"):
                    p = app.input_dir / f"{stem}{e}"
                    if p.exists():
                        p.unlink()
                        removed.append(p.name)
        elif kind in ("voice", "voice_raw"):
            for e in audio_tools.AUDIO_EXTS:
                p = app.input_dir / f"{kind}{e}"
                if p.exists():
                    p.unlink()
                    removed.append(p.name)
        else:
            raise ApiError("kind 는 clip / voice / voice_raw")
        return {"removed": removed}


def make_server(port: int = 8765, base: Path = BASE, host: str = "127.0.0.1") -> ThreadingHTTPServer:
    app = AppState(base)
    handler = type("BoundHandler", (Handler,), {"app": app})
    srv = ThreadingHTTPServer((host, port), handler)
    srv.app = app  # type: ignore[attr-defined]
    return srv


def environment_check() -> int:
    ok = True

    def line(flag: Optional[bool], text: str, hint: str = "") -> None:
        nonlocal ok
        mark = "[OK]  " if flag else ("[필요]" if flag is False else "[선택]")
        if flag is False:
            ok = False
        print(f"{mark} {text}" + (f"   -> {hint}" if hint and not flag else ""))

    app = AppState(BASE)
    s = app.status()
    line(sys.version_info >= (3, 9), f"Python {s['python']}", "Python 3.9 이상 필요 (python.org, 'Add python.exe to PATH' 체크)")
    line(bool(s["ffmpeg"]), s["ffmpeg"] or "FFmpeg", "winget install Gyan.FFmpeg  후 새 터미널에서 ffmpeg -version 확인")
    line(s["ffprobe"], "ffprobe", "FFmpeg 와 함께 설치됨")
    line(bool(s["font_title"]), f"한글 폰트: {s['font_title'] or '없음'}", "assets/ 에 Pretendard-Black.ttf, Pretendard-Bold.ttf 넣기")
    line(None if s["pretendard"] else None, "Pretendard 폰트 " + ("있음" if s["pretendard"] else "없음(대체 폰트 사용)"))
    t = s["tools"]
    line(None, f"YOUTUBE_API_KEY {'설정됨' if t['youtube_api_key'] else '없음(떡상 탐색 시 대시보드에 입력 가능)'}")
    line(None, f"youtube-transcript-api {'설치됨' if t['youtube_transcript_api'] else '없음(pip install youtube-transcript-api)'}")
    line(None, f"yt-dlp {'설치됨' if t['yt_dlp'] else '없음(pip install yt-dlp)'}")
    line(None, f"faster-whisper {'설치됨' if t['faster_whisper'] else '없음(자막 없는 영상 음성인식용, 선택)'}")
    line(None, f"claude CLI {'있음' if s['claude_cli'] else '없음(대시보드에서 직접 복사/붙여넣기 방식 사용)'}")
    print("\n필수 항목이 모두 [OK]면 준비 완료입니다." if ok else "\n[필요] 항목을 먼저 해결해 주세요.")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="AI 쇼츠 파이프라인 로컬 서버")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--check", action="store_true", help="환경 점검만 하고 종료")
    a = ap.parse_args()
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if a.check:
        return environment_check()
    srv = None
    for port in range(a.port, a.port + 10):
        try:
            srv = make_server(port)
            break
        except OSError:
            continue
    if srv is None:
        print("사용 가능한 포트를 찾지 못했습니다.", file=sys.stderr)
        return 1
    url = f"http://127.0.0.1:{srv.server_address[1]}/"
    print(f"AI Shorts Pipeline Studio -> {url}   (종료: Ctrl+C)")
    if not a.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n종료합니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
