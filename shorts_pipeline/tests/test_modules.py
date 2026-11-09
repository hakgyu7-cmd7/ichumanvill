"""스티처 / 오디오 / 소스 도구 / 크롤러 / 서버 테스트 (네트워크 호출 없음).
실행: python -m unittest discover -s tests -v
"""
import http.client
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import audio_tools  # noqa: E402
import prompt_engine as pe  # noqa: E402
import shorts_stitcher as st  # noqa: E402
import source_tools  # noqa: E402
import trend_crawler  # noqa: E402

CFG = pe.load_config()
RAMEN = pe.normalize_project(json.loads((ROOT / "samples" / "ramen_bgrade.json").read_text(encoding="utf-8")), CFG)
HAVE_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def make_clip(path, seconds=1.5, size="360x640"):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=size={size}:rate=24:duration={seconds}",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path)], check=True)


class StitcherUnit(unittest.TestCase):
    def test_wrap_text(self):
        self.assertEqual(st.wrap_text("짧은 문장", 18), "짧은 문장")
        w = st.wrap_text("라면 끓일 때마다 물 맞추기 실패한다면", 18)
        self.assertEqual(w, "라면 끓일 때마다 물 맞추기\n실패한다면")
        self.assertTrue(all(len(x) <= 18 for x in w.split("\n")))
        self.assertEqual(st.wrap_text("あ" * 25, 10).split("\n"), ["あ" * 10, "あ" * 10, "あ" * 5])  # 공백 없는 문장 강제 분할
        self.assertEqual(st.wrap_text("", 10), "")

    def test_ff_escape_windows_and_quotes(self):
        self.assertEqual(st.ff_escape("C:\\Windows\\Fonts\\malgun.ttf"), "C\\:/Windows/Fonts/malgun.ttf")
        self.assertEqual(st.ff_escape("a'b"), "a\\'b")

    def test_timeline_uses_real_clip_length(self):
        scenes = RAMEN["scenes"][:2]
        ev = st.build_timeline(scenes, [7.5, 6.0], 18)
        self.assertEqual(len(ev), 6)
        self.assertEqual((ev[0][0], ev[0][1]), (0.0, 2.5))
        self.assertEqual((ev[3][0], ev[3][1]), (7.5, 9.5))  # 두 번째 클립(6초)을 3등분
        self.assertAlmostEqual(ev[5][1], 13.5)
        scenes2 = [dict(scenes[0], beats=["a", "", "c"])]
        self.assertEqual(len(st.build_timeline(scenes2, [7.5], 18)), 2)  # 빈 비트는 건너뜀

    def _cmd(self, project, n=6, voice=True, durations=None):
        clips = [Path(f"/x/scene{i}.mp4") for i in range(1, n + 1)]
        d = durations or [7.5] * n
        proj = dict(project, scenes=project["scenes"][:n])
        return st.build_command(clips, Path("/x/voice.mp3") if voice else None, proj, CFG, d, Path("/f/a.ttf"), Path("/f/b.ttf"), Path("/o/out.mp4"))

    def test_command_structure(self):
        cmd, files = self._cmd(RAMEN)
        fc = cmd[cmd.index("-filter_complex") + 1]
        self.assertIn("concat=n=6:v=1:a=0[cat]", fc)
        self.assertIn("pad=1080:1920:0:240:color=0x000000", fc)  # 상단 240px
        self.assertIn("scale=w=1145:h=1357:force_original_aspect_ratio=increase,crop=1080:1280", fc)  # 1.06x cover
        self.assertEqual(fc.count("drawtext="), len(files))
        self.assertIn("gte(t,0.0)*lt(t,2.5)", fc)
        self.assertIn("gte(t,42.5)*lt(t,45.0)", fc)
        self.assertIn("y=1500-14-", fc)  # 하단 바 바로 위 정렬
        self.assertIn("-map", cmd)
        self.assertIn("6:a", cmd)       # 음성은 7번째 입력
        self.assertEqual(cmd[cmd.index("-t") + 1], "45.000")
        self.assertTrue(all(len(c.split("\n")) == 1 for c in files.values()))  # 줄마다 별도 파일 (줄별 중앙정렬)

    def test_custom_letterbox_title_and_subtitle_style(self):
        p = json.loads(json.dumps(RAMEN))
        p["render"].update({"top_bar": 300, "bottom_bar": 200, "bar_color": "#112233", "title_size": 80, "title_color": "00ff00", "title_outline": 0,
                            "title_y": -20, "sub_size": 40, "sub_color": "#FFFF00", "sub_outline": 3, "sub_outline_color": "FF0000", "sub_box": False,
                            "sub_gap": 4})
        cmd, files = self._cmd(p)
        fc = cmd[cmd.index("-filter_complex") + 1]
        self.assertIn("scale=w=1145:h=1505:force_original_aspect_ratio=increase,crop=1080:1420", fc)   # 영상 높이 = 1920-300-200 = 1420
        self.assertIn("pad=1080:1920:0:300:color=0x112233", fc)
        self.assertIn("fontsize=80:fontcolor=0x00FF00:", fc)
        self.assertIn("y=(300-(2*text_h+1*8))/2+0*(text_h+8)+-20", fc)
        self.assertNotIn("bordercolor=0x000000:x=(w-text_w)/2:y=(300", fc)                         # 타이틀 외곽선 0 -> 없음
        self.assertIn("fontsize=40:fontcolor=0xFFFF00:borderw=3:bordercolor=0xFF0000:x=(w-text_w)/2:y=1700-0-", fc)  # 자막 하단 = 1920-200-20, 박스 없음 -> 패딩 0
        self.assertNotIn("box=1", fc)

    def test_subtitle_bottom_manual_and_box_options(self):
        p = json.loads(json.dumps(RAMEN))
        p["render"].update({"sub_bottom": 1400, "sub_box_color": "202020", "sub_box_alpha": 0.5, "sub_box_border": 20})
        fc = self._cmd(p)[0][self._cmd(p)[0].index("-filter_complex") + 1]
        self.assertIn("boxcolor=0x202020@0.5:boxborderw=20:", fc)
        self.assertIn("y=1400-20-", fc)

    def test_render_settings_validation_and_fallbacks(self):
        p = json.loads(json.dumps(RAMEN))
        p["render"].update({"top_bar": 900, "bottom_bar": 900})
        with self.assertRaises(st.StitchError) as cm:
            st.render_settings(CFG, p)
        self.assertIn("영상 높이", str(cm.exception))
        q = json.loads(json.dumps(RAMEN))
        q["render"].update({"title_color": "not-a-color", "sub_size": "abc", "bar_color": None, "sub_box_alpha": 9, "crop_scale": 5})
        S = st.render_settings(CFG, q)
        self.assertEqual((S["title_color"], S["sub_size"], S["bar"], S["sub_box_alpha"], S["zoom"]), ("FFE500", 52, "000000", 1.0, 1.5))
        self.assertEqual((S["top"], S["bottom"], S["video_h"], S["sub_bottom"]), (240, 400, 1280, 1500))
        q["render"]["bottom_bar"] = 100
        self.assertEqual(st.render_settings(CFG, q)["sub_bottom"], 1800)                           # 자동 위치는 하단 바 변경을 따라감

    def test_font_resolution_and_listing(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / "MyFont.ttf").write_bytes(b"x")
            (td / "readme.txt").write_text("x")
            f, pre = st.resolve_font("assets:MyFont.ttf", td, "bold")
            self.assertEqual((f.name, pre), ("MyFont.ttf", False))
            f2, _ = st.resolve_font("assets:../../etc/passwd", td, "bold")                       # 경로 탈출 시도는 자동 선택으로 대체
            self.assertNotEqual(f2.name if f2 else None, "passwd")
            f3, _ = st.resolve_font("assets:Missing.ttf", td, "bold")
            self.assertEqual(f3.name if f3 else None, "MyFont.ttf")                               # 없으면 assets 안의 다른 폰트로 대체
            lst = st.list_fonts(td)
            self.assertEqual(lst[0], {"spec": "assets:MyFont.ttf", "name": "MyFont", "group": "assets"})
            self.assertTrue(all(x["group"] in ("assets", "system") for x in lst))
            self.assertNotIn("readme", [x["name"] for x in lst])
            self.assertIsNone(st.find_system_font("definitely-not-a-font-xyz.ttf"))

    def test_command_contain_and_no_voice(self):
        p = json.loads(json.dumps(RAMEN))
        p["render"]["fit"] = "contain"
        cmd, _ = self._cmd(p, voice=False)
        fc = cmd[cmd.index("-filter_complex") + 1]
        self.assertIn("pad=1080:1280:(ow-iw)/2:(oh-ih)/2:color=black", fc)
        self.assertNotIn("-af", cmd)

    def test_text_goes_through_textfile_not_inline(self):
        p = json.loads(json.dumps(RAMEN))
        p["scenes"][0]["beats"][0] = "따옴표 ' 와 콜론 : 그리고 100% 테스트"
        cmd, files = self._cmd(p)
        fc = cmd[cmd.index("-filter_complex") + 1]
        self.assertNotIn("따옴표", fc)
        self.assertTrue(any("따옴표" in v for v in files.values()))
        self.assertIn("expansion=none", fc)

    def test_font_fallback_order(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(st.find_font(Path(td), "bold")[1], False)
            (Path(td) / "Pretendard-Bold.ttf").write_bytes(b"x")
            f, pre = st.find_font(Path(td), "bold")
            self.assertEqual((f.name, pre), ("Pretendard-Bold.ttf", True))
            f2, pre2 = st.find_font(Path(td), "black")  # Black 없으면 Bold 로 대체
            self.assertEqual((f2.name, pre2), ("Pretendard-Bold.ttf", True))

    def test_clip_name_variants(self):
        with tempfile.TemporaryDirectory() as td:
            for n in ("scene_01.mp4", "scene2.mov", "scene03.webm"):
                (Path(td) / n).write_bytes(b"x")
            self.assertEqual([bool(st.find_clip(Path(td), i)) for i in range(1, 6)], [True, True, True, False, False])


@unittest.skipUnless(HAVE_FFMPEG, "ffmpeg 없음")
class StitcherRender(unittest.TestCase):
    def test_partial_render_end_to_end(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            inp, out = td / "in", td / "out"
            inp.mkdir()
            make_clip(inp / "scene1.mp4")
            make_clip(inp / "scene_02.mp4", 1.5, "640x360")  # 가로 영상도 처리되어야 함
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=6", str(inp / "voice.mp3")], check=True)
            logs = []
            res = st.render(RAMEN, inp, out, ROOT / "assets", partial=True, log=logs.append)
            r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height,codec_type", "-of", "json", res["output"]], capture_output=True, text=True)
            streams = json.loads(r.stdout)["streams"]
            v = next(s for s in streams if s["codec_type"] == "video")
            self.assertEqual((v["width"], v["height"]), (1080, 1920))
            self.assertTrue(any(s["codec_type"] == "audio" for s in streams))
            self.assertAlmostEqual(res["duration"], 3.0, delta=0.15)  # 음성(6초)이 길어도 영상 길이에 맞춰짐
            self.assertTrue(any("음성" in l and "경고" in l for l in logs))
            self.assertFalse((st.BASE / "output" / "_tmp").exists(), "임시 텍스트 파일이 정리되어야 함")

    def test_custom_style_render_end_to_end(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            inp = td / "in"
            inp.mkdir()
            make_clip(inp / "scene1.mp4")
            p = json.loads(json.dumps(RAMEN))
            p["render"].update({"top_bar": 300, "bottom_bar": 300, "bar_color": "301020", "sub_box": False, "sub_outline": 2, "title_color": "00FFAA"})
            res = st.render(p, inp, td / "out", ROOT / "assets", partial=True, log=lambda m: None)
            r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", res["output"]], capture_output=True, text=True)
            v = json.loads(r.stdout)["streams"][0]
            self.assertEqual((v["width"], v["height"]), (1080, 1920))
            frame = td / "f.png"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", "0.3", "-i", res["output"], "-frames:v", "1", "-vf", "crop=4:4:500:20,scale=1:1", "-pix_fmt", "rgb24", "-f", "rawvideo", str(frame)], check=True)
            got = list(frame.read_bytes())[:3]                                                       # 상단 바 색(301020)이 실제로 칠해짐 (YUV 변환 오차 허용)
            self.assertTrue(all(abs(g - w) <= 3 for g, w in zip(got, [0x30, 0x10, 0x20])), got)

    def test_missing_clips_error_lists_scenes(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(st.StitchError) as cm:
                st.render(RAMEN, Path(td), Path(td) / "o", ROOT / "assets")
            self.assertIn("scene1.mp4", str(cm.exception))
            self.assertIn("scene6.mp4", str(cm.exception))

    def test_dry_run_without_clips_shows_command(self):
        with tempfile.TemporaryDirectory() as td:
            logs = []
            res = st.render(RAMEN, Path(td), Path(td) / "o", ROOT / "assets", dry_run=True, log=logs.append)
            self.assertEqual(res["duration"], 45.0)
            self.assertEqual(len(res["clips"]), 6)
            self.assertTrue(any("자리표시" in l for l in logs))
            self.assertIn("concat=n=6", " ".join(res["command"]))

    def test_dry_run(self):
        with tempfile.TemporaryDirectory() as td:
            for i in range(1, 7):
                (Path(td) / f"scene{i}.mp4").write_bytes(b"x")
            with mock.patch.object(st, "probe_duration", return_value=7.5):
                res = st.render(RAMEN, Path(td), Path(td) / "o", ROOT / "assets", dry_run=True)
            self.assertTrue(res["dry_run"])
            self.assertEqual(res["duration"], 45.0)


@unittest.skipUnless(HAVE_FFMPEG, "ffmpeg 없음")
class AudioTests(unittest.TestCase):
    def test_filter_string(self):
        f = audio_tools.build_filter(1.2, True)
        self.assertIn("silenceremove", f)
        self.assertIn("atempo=1.2", f)
        self.assertEqual(audio_tools.build_filter(1.0, False), "anull")
        self.assertIn("atempo=2.0,atempo=", audio_tools.build_filter(3.0, False))

    def test_silence_removed_and_sped_up(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=1", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono:d=1",
                            "-f", "lavfi", "-i", "sine=frequency=440:duration=1", "-filter_complex", "[0][1][2]concat=n=3:v=0:a=1", str(td / "raw.wav")], check=True)
            res = audio_tools.process_voice(td / "raw.wav", td / "voice.mp3")
            self.assertAlmostEqual(res["before"], 3.0, delta=0.1)
            self.assertAlmostEqual(res["after"], 2.0 / 1.2, delta=0.2)  # 무음 1초 제거 + 1.2배속
            self.assertEqual(audio_tools.check_voice(td / "voice.mp3", 45)["ok"], False)

    def _gap_wav(self, td):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=1", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono:d=1",
                        "-f", "lavfi", "-i", "sine=frequency=440:duration=1", "-filter_complex", "[0][1][2]concat=n=3:v=0:a=1", str(td / "raw.wav")], check=True)
        return td / "raw.wav"

    def test_settings_actually_change_the_result(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            raw = self._gap_wav(td)
            a = audio_tools.process_voice(raw, td / "a.mp3", speed=1.0, remove_silence=False)
            b = audio_tools.process_voice(raw, td / "b.mp3", speed=1.0, remove_silence=True)
            c = audio_tools.process_voice(raw, td / "c.mp3", speed=2.0, remove_silence=True)
            d = audio_tools.process_voice(raw, td / "d.mp3", speed=0.8, remove_silence=True)
            e = audio_tools.process_voice(raw, td / "e.mp3", speed=1.0, remove_silence=True, min_silence=0.02)
            self.assertAlmostEqual(a["after"], 3.0, delta=0.15)       # 무음 유지 + 원속도
            self.assertTrue(2.0 <= b["after"] <= 2.35, b)             # 무음 제거(문장 사이 min_silence 만큼은 남김)
            self.assertAlmostEqual(c["after"], b["after"] / 2, delta=0.12)    # 2배속
            self.assertAlmostEqual(d["after"], b["after"] / 0.8, delta=0.15)  # 0.8배속(느리게)
            self.assertLess(e["after"], b["after"])                   # min_silence 를 줄이면 더 짧아짐

    def test_fit_seconds_picks_speed_automatically(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            raw = self._gap_wav(td)
            r = audio_tools.process_voice(raw, td / "f.mp3", remove_silence=True, fit_seconds=4.0)
            self.assertAlmostEqual(r["speed"], r["base_len"] / 4.0, places=2)     # 무음 제거 후 길이 / 목표 길이
            self.assertAlmostEqual(r["after"], 4.0, delta=0.25)
            self.assertFalse(r["fit_clamped"])
            r2 = audio_tools.process_voice(raw, td / "g.mp3", remove_silence=True, fit_seconds=1.0)   # 2배속 초과 필요 -> 2.0 으로 제한
            self.assertEqual((r2["speed"], r2["fit_clamped"]), (2.0, True))
            r3 = audio_tools.process_voice(raw, td / "h.mp3", remove_silence=True, fit_seconds=0.5)
            self.assertEqual((r3["speed"], r3["fit_clamped"]), (2.0, True))
            r4 = audio_tools.process_voice(raw, td / "i.mp3", remove_silence=False, fit_seconds=6.0)  # 무음 유지 3.0초 -> 6초 = 0.5배속
            self.assertAlmostEqual(r4["speed"], 0.5, places=2)
            self.assertFalse(r4["fit_clamped"])
            with self.assertRaises(audio_tools.AudioError):
                audio_tools.process_voice(raw, td / "j.mp3", fit_seconds=-1)

    def test_missing_source(self):
        with self.assertRaises(audio_tools.AudioError):
            audio_tools.process_voice(Path("/nope.wav"), Path("/tmp/x.mp3"))


class SourceToolTests(unittest.TestCase):
    def test_extract_video_id(self):
        cases = {
            "https://www.youtube.com/shorts/JNcjKUSolis?si=abc": "JNcjKUSolis", "https://youtu.be/aadVpZdFiK8?si=x": "aadVpZdFiK8",
            "https://www.youtube.com/watch?v=KR3t_vMePn8&t=3": "KR3t_vMePn8", "https://m.youtube.com/watch?v=KR3t_vMePn8": "KR3t_vMePn8",
            "KR3t_vMePn8": "KR3t_vMePn8", "https://example.com/watch?v=KR3t_vMePn8": None, "garbage": None, "": None,
        }
        for url, vid in cases.items():
            self.assertEqual(source_tools.extract_video_id(url), vid, url)

    def test_ratio(self):
        self.assertEqual(source_tools.vs_ratio(5_200_000, 200_000), 26.0)
        self.assertIsNone(source_tools.vs_ratio(100, 0))
        g = lambda r: source_tools.classify_ratio(r)["grade"]  # noqa: E731
        self.assertEqual([g(0.5), g(2), g(7), g(10), g(None)], ["normal", "ok", "good", "viral", "unknown"])
        self.assertEqual(source_tools.parse_iso_duration("PT1M5S"), 65)

    def test_vtt_parse_dedupes_auto_captions(self):
        vtt = """WEBVTT
Kind: captions
Language: ko

00:00:00.000 --> 00:00:02.000
안녕하세요 <c>여러분</c>

00:00:02.000 --> 00:00:04.000
안녕하세요 여러분
오늘은 라면을 끓입니다

00:00:04.000 --> 00:00:06.000
오늘은 라면을 끓입니다
&amp; 시작합니다
"""
        self.assertEqual(source_tools.parse_vtt(vtt), "안녕하세요 여러분 오늘은 라면을 끓입니다 & 시작합니다")

    def test_search_outliers_with_mock(self):
        def fetch(url):
            if "/search?" in url:
                self.assertIn("videoDuration=short", url)
                self.assertIn("publishedAfter=", url)
                return {"items": [{"id": {"videoId": v}} for v in ("a", "b", "c", "d")]}
            if "/videos?" in url:
                mk = lambda i, ch, views, dur: {"id": i, "snippet": {"channelId": ch, "title": "t" + i, "channelTitle": ch, "publishedAt": "x", "thumbnails": {}},  # noqa: E731
                                                "contentDetails": {"duration": dur}, "statistics": {"viewCount": str(views)}}
                return {"items": [mk("a", "c1", 5_000_000, "PT30S"), mk("b", "c2", 300_000, "PT20S"), mk("c", "c3", 9_000_000, "PT10M"), mk("d", "c4", 900_000, "PT45S")]}
            if "/channels?" in url:
                return {"items": [{"id": "c1", "statistics": {"subscriberCount": "100000"}}, {"id": "c2", "statistics": {"subscriberCount": "1000000"}},
                                  {"id": "c3", "statistics": {"subscriberCount": "1000"}}, {"id": "c4", "statistics": {"hiddenSubscriberCount": True}}]}
            raise AssertionError(url)
        res = source_tools.search_outliers("KEY", "kitchen", days=30, min_ratio=10, fetch=fetch)
        self.assertEqual([r["video_id"] for r in res], ["a"])       # b: 0.3배, c: 10분(쇼츠 아님), d: 구독자 비공개
        self.assertEqual(res[0]["ratio"], 50.0)
        self.assertEqual(res[0]["grade"], "viral")
        self.assertEqual([r["video_id"] for r in source_tools.search_outliers("KEY", "k", min_ratio=0.1, fetch=fetch)], ["a", "b"])

    def test_outliers_input_validation(self):
        with self.assertRaises(source_tools.SourceError):
            source_tools.search_outliers("", "x")
        with self.assertRaises(source_tools.SourceError):
            source_tools.search_outliers("k", "  ")

    def test_transcript_bad_url(self):
        with self.assertRaises(source_tools.SourceError):
            source_tools.fetch_transcript("https://example.com/video")


class CrawlerTests(unittest.TestCase):
    def test_seed_fallback_is_marked_sample(self):
        r = trend_crawler.TrendCrawler.get_all_trends(["coupang", "tiktok", "reddit"], live=False)
        self.assertTrue(r["items"])
        self.assertTrue(all(it["live"] is False and it["sample"] for it in r["items"]))
        self.assertTrue(all(v["live"] is False for v in r["status"].values()))
        self.assertTrue(r["manual_links"])

    def test_coupang_blocked_returns_sample_with_reason(self):
        import urllib.error

        def blocked(url):
            raise urllib.error.HTTPError(url, 403, "Forbidden", {}, None)
        r = trend_crawler.TrendCrawler.get_coupang_best(live=True, fetch=blocked)
        self.assertFalse(r["live"])
        self.assertIn("403", r["note"])
        self.assertTrue(r["items"] and all(not i["live"] for i in r["items"]))

    def test_coupang_parse_and_live_flag(self):
        page = '<ul><li><div class="name">  접이식 캠핑 의자 초경량  </div></li><li><div class="name">접이식 캠핑 의자 초경량</div></li><li><div class="title">원터치 진공 밀폐용기</div></li></ul>'
        r = trend_crawler.TrendCrawler.get_coupang_best(live=True, fetch=lambda u: page)
        self.assertTrue(r["live"])
        self.assertEqual([i["title"] for i in r["items"]], ["접이식 캠핑 의자 초경량", "원터치 진공 밀폐용기"])  # 중복 제거
        self.assertTrue(all(i["live"] for i in r["items"]))

    def test_reddit_parse(self):
        data = {"data": {"children": [
            {"data": {"title": "TIL a fact", "score": 10, "permalink": "/r/x/1", "num_comments": 3}},
            {"data": {"title": "pinned", "stickied": True, "score": 99}},
            {"data": {"title": "nsfw", "over_18": True}},
            {"data": {"title": "Second", "score": 50, "permalink": "/r/x/2"}}]}}
        r = trend_crawler.TrendCrawler.get_reddit_topics("history", live=True, fetch=lambda u: json.dumps(data))
        self.assertTrue(r["live"])
        self.assertEqual([i["title"] for i in r["items"]], ["Second", "TIL a fact"])  # 점수순, 고정글/NSFW 제외
        self.assertTrue(r["items"][0]["url"].startswith("https://www.reddit.com/r/x/"))

    def test_youtube_without_key_does_not_call_network(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("YOUTUBE_API_KEY", None)
            r = trend_crawler.TrendCrawler.get_youtube_outliers("kitchen", fetch=lambda u: (_ for _ in ()).throw(AssertionError("호출되면 안 됨")))
        self.assertFalse(r["live"])
        self.assertIn("API 키", r["note"])


# ------------------------------------------------------------------ server
def _copy_project(dst: Path):
    for name in ("config.json", "config.js", "web_dashboard.html", "pipeline_core.js"):
        shutil.copy(ROOT / name, dst / name)
    shutil.copytree(ROOT / "data", dst / "data")
    shutil.copytree(ROOT / "samples", dst / "samples")
    (dst / "assets").mkdir()


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import server
        cls.server = server
        cls.tmp = tempfile.TemporaryDirectory()
        _copy_project(Path(cls.tmp.name))
        cls.srv = server.make_server(0, Path(cls.tmp.name))
        cls.port = cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.env = mock.patch.dict(os.environ, {}, clear=False)
        cls.env.start()
        os.environ.pop("YOUTUBE_API_KEY", None)

    @classmethod
    def tearDownClass(cls):
        cls.env.stop()
        cls.srv.shutdown()
        cls.srv.server_close()
        cls.tmp.cleanup()

    def req(self, method, path, body=None, headers=None, raw=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=30)
        h = dict(headers or {})
        data = raw
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            h["Content-Type"] = "application/json"
        c.request(method, path, body=data, headers=h)
        r = c.getresponse()
        payload = r.read()
        c.close()
        try:
            return r.status, json.loads(payload.decode("utf-8")), r
        except ValueError:
            return r.status, payload, r

    def test_static_and_config(self):
        s, body, _ = self.req("GET", "/")
        self.assertEqual(s, 200)
        self.assertIn(b"AI Shorts Pipeline Studio", body)
        self.assertEqual(self.req("GET", "/pipeline_core.js")[0], 200)
        self.assertEqual(self.req("GET", "/config.js")[0], 200)
        s, cfg, _ = self.req("GET", "/api/config")
        self.assertEqual((s, cfg["version"]), (200, "3.0"))
        self.assertEqual(self.req("GET", "/server.py")[0], 404)       # 소스 파일은 노출 안 함
        self.assertEqual(self.req("GET", "/config.json")[0], 404)

    def test_host_and_origin_guard(self):
        self.assertEqual(self.req("GET", "/api/config", headers={"Host": "evil.com"})[0], 403)
        s, _, _ = self.req("POST", "/api/validate", {"project": {}}, headers={"Origin": "http://evil.com"})
        self.assertEqual(s, 403)
        s, _, _ = self.req("POST", "/api/validate", {"project": {}}, headers={"Origin": f"http://127.0.0.1:{self.port}"})
        self.assertEqual(s, 200)

    def test_prompt_and_validate_api(self):
        proj = json.loads((ROOT / "samples" / "airfryer_shopping.json").read_text(encoding="utf-8"))
        s, r, _ = self.req("POST", "/api/build-prompt", {"project": proj})
        self.assertEqual(s, 200)
        self.assertEqual(r["prompt"], pe.build_master_prompt(CFG, pe.normalize_project(proj, CFG)))
        self.assertEqual(r["model"]["name"], "Claude Sonnet 5.5")
        s, r, _ = self.req("POST", "/api/build-prompt", {"project": proj, "kind": "metadata", "languages": ["ko", "en"]})
        self.assertIn("en(English)", r["prompt"])
        s, r, _ = self.req("POST", "/api/validate", {"project": proj})
        self.assertEqual((r["total"], [i["level"] for i in r["issues"]]), (325, ["ok", "ok"]))

    def test_upload_media_range_and_delete(self):
        s, r, _ = self.req("POST", "/api/upload?kind=clip&scene=3&name=x.MOV", raw=b"0123456789")
        self.assertEqual((s, r["saved"]), (200, "scene3.mov"))
        s, r, _ = self.req("POST", "/api/upload?kind=clip&scene=3&name=y.mp4", raw=b"abcdefghij")
        self.assertEqual(r["saved"], "scene3.mp4")
        self.assertFalse((Path(self.tmp.name) / "input" / "scene3.mov").exists(), "같은 씬의 이전 파일은 교체됨")
        s, files, _ = self.req("GET", "/api/files")
        self.assertEqual(files["clips"]["3"]["name"], "scene3.mp4")
        self.assertEqual(files["missing_clips"], [1, 2, 4, 5, 6])
        s, data, resp = self.req("GET", "/media/input/scene3.mp4", headers={"Range": "bytes=2-5"})
        self.assertEqual((s, data, resp.getheader("Content-Range")), (206, b"cdef", "bytes 2-5/10"))
        self.assertEqual(self.req("GET", "/media/input/secret.txt")[0], 403)
        self.assertIn(self.req("GET", "/media/input/..%2Fconfig.json")[0], (403, 404))
        self.assertEqual(self.req("POST", "/api/upload?kind=clip&scene=7&name=a.mp4", raw=b"x")[0], 400)
        self.assertEqual(self.req("POST", "/api/upload?kind=clip&scene=1&name=a.exe", raw=b"x")[0], 400)
        self.assertEqual(self.req("POST", "/api/upload?kind=voice&name=a.mp4", raw=b"x")[0], 400)
        s, r, _ = self.req("POST", "/api/upload?kind=voice_raw&name=tts.wav", raw=b"RIFF")
        self.assertEqual(r["saved"], "voice_raw.wav")
        s, r, _ = self.req("POST", "/api/delete-file", {"kind": "clip", "scene": 3})
        self.assertEqual(r["removed"], ["scene3.mp4"])

    def test_reference_image_upload_media_delete(self):
        png = b"\x89PNG\r\n\x1a\n0123456789"
        s, r, _ = self.req("POST", "/api/upload?kind=ref&id=hero&name=a.PNG", raw=png)
        self.assertEqual((s, r["saved"]), (200, "hero.png"))
        s, r, _ = self.req("POST", "/api/upload?kind=ref&id=hero&name=b.jpg", raw=b"jpgdata")
        self.assertEqual(r["saved"], "hero.jpg")
        self.assertFalse((Path(self.tmp.name) / "input" / "refs" / "hero.png").exists(), "같은 id 의 이전 파일은 교체됨")
        s, files, _ = self.req("GET", "/api/files")
        self.assertEqual(files["refs"], {"hero": "hero.jpg"})
        s, data, resp = self.req("GET", "/media/refs/hero.jpg")
        self.assertEqual((s, data), (200, b"jpgdata"))
        self.assertEqual(self.req("GET", "/media/refs/..%2fconfig.json")[0], 404)
        self.assertEqual(self.req("GET", "/media/refs/HERO.jpg")[0], 404)           # 허용 패턴(소문자 id)만
        for bad in ("kind=ref&id=Hero&name=a.png", "kind=ref&id=h&name=a.exe", "kind=ref&id=..%2fx&name=a.png", "kind=ref&name=a.png"):
            self.assertEqual(self.req("POST", "/api/upload?" + bad, raw=b"x")[0], 400, bad)
        s, r, _ = self.req("POST", "/api/delete-file", {"kind": "ref", "id": "hero"})
        self.assertEqual(r["removed"], ["hero.jpg"])
        self.assertEqual(self.req("POST", "/api/delete-file", {"kind": "ref", "id": "../x"})[0], 400)
        self.assertEqual(self.req("GET", "/api/files")[1]["refs"], {})

    def test_fonts_endpoints_and_upload(self):
        s, r, _ = self.req("GET", "/api/fonts")
        self.assertEqual(s, 200)
        self.assertIsInstance(r["fonts"], list)
        s, r, _ = self.req("POST", "/api/upload?kind=font&name=" + "My%20Font!.TTF", raw=b"FAKEFONTDATA")
        self.assertEqual(s, 200)
        self.assertEqual(r["spec"], "assets:My Font_.TTF")
        self.assertTrue((Path(self.tmp.name) / "assets" / "My Font_.TTF").exists())
        fonts = self.req("GET", "/api/fonts")[1]["fonts"]
        self.assertEqual(fonts[0]["spec"], "assets:My Font_.TTF")
        import urllib.parse
        s, data, resp = self.req("GET", "/api/font-file?spec=" + urllib.parse.quote("assets:My Font_.TTF"))
        self.assertEqual((s, data), (200, b"FAKEFONTDATA"))
        self.assertEqual(self.req("GET", "/api/font-file?spec=" + urllib.parse.quote("assets:../../config.json"))[0], 404)
        self.assertEqual(self.req("GET", "/api/font-file?spec=system:nope-xyz.ttf")[0], 404)
        self.assertEqual(self.req("GET", "/api/font-file?spec=/etc/passwd")[0], 404)
        for bad in ("kind=font&name=a.exe", "kind=font&name=..", "kind=font"):
            self.assertEqual(self.req("POST", "/api/upload?" + bad, raw=b"x")[0], 400, bad)

    @unittest.skipUnless(HAVE_FFMPEG, "ffmpeg 없음")
    def test_audio_process_respects_posted_settings(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=1", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono:d=1",
                            "-f", "lavfi", "-i", "sine=frequency=440:duration=1", "-filter_complex", "[0][1][2]concat=n=3:v=0:a=1", str(td / "raw.wav")], check=True)
            self.assertEqual(self.req("POST", "/api/upload?kind=voice_raw&name=r.wav", raw=(td / "raw.wav").read_bytes())[0], 200)
            try:
                def run(**kw):
                    st_, r, _ = self.req("POST", "/api/audio/process", kw)
                    self.assertEqual(st_, 200, r)
                    return r
                a = run(speed=1.0, remove_silence=False)
                b = run(speed=1.0, remove_silence=True)
                c = run(speed=2.0, remove_silence=True)
                self.assertAlmostEqual(a["after"], 3.0, delta=0.2)
                self.assertTrue(2.0 <= b["after"] <= 2.4, b)
                self.assertAlmostEqual(c["after"], b["after"] / 2, delta=0.15)
                f = run(speed=1.2, remove_silence=True, fit_seconds=4)
                self.assertAlmostEqual(f["after"], 4.0, delta=0.3)
                self.assertAlmostEqual(f["speed"], f["base_len"] / 4, places=2)
            finally:
                self.req("POST", "/api/delete-file", {"kind": "voice_raw"})
                self.req("POST", "/api/delete-file", {"kind": "voice"})

    def test_project_save_load(self):
        self.assertEqual(self.req("POST", "/api/project", {"name": "../evil", "project": {}})[0], 400)
        self.assertEqual(self.req("POST", "/api/project", {"name": ".hidden", "project": {}})[0], 400)
        s, r, _ = self.req("POST", "/api/project", {"name": "내 프로젝트 1", "project": {"meta": {"topic": "t"}}})
        self.assertEqual((s, r["saved"]), (200, "내 프로젝트 1"))
        import urllib.parse
        s, r, _ = self.req("GET", "/api/project?name=" + urllib.parse.quote("내 프로젝트 1"))
        self.assertEqual(r["meta"]["topic"], "t")
        s, r, _ = self.req("GET", "/api/projects")
        self.assertIn("내 프로젝트 1", r["projects"])

    def test_source_endpoints_error_paths(self):
        s, r, _ = self.req("POST", "/api/outliers", {"query": "kitchen"})
        self.assertEqual(s, 502)
        self.assertIn("API 키", r["error"])
        s, r, _ = self.req("POST", "/api/transcript", {"url": "https://example.com/x"})
        self.assertEqual(s, 422)
        s, r, _ = self.req("POST", "/api/audio/process", {})
        self.assertEqual(s, 400)

    def test_claude_endpoint_never_calls_cli_when_missing(self):
        with mock.patch.object(self.server.shutil, "which", return_value=None):
            s, r, _ = self.req("POST", "/api/claude", {"prompt": "hi"})
        self.assertEqual(s, 501)

    def test_trends_offline(self):
        s, r, _ = self.req("GET", "/api/trends?live=0&sources=coupang,tiktok")
        self.assertEqual(s, 200)
        self.assertTrue(all(not i["live"] for i in r["items"]))
        self.assertEqual(set(r["status"]), {"coupang", "tiktok"})

    def test_render_without_clips_reports_error(self):
        s, r, _ = self.req("POST", "/api/render", {"project": {}})
        self.assertEqual((s, r["started"]), (200, True))
        for _ in range(50):
            time.sleep(0.1)
            _, job, _ = self.req("GET", "/api/render/status")
            if job["state"] != "running":
                break
        self.assertEqual(job["state"], "error")
        self.assertIn("씬 클립", job["error"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
