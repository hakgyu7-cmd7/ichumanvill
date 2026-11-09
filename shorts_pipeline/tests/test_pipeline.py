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
    reply = (ROOT / "tests" / "fixtures" / "claude_reply.txt").read_text(encoding="utf-8")
    areply = (ROOT / "tests" / "fixtures" / "assets_reply.txt").read_text(encoding="utf-8")
    cases.append({"name": "assets", "project": copy.deepcopy(AIR), "response": reply, "assets_response": areply})
    pa = copy.deepcopy(AIR)
    pa["meta"]["language"] = "en"
    pa["assets"][1]["appearance"] = "한글 appearance"
    pa["scenes"][2]["refs"] = ["pot", "nope", "pot"]
    cases.append({"name": "assets-en-bad", "project": pa, "assets_response": areply})
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
        refs = proj["scenes"][0]["refs"]            # Scene 01: cook, fryer
        f = pe.compose_frame(CFG, proj, "a wide shot.", refs)
        self.assertTrue(f.startswith(CFG["styles"]["diorama"]["anchor"]))
        self.assertTrue(f.endswith(CFG["suffix"]["zero_text"]))
        by_id = {a["id"]: a for a in proj["assets"]}
        self.assertIn(by_id["cook"]["appearance"], f)
        self.assertIn(by_id["fryer"]["appearance"], f)
        self.assertNotIn(by_id["pot"]["appearance"], f)          # 이 씬에 연결되지 않은 대상은 삽입 안 됨
        self.assertLess(f.index(by_id["cook"]["appearance"]), f.index("a wide shot"))  # 앵커 -> 대상 외형 -> 장면 묘사 순서
        self.assertEqual(f.count("--no text"), 1)
        self.assertNotIn(by_id["cook"]["appearance"], pe.compose_frame(CFG, proj, "a wide shot", []))
        proj["options"] = {"zero_text": False, "safe_margin": False}
        f2 = pe.compose_frame(CFG, proj, "a wide shot", refs)
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
        self.assertEqual(parsed["assets"][0]["appearance"], "a tiny PVC figure")   # 옛 subject_anchor -> asset
        self.assertEqual(parsed["scenes"][0]["refs"], ["main"])
        full = pe.parse_claude_response((ROOT / "tests" / "fixtures" / "claude_reply.txt").read_text(encoding="utf-8"), CFG)
        self.assertEqual([a["id"] for a in full["assets"]], ["hero", "pot", "kitchen"])
        self.assertEqual(full["scenes"][1]["refs"], ["hero", "pot", "kitchen"])
        applied = pe.apply_response(pe.normalize_project({}, CFG), full)
        self.assertEqual(len(applied["assets"]), 3)
        with self.assertRaises(ValueError):
            pe.parse_claude_response("JSON 없음", CFG)

    def test_assets_normalization_and_legacy_anchor(self):
        a = pe.normalize_assets([{"id": "Hero Man", "label": "x"}, {"id": "hero man"}, {"label": "The Pot", "type": "THING"}, "bad", {"type": "place"}])
        self.assertEqual([x["id"] for x in a], ["hero_man", "hero_man_2", "the_pot", "asset5"])
        self.assertEqual([x["type"] for x in a], ["object", "object", "object", "place"])
        p = pe.normalize_project({"subject_anchor": "a tiny PVC figure --no text.", "scenes": [{"beats": ["a", "b", "c"]}]}, CFG)
        self.assertEqual(len(p["assets"]), 1)
        self.assertEqual(p["assets"][0]["appearance"], "a tiny PVC figure")
        self.assertTrue(all(sc["refs"] == ["main"] for sc in p["scenes"]))
        self.assertNotIn("subject_anchor", p)
        q = pe.normalize_project({"assets": [{"id": "a"}], "scenes": [{"refs": ["a", "a", "zzz"]}]}, CFG)
        self.assertEqual(q["scenes"][0]["refs"], ["a"])   # 중복/없는 id 제거

    def test_reference_prompts(self):
        proj = pe.normalize_project(RAMEN, CFG)
        refs = pe.reference_prompts(CFG, proj)
        self.assertEqual([r["id"] for r in refs], ["hero", "pot", "kitchen"])
        self.assertEqual(refs[2]["scenes"], [1, 2, 5])
        hero = refs[0]
        self.assertTrue(hero["main"].startswith(CFG["styles"]["diorama"]["anchor"]))
        self.assertIn("full-body character reference image", hero["main"])
        self.assertTrue(hero["main"].endswith(CFG["suffix"]["zero_text_core"] + " --ar 9:16"))
        self.assertIn("turnaround reference sheet", hero["sheet"])
        self.assertTrue(hero["sheet"].endswith("--ar 16:9"))
        self.assertIn("single hero object reference image", refs[1]["main"])
        self.assertIn("establishing reference image", refs[2]["main"])
        proj["options"]["zero_text"] = False
        self.assertNotIn("--no", pe.compose_reference(CFG, proj, proj["assets"][0], "main"))
        self.assertIn("[기준 이미지] 주인공 피규어", pe.all_prompts_text(CFG, pe.normalize_project(RAMEN, CFG)))

    def test_master_prompt_asset_rules(self):
        empty = pe.normalize_project({"meta": {"topic": "t"}}, CFG)
        m = pe.build_master_prompt(CFG, empty)
        self.assertIn("assets 배열에 정의하세요", m)
        self.assertIn('"assets": [', m)
        self.assertIn('"refs"', m)
        self.assertNotIn("subject_anchor", m)
        m2 = pe.build_master_prompt(CFG, pe.normalize_project(RAMEN, CFG))
        self.assertIn("이미 정의된 기준 이미지 대상", m2)
        self.assertIn("hero (character) 주인공 피규어 / the deadpan PVC man figure", m2)

    def test_asset_analysis_prompt_parse_apply_link(self):
        proj = pe.normalize_project(RAMEN, CFG)
        ap = pe.build_asset_prompt(CFG, proj)
        self.assertIn("Scene 01: 라면 끓일 때마다", ap)
        self.assertIn("scene_refs", ap)
        self.assertIn("이미 정의된 asset", ap)
        self.assertNotIn("{{", ap)
        text = (ROOT / "tests" / "fixtures" / "assets_reply.txt").read_text(encoding="utf-8")
        parsed = pe.parse_assets_response(text, CFG)
        self.assertEqual([a["id"] for a in parsed["assets"]], ["hero_man", "pot", "pot_2"])
        self.assertEqual(parsed["assets"][0]["keywords"], "남자, 주인공")           # 리스트 -> 문자열
        self.assertEqual(parsed["assets"][0]["appearance"], "a male figure with short black hair")  # --no 제거
        self.assertEqual(parsed["assets"][1]["type"], "object")                     # 알 수 없는 타입 -> object
        self.assertEqual(sorted(parsed["scene_refs"]), ["1", "2"])                  # 범위 밖/비정수/잘못된 값 무시
        base = json.loads(json.dumps(proj))
        base["assets"][1]["done"] = True                                            # 기존 pot(done) 은 id 가 같으면 유지
        applied = pe.apply_assets(pe.normalize_project(base, CFG), parsed)
        self.assertEqual(applied["scenes"][0]["refs"], ["hero_man", "pot"])        # 없는 id(ghost) 제거
        self.assertEqual(applied["scenes"][1]["refs"], ["pot"])                      # 중복 제거
        self.assertEqual(applied["scenes"][2]["refs"], ["pot"])                       # scene_refs 에 없는 씬은 기존 연결 중 유효한 id 만 유지
        self.assertTrue(next(a for a in applied["assets"] if a["id"] == "pot")["done"])
        with self.assertRaises(ValueError):
            pe.parse_assets_response("자산 없음", CFG)

    def test_link_assets_by_keywords(self):
        proj = pe.normalize_project(RAMEN, CFG)
        for sc in proj["scenes"]:
            sc["refs"] = []
        linked = pe.link_assets(proj)
        # '냄비'는 대본에 나오는 씬에, 'hero' 키워드(남자/주인공/사람/나)는 프롬프트의 'male PVC figure'가 아니라 한글 키워드 기준
        self.assertIn("pot", linked["scenes"][0]["refs"])        # Scene 01 대본: "냄비 위에"
        self.assertIn("kitchen", linked["scenes"][1]["refs"])    # Scene 02 프롬프트: "kitchen counter" (label 'the tiny apartment kitchen' 아님 -> 키워드 '주방/싱크대': 대본 '싱크대')
        self.assertEqual(pe.link_assets(linked), linked)         # 멱등

    def test_suggest_recurring_words(self):
        proj = pe.normalize_project({"scenes": [{"frame1": "a rusty lantern on a table", "frame2": "x"}, {"frame1": "the rusty lantern glows"},
                                                {"cuts": [{"prompt": "camera push toward the rusty lantern"}]}, {"frame1": "lantern"}]}, CFG)
        words = {x["word"]: x["scenes"] for x in pe.suggest_recurring(CFG, proj)}
        self.assertEqual(words.get("lantern"), 4)
        self.assertEqual(words.get("rusty"), 3)
        self.assertNotIn("camera", words)
        proj["assets"] = pe.normalize_assets([{"id": "l", "label": "the rusty lantern", "appearance": "x"}])
        self.assertNotIn("lantern", {x["word"] for x in pe.suggest_recurring(CFG, proj)})   # 이미 asset 인 단어는 제외

    def test_validator_asset_checks(self):
        proj = pe.normalize_project(RAMEN, CFG)
        proj["assets"].append({"id": "x", "type": "object", "name": "유령", "label": "한글 라벨", "appearance": "", "keywords": "", "done": False})
        codes = [(i["code"], i["level"]) for i in pe.validate_project(CFG, proj)]
        self.assertIn(("asset_empty", "warn"), codes)
        self.assertIn(("asset_cjk", "error"), codes)
        self.assertIn(("asset_unlinked", "warn"), codes)
        none = pe.normalize_project(RAMEN, CFG)
        none["assets"], none["scenes"] = [], [dict(s, refs=[]) for s in none["scenes"]]
        self.assertIn("no_assets", [i["code"] for i in pe.validate_project(CFG, none)])
        self.assertNotIn("no_assets", [i["code"] for i in pe.validate_project(CFG, pe.normalize_project(RAMEN, CFG))])

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
            self.assertEqual(j["refs"], pe.reference_prompts(CFG, p), f"reference prompts 불일치: {n}")
            self.assertEqual(j["asset_prompt"], pe.build_asset_prompt(CFG, p), f"asset prompt 불일치: {n}")
            self.assertEqual(j["linked"], pe.link_assets(p), f"link 불일치: {n}")
            self.assertEqual(j["suggest"], pe.suggest_recurring(CFG, p), f"suggest 불일치: {n}")
            if "assets_response" in case:
                pa_ = pe.parse_assets_response(case["assets_response"], CFG)
                self.assertEqual(j["parsed_assets"], pa_, "parse_assets 불일치")
                self.assertEqual(j["applied_assets"], pe.apply_assets(p, pa_), "apply_assets 불일치")
            if "response" in case:
                parsed = pe.parse_claude_response(case["response"], CFG)
                self.assertEqual(j["parsed"], parsed, "parse 불일치")
                self.assertEqual(j["applied"], pe.apply_response(p, parsed), "apply 불일치")


if __name__ == "__main__":
    unittest.main(verbosity=2)
