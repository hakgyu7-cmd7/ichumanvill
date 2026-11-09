"""AI 쇼츠 파이프라인 통합 테스트.  실행: python -m unittest discover -s tests -v   (또는 python tests/test_pipeline.py)"""
import copy
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import prompt_engine as pe  # noqa: E402

CFG = pe.load_config()
RAMEN = json.loads((ROOT / "samples" / "ramen_bgrade.json").read_text(encoding="utf-8"))
AIR = json.loads((ROOT / "samples" / "airfryer_shopping.json").read_text(encoding="utf-8"))

MESSY_RESPONSE = '''설명 문장이 앞에 붙어 있어도 괜찮아야 합니다.
```json
{"analysis": {"hook_technique": "h", "retention_psychology": "r", "skeleton": "s"},
 "plan": {"titles": ["a", "b", "c"], "description": "d", "hashtags": ["#x"]},
 "top_title": "  테스트 타이틀  ", "subject_anchor": "a tiny PVC figure",
 "scenes": [
  {"id": 1, "beats": ["[0.0~2.5s] 첫 번째 비트", "[2.5~5.0s] 두 번째 비트", "[5.0~7.5s] 세 번째 비트"],
   "frame1": "wide shot of a figure --no text --ar 9:16", "frame2": "low angle shot",
   "cuts": [{"type": "Medium Close-up", "prompt": "Rapid push-in"}, {"type": "Low-angle", "prompt": "Hard cut"}, "Whip-pan"]},
  {"id": 2, "narration": "[0~2.5s] 하나 [2.5~5s] 둘 [5~7.5s] 셋", "frame_1": "f1", "frame_2": "f2", "angles": [{"prompt": "a"}, {"prompt": "b"}, {"prompt": "c"}]}
 ]}
```
끝.'''


def variants():
    """Python/JS parity 테스트용 케이스 매트릭스."""
    cases = []
    for name, base in (("ramen", RAMEN), ("air", AIR)):
        for lang in ("ko", "en", "ja", "zh"):
            p = copy.deepcopy(base)
            p["meta"]["language"] = lang
            cases.append({"name": f"{name}-{lang}", "project": p, "langs": ["ko", "en"] if lang == "ko" else [lang, "ko", "zh"]})
    p = copy.deepcopy(RAMEN)
    p["meta"].update({"category": "disaster", "category2": "bgrade", "format": "moral_dilemma", "style": "cinematic",
                      "source_url": "https://youtu.be/abc", "source_script": "원본 $& $1 {{topic}} `x` \"q\" \\ 대본"})
    p["options"] = {"zero_text": False, "safe_margin": False}
    p["subject_anchor"] = "the same 30-year-old Korean man in a dusty grey hoodie."
    cases.append({"name": "cross", "project": p, "langs": ["ko", "en", "ja", "zh"]})
    p = copy.deepcopy(AIR)
    p["meta"].update({"category": "history", "category2": "shopping", "style": "vintage_1930", "format": "unusual_top5"})
    p["scenes"][5]["beats"][2] = "그냥 평범한 마지막 문장"
    p["scenes"][1]["frame1"] = "사람이 간판을 보는 장면 with signage and extreme close-up macro, headline poster"
    p["scenes"][2]["cuts"][1]["type"] = "Extreme Close-up"
    cases.append({"name": "bad", "project": p})
    cases.append({"name": "empty", "project": {}})
    cases.append({"name": "legacy", "project": {"meta": {"style": "피규어_디오라마", "category": "쇼핑_꿀템", "category2": "B급_병맛", "language": "xx"}}})
    cases.append({"name": "response", "project": copy.deepcopy(RAMEN), "response": MESSY_RESPONSE})
    return cases


class ConfigTests(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(len(CFG["styles"]), 7)
        self.assertEqual(len(CFG["categories"]), 13)
        self.assertEqual(len(CFG["formats"]), 4)
        self.assertEqual(set(CFG["languages"]), {"ko", "en", "ja", "zh"})
        self.assertEqual(len(CFG["scene_roles"]), 6)
        self.assertEqual(sorted(s["number"] for s in CFG["styles"].values()), list(range(1, 8)))

    def test_blueprints_complete(self):
        keys = [k for k, _ in CFG["blueprint_keys"]]
        for cid, c in CFG["categories"].items():
            for k in keys + ["name", "flow", "styles"]:
                self.assertTrue(c.get(k), f"{cid}.{k} 누락")
            for s in c["styles"]:
                self.assertIn(s, CFG["styles"])
        self.assertEqual([c for c, v in CFG["categories"].items() if v.get("shopping")], ["shopping"])

    def test_styles_complete(self):
        for sid, s in CFG["styles"].items():
            for k in ("anchor", "video_feel", "name", "name_en", "desc"):
                self.assertTrue(s.get(k), f"{sid}.{k}")
        self.assertEqual(pe.default_style_id(CFG), "diorama")

    def test_config_js_in_sync(self):
        txt = (ROOT / "config.js").read_text(encoding="utf-8")
        dec = json.JSONDecoder()

        def grab(name):
            i = txt.index(f"window.{name} = ") + len(f"window.{name} = ")
            return dec.raw_decode(txt[i:])[0]

        hint = "config.js 가 오래됨: python prompt_engine.py sync-config"
        self.assertEqual(grab("PIPELINE_CONFIG"), CFG, hint)
        self.assertEqual(grab("PIPELINE_SEED"), json.loads((ROOT / "data" / "trends_seed.json").read_text(encoding="utf-8")), hint)
        samples = {p.stem: pe.normalize_project(json.loads(p.read_text(encoding="utf-8")), CFG) for p in sorted((ROOT / "samples").glob("*.json"))}
        self.assertEqual(grab("PIPELINE_SAMPLES"), samples, hint)


class EngineTests(unittest.TestCase):
    def test_samples_valid(self):
        for p in (RAMEN, AIR):
            proj = pe.normalize_project(p, CFG)
            errs = [i for i in pe.validate_project(CFG, proj) if i["level"] == "error"]
            self.assertEqual(errs, [], errs)
            total = pe.total_units(proj, CFG)
            self.assertTrue(320 <= total <= 350, total)

    def test_frame_composition(self):
        proj = pe.normalize_project(AIR, CFG)
        f = pe.compose_frame(CFG, proj, "a wide shot.")
        self.assertTrue(f.startswith(CFG["styles"]["diorama"]["anchor"]))
        self.assertTrue(f.endswith(CFG["suffix"]["zero_text"]))
        self.assertIn(proj["subject_anchor"].rstrip("."), f)
        self.assertEqual(f.count("--no text"), 1)
        proj["options"] = {"zero_text": False, "safe_margin": False}
        f2 = pe.compose_frame(CFG, proj, "a wide shot")
        self.assertNotIn("--no", f2)
        self.assertNotIn("safe area", f2)

    def test_style_switch_changes_every_frame(self):
        proj = pe.normalize_project(RAMEN, CFG)
        proj["meta"]["style"] = "claymation"
        for i in range(6):
            pk = pe.scene_package(CFG, proj, i)
            self.assertTrue(pk["frame1"].startswith(CFG["styles"]["claymation"]["anchor"]))
            self.assertTrue(pk["frame2"].startswith(CFG["styles"]["claymation"]["anchor"]))
            self.assertIn(CFG["styles"]["claymation"]["video_feel"], pk["omni"])

    def test_omni_structure(self):
        proj = pe.normalize_project(RAMEN, CFG)
        o = pe.compose_omni(CFG, proj, proj["scenes"][0])
        for lab in CFG["time_labels"]:
            self.assertIn(lab, o)
        self.assertIn("Start from Frame 1.", o)
        self.assertIn("Instant hard cut to the Frame 2 view.", o)
        self.assertEqual(o.count("[") , 3)

    def test_master_prompt_rules(self):
        m = pe.build_master_prompt(CFG, pe.normalize_project(AIR, CFG))
        for needle in ("45초", "320~350자", "Zero-Text", "1.06배", "쇼핑 카테고리 전용", "제품 정보는 하단 쇼핑 태그와 고정 댓글 확인!", "```json"):
            self.assertIn(needle, m)
        self.assertNotIn("{{", m)
        r = pe.build_master_prompt(CFG, pe.normalize_project(RAMEN, CFG))
        self.assertNotIn("쇼핑 카테고리 전용", r)
        self.assertNotIn("{{", r)

    def test_cross_mode_and_source(self):
        p = pe.normalize_project(RAMEN, CFG)
        p["meta"].update({"category": "history", "category2": "shopping", "source_script": "원본 대본 텍스트"})
        m = pe.build_master_prompt(CFG, p)
        self.assertIn("합성 크로스오버", m)
        self.assertIn("(1차)", m)
        self.assertIn("(2차 착지)", m)
        self.assertIn("원본 대본 텍스트", m)
        self.assertIn("쇼핑 카테고리 전용", m)  # 2차가 쇼핑이면 CTA 규칙 적용
        self.assertEqual(pe.recommended_model(CFG, p)["name"], "Claude Opus 5.5")

    def test_language_counting(self):
        self.assertEqual(pe.count_units("가 나 다", "ko", CFG), 5)
        self.assertEqual(pe.count_units("a b  c", "en", CFG), 3)
        self.assertEqual(pe.count_units("こ ん に", "ja", CFG), 3)

    def test_validator_catches_problems(self):
        p = pe.normalize_project(AIR, CFG)
        p["scenes"][0]["frame1"] = "한글 프롬프트 sign text"
        p["scenes"][1]["frame2"] = "extreme close-up of a pot"
        p["scenes"][5]["beats"][2] = "그냥 끝"
        codes = {i["code"] for i in pe.validate_project(CFG, p)}
        self.assertTrue({"zero_text_cjk", "zero_text_word", "extreme_closeup", "cta"} <= codes, codes)
        p2 = pe.inject_cta(CFG, p)
        codes2 = {i["code"] for i in pe.validate_project(CFG, p2) if i["level"] == "error"}
        self.assertNotIn("cta", codes2)
        self.assertEqual(pe.inject_cta(CFG, p2), p2)  # 멱등

    def test_parse_claude_response(self):
        parsed = pe.parse_claude_response(MESSY_RESPONSE, CFG)
        self.assertEqual(len(parsed["scenes"]), 6)
        s1, s2 = parsed["scenes"][0], parsed["scenes"][1]
        self.assertEqual(s1["beats"][0], "첫 번째 비트")
        self.assertEqual(s1["frame1"], "wide shot of a figure")  # --no/--ar 접미사 제거
        self.assertEqual(s1["cuts"][2]["prompt"], "Whip-pan")
        self.assertEqual(s2["beats"], ["하나", "둘", "셋"])
        self.assertEqual(s2["frame1"], "f1")
        self.assertEqual(parsed["top_title"], "테스트 타이틀")
        with self.assertRaises(ValueError):
            pe.parse_claude_response("JSON 없음", CFG)

    def test_legacy_keys(self):
        p = pe.normalize_project({"meta": {"style": "피규어_디오라마", "category": "쇼핑_꿀템", "category2": "B급_병맛", "language": "xx"}}, CFG)
        self.assertEqual((p["meta"]["style"], p["meta"]["category"], p["meta"]["category2"], p["meta"]["language"]), ("diorama", "shopping", "bgrade", "ko"))

    def test_metadata_prompt(self):
        m = pe.build_metadata_prompt(CFG, pe.normalize_project(AIR, CFG), ["ko", "en", "ja", "zh"])
        for needle in ("YouTube Shorts", "Instagram Reels", "TikTok", "ko(한국어)", "zh(中文)", "쇼핑 태그", "Scene 06"):
            self.assertIn(needle, m)
        self.assertNotIn("{{", m)


@unittest.skipUnless(shutil.which("node"), "node 없음")
class ParityTests(unittest.TestCase):
    def test_python_js_identical(self):
        cases = variants()
        res = subprocess.run(["node", str(ROOT / "tests" / "parity_node.js")], input=json.dumps(cases), capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(res.returncode, 0, res.stderr)
        js = json.loads(res.stdout)
        self.assertEqual(len(js), len(cases))
        for case, j in zip(cases, js):
            n = case["name"]
            p = pe.normalize_project(case["project"], CFG)
            self.assertEqual(j["project"], p, f"normalize 불일치: {n}")
            self.assertEqual(j["master"], pe.build_master_prompt(CFG, p), f"master 불일치: {n}")
            self.assertEqual(j["metadata"], pe.build_metadata_prompt(CFG, p, case.get("langs", ["ko"])), f"metadata 불일치: {n}")
            self.assertEqual(j["all_prompts"], pe.all_prompts_text(CFG, p), f"all_prompts 불일치: {n}")
            self.assertEqual(j["packages"], [pe.scene_package(CFG, p, i) for i in range(6)], f"packages 불일치: {n}")
            self.assertEqual(j["validate"], pe.validate_project(CFG, p), f"validate 불일치: {n}")
            self.assertEqual(j["total"], pe.total_units(p, CFG), n)
            self.assertEqual(j["shopping"], pe.is_shopping(p, CFG), n)
            self.assertEqual(j["model"], pe.recommended_model(CFG, p), n)
            self.assertEqual(j["cta"], pe.inject_cta(CFG, p), f"cta 불일치: {n}")
            if "response" in case:
                parsed = pe.parse_claude_response(case["response"], CFG)
                self.assertEqual(j["parsed"], parsed, "parse 불일치")
                self.assertEqual(j["applied"], pe.apply_response(p, parsed), "apply 불일치")


if __name__ == "__main__":
    unittest.main(verbosity=2)
