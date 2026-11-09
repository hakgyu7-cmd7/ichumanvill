"""브라우저(Playwright) UI 스모크 테스트 래퍼. node + playwright 가 없으면 건너뜀.
수동 실행: python tests/test_ui.py   (결과 스크린샷은 임시 폴더 또는 SHORTS_UI_OUT 에 저장)"""
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _node_env():
    if not (shutil.which("node") and shutil.which("ffmpeg")):
        return None
    env = dict(os.environ)
    try:
        root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True, timeout=20).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        root = ""
    env["NODE_PATH"] = root + os.pathsep + env.get("NODE_PATH", "")
    ok = subprocess.run(["node", "-e", "require('playwright')"], env=env, capture_output=True).returncode == 0
    return env if ok else None


ENV = _node_env()


@unittest.skipUnless(ENV, "node/playwright/ffmpeg 필요")
class UiSmoke(unittest.TestCase):
    def test_ui(self):
        import server
        from tests.test_modules import _copy_project
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            proj = td / "proj"
            proj.mkdir()
            _copy_project(proj)
            out = Path(os.environ.get("SHORTS_UI_OUT") or td / "out")
            out.mkdir(parents=True, exist_ok=True)
            clip, wav, png = td / "clip.mp4", td / "tts.wav", td / "ref.png"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=c=red:size=64x64", "-frames:v", "1", str(png)], check=True)
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=360x640:rate=24:duration=1.5", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(clip)], check=True)
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=330:duration=3", str(wav)], check=True)
            srv = server.make_server(0, proj)
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            try:
                url = f"http://127.0.0.1:{srv.server_address[1]}/"
                r = subprocess.run(["node", str(ROOT / "tests" / "ui_smoke.js"), url, (proj / "web_dashboard.html").as_uri(), str(clip), str(wav), str(out), str(png)],
                                   env=ENV, capture_output=True, text=True, encoding="utf-8", timeout=240)
                print(r.stdout)
                self.assertEqual(r.returncode, 0, r.stdout + "\n" + r.stderr)
            finally:
                srv.shutdown()
                srv.server_close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
