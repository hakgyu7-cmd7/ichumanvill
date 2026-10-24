"""find_hits.py 시험. 실행: python3 -m unittest yadam/tools/test_find_hits.py"""
import csv
import os
import sys
import tempfile
import unittest
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(__file__))
import find_hits as fh  # noqa: E402

TODAY = date(2026, 10, 22)


def video(channel, subs, views, days_ago=30, seconds=900, likes=None, **kw):
    v = {"channel_id": channel, "channel": channel, "channel_url": "", "subscribers": subs,
         "video_id": f"{channel}-{views}-{days_ago}", "url": "", "title": f"{channel} {views}",
         "published": (TODAY - timedelta(days=days_ago)).isoformat(), "seconds": seconds,
         "views": views, "likes": likes, "comments": None, "is_live": False}
    v.update(kw)
    return v


def channel_with(name, subs, baseline_views, extra):
    """기준선(중앙값)이 baseline_views가 되도록 평범한 영상 7편을 깔고 extra 영상을 더한다."""
    vs = [video(name, subs, baseline_views, days_ago=20 + i * 5) for i in range(7)]
    return vs + extra


class JudgeTest(unittest.TestCase):
    def test_examples_from_criteria(self):
        # 분석 기준표 4장 계산 예시
        mid = channel_with("중형", 50_000, 20_000, [
            video("중형", 50_000, 120_000, days_ago=40),
            video("중형", 50_000, 60_000, days_ago=45),
        ])
        small = channel_with("소형", 5_000, 1_500, [video("소형", 5_000, 9_000, days_ago=40)])
        videos = mid + small
        channels = fh.judge(videos, TODAY)
        self.assertEqual(channels["중형"]["baseline"], 20_000)
        status = {(v["channel"], v["views"]): v["status"] for v in videos}
        self.assertEqual(status[("중형", 120_000)], "잘 됨")
        self.assertEqual(status[("중형", 20_000)], "평범")
        self.assertEqual(status[("중형", 60_000)], "보류")
        self.assertEqual(status[("소형", 9_000)], "보류")  # 6배지만 1만 회 미만

    def test_exclusions(self):
        vs = channel_with("A", 50_000, 20_000, [
            video("A", 50_000, 300_000, seconds=59),
            video("A", 50_000, 300_000, days_ago=5),
            video("A", 50_000, 300_000, days_ago=120),
            video("A", 50_000, 300_000, is_live=True),
        ])
        vs += [video("구간밖", 20_000, 300_000)]
        fh.judge(vs, TODAY)
        got = [v["status"] for v in vs[7:]]
        self.assertEqual(got, ["제외: 8분 미만", "제외: 14일 안 됨", "제외: 기간 밖",
                               "제외: 라이브", "제외: 구간 밖"])

    def test_ad_suspect_and_small_channel(self):
        vs = [video("B", 50_000, 20_000, days_ago=20 + i, likes=400) for i in range(7)]
        vs.append(video("B", 50_000, 200_000, days_ago=40, likes=200))  # 좋아요율 0.1% < 2%/3
        vs += [video("C", 50_000, 20_000, days_ago=20 + i) for i in range(3)]
        fh.judge(vs, TODAY)
        self.assertEqual(vs[7]["status"], "제외: 광고 유입 의심")
        self.assertTrue(vs[-1]["status"].startswith("제외: 채널 영상 3편뿐"))

    def test_sample_picks_best_per_channel_and_closest_pair(self):
        videos = []
        for i, name in enumerate(["M1", "M2", "M3", "M4"]):
            videos += channel_with(name, 50_000, 20_000, [
                video(name, 50_000, 120_000 + i * 20_000, days_ago=50),
                video(name, 50_000, 110_000, days_ago=60),
            ])
        channels = fh.judge(videos, TODAY)
        sample, notes = fh.pick_sample(videos, channels)
        mid = [s for s in sample if s["tier"] == "중형"]
        hits = [s for s in mid if s["role"] == "잘 됨"]
        pairs = [s for s in mid if s["role"].startswith("평범")]
        self.assertEqual([h["channel"] for h in hits], ["M4", "M3", "M2"])
        self.assertEqual([h["views"] for h in hits], [180_000, 160_000, 140_000])
        self.assertEqual([p["channel"] for p in pairs], ["M4", "M3"])
        # 잘 된 영상(50일 전)과 업로드일이 가장 가까운 평범한 영상(50일 전 근처 = 50일 전 기준선 영상)
        self.assertTrue(all(abs(p["age_days"] - 50) <= 5 for p in pairs))
        self.assertTrue(any("소형" in n for n in notes))


class ParseTest(unittest.TestCase):
    def test_numbers(self):
        self.assertEqual(fh.to_int("1,234"), 1234)
        self.assertEqual(fh.to_int("3.2만"), 32_000)
        self.assertEqual(fh.to_seconds("12:14"), 734)
        self.assertEqual(fh.to_seconds("1:02:03"), 3723)
        self.assertEqual(fh.parse_duration("PT1H2M3S"), 3723)
        self.assertEqual(fh.parse_duration("PT45S"), 45)

    def test_csv_round_trip(self):
        rows = channel_with("D", 90_000, 30_000, [video("D", 90_000, 200_000, days_ago=40)])
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "in.csv")
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                w = csv.writer(f)
                w.writerow(["channel", "subscribers", "title", "published", "seconds", "views", "likes"])
                for r in rows:
                    w.writerow([r["channel"], f"{r['subscribers']:,}", r["title"], r["published"],
                                "15:00", r["views"], ""])
            out = os.path.join(d, "out")
            fh.main(["--from-csv", path, "--date", TODAY.isoformat(), "--out", out])
            with open(os.path.join(out, "결과.md"), encoding="utf-8") as f:
                report = f.read()
            self.assertIn("| 대형 | 잘 됨 | D |", report)
            self.assertTrue(os.path.exists(os.path.join(out, "표본15편.csv")))


class ApiTest(unittest.TestCase):
    def test_collect_with_fake_api(self):
        class Fake(fh.YouTube):
            def get(self, path, cost=1, **params):
                if path == "channels":
                    return {"items": [{"id": "UC" + "x" * 22, "snippet": {"title": "가짜채널"},
                                       "statistics": {"subscriberCount": "52000"},
                                       "contentDetails": {"relatedPlaylists": {"uploads": "UUx"}}}]}
                if path == "playlistItems":
                    items = [{"contentDetails": {"videoId": f"v{i}",
                              "videoPublishedAt": f"2026-{9 if i < 3 else 6:02d}-0{i + 1}T00:00:00Z"}}
                             for i in range(5)]
                    return {"items": items}
                if path == "videos":
                    return {"items": [{"id": vid, "snippet": {"title": vid, "publishedAt": "2026-09-01T00:00:00Z",
                                                              "liveBroadcastContent": "none"},
                                       "contentDetails": {"duration": "PT12M"},
                                       "statistics": {"viewCount": "1000", "likeCount": "10"}}
                                      for vid in params["id"].split(",")]}
                raise AssertionError(path)

        vs = fh.collect_from_api(Fake("k"), ["@가짜"], TODAY)
        self.assertEqual([v["video_id"] for v in vs], ["v0", "v1", "v2"])  # 6월 영상에서 멈춤
        self.assertEqual(vs[0]["seconds"], 720)
        self.assertFalse(vs[0]["is_live"])

    def test_channel_without_uploads_is_skipped(self):
        class Fake(fh.YouTube):
            def get(self, path, cost=1, **params):
                if path == "channels":
                    return {"items": [{"id": "UC" + "y" * 22, "snippet": {"title": "빈채널"},
                                       "statistics": {"subscriberCount": "5000"},
                                       "contentDetails": {"relatedPlaylists": {"uploads": "UUy"}}}]}
                raise fh.ApiError(404, "playlist cannot be found")

        self.assertEqual(fh.collect_from_api(Fake("k"), ["@빈채널"], TODAY), [])

    def test_other_errors_still_stop(self):
        class Fake(fh.YouTube):
            def get(self, path, cost=1, **params):
                raise fh.ApiError(403, "quotaExceeded")

        with self.assertRaises(fh.ApiError):
            fh.collect_from_api(Fake("k"), ["@x"], TODAY)


if __name__ == "__main__":
    unittest.main()
