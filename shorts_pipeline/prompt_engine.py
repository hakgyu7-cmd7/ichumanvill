#!/usr/bin/env python3
"""
prompt_engine.py  -  AI 쇼츠 파이프라인 대본/프롬프트/메타데이터 엔진 (v3)

모든 규칙(45초 1.2배속 6씬, 방법 B 2.5초 컷, 7대 화풍 앵커, Zero-Text, 1.06배 크롭 안전 마진,
쇼핑 CTA, 12개 카테고리 + 합성, 4개국어, 3대 플랫폼 메타데이터)은 config.json 한 곳에 있고,
pipeline_core.js(웹 대시보드)가 같은 템플릿을 같은 방식으로 채웁니다.
두 구현이 어긋나지 않는지는 tests/test_pipeline.py 가 검증합니다.

CLI
  python prompt_engine.py master   --project samples/ramen_bgrade.json
  python prompt_engine.py package  --project samples/ramen_bgrade.json      # 씬별 Frame1/Frame2/Omni 완성 프롬프트
  python prompt_engine.py validate --project samples/ramen_bgrade.json
  python prompt_engine.py metadata --project samples/ramen_bgrade.json --langs ko,en
  python prompt_engine.py parse    --response claude_reply.txt --project my.json   # Claude 응답(JSON) 가져오기
  python prompt_engine.py sync-config                                             # config.json -> config.js
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE = Path(__file__).resolve().parent
CONFIG_PATH = BASE / "config.json"
CONFIG_JS_PATH = BASE / "config.js"

# 제미나이 시절 한글 키 -> 현재 식별자 (옛 JSON/코드 호환)
LEGACY_STYLE_KEYS = {
    "피규어_디오라마": "diorama", "시네마틱_실사": "cinematic", "클레이메이션": "claymation",
    "스톱모션_클레이": "claymation", "3D_CGI": "hyperreal_3d", "빈티지_흑백": "vintage_1930",
    "과학_매크로": "macro_medical", "미니멀_광고": "minimal_ad", "vintage_1930s": "vintage_1930",
}
LEGACY_CATEGORY_KEYS = {
    "쇼핑_꿀템": "shopping", "역사_비화": "history", "재난_시뮬레이션": "disaster", "재난_시뮬": "disaster",
    "B급_병맛": "bgrade", "인체_뇌과학": "body_brain", "건축_공간공학": "architecture",
}

BANNED_PROMPT_WORDS = [
    "text", "texts", "letter", "letters", "word", "words", "caption", "subtitle", "subtitles",
    "signage", "sign", "signs", "writing", "written", "typography", "font", "logo", "logos",
    "label", "banner", "headline", "headlines", "poster", "newspaper", "slogan", "handwriting",
]
EXTREME_CLOSEUP_RE = re.compile(r"\b(extreme|tight)[- ](close[- ]?up|macro)\b|\bmacro close[- ]?up\b", re.I)
CJK_RE = re.compile(r"[ᄀ-ᇿ぀-ヿ㄰-㆏㐀-䶿一-鿿가-힯]")
TIME_MARKER_RE = re.compile(r"^\s*\[[^\]]*\]\s*")


# --------------------------------------------------------------------------- config
def load_config(path: Path = CONFIG_PATH) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sync_config_js(cfg: Optional[Dict[str, Any]] = None) -> Path:
    """config.json + data/trends_seed.json + samples/*.json -> config.js
    (file:// 로 열어도 대시보드가 같은 규칙/샘플/시드를 쓰도록 window 전역 변수로 내보낸다)."""
    cfg = cfg or load_config()
    seed = json.loads((BASE / "data" / "trends_seed.json").read_text(encoding="utf-8"))
    samples = {p.stem: normalize_project(json.loads(p.read_text(encoding="utf-8")), cfg)
               for p in sorted((BASE / "samples").glob("*.json"))}
    dump = lambda o: json.dumps(o, ensure_ascii=False, indent=1)  # noqa: E731
    CONFIG_JS_PATH.write_text(
        "/* 자동 생성 파일: python prompt_engine.py sync-config  (config.json / samples / data 를 수정한 뒤 실행) */\n"
        f"window.PIPELINE_CONFIG = {dump(cfg)};\n"
        f"window.PIPELINE_SEED = {dump(seed)};\n"
        f"window.PIPELINE_SAMPLES = {dump(samples)};\n", encoding="utf-8")
    return CONFIG_JS_PATH


# --------------------------------------------------------------------------- template
def fill(lines: List[str], values: Dict[str, str]) -> str:
    """{{key}} 치환. 한 줄이 '{{key}}' 하나뿐이고 값이 비어 있으면 그 줄을 지운다."""
    out: List[str] = []
    for line in lines:
        m = re.fullmatch(r"\s*\{\{(\w+)\}\}\s*", line)
        if m and m.group(1) in values and values[m.group(1)] == "":
            continue
        out.append(re.sub(r"\{\{(\w+)\}\}", lambda mm: str(values.get(mm.group(1), mm.group(0))), line))
    return "\n".join(out)


# --------------------------------------------------------------------------- project model
def default_style_id(cfg: Dict[str, Any]) -> str:
    for k, v in cfg["styles"].items():
        if v.get("default"):
            return k
    return next(iter(cfg["styles"]))


def empty_scene(i: int) -> Dict[str, Any]:
    return {"id": i, "beats": ["", "", ""], "frame1": "", "frame2": "",
            "cuts": [{"type": "", "prompt": ""} for _ in range(3)]}


def default_project(cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    cfg = cfg or load_config()
    return {
        "version": 3,
        "meta": {
            "topic": "", "top_title": "", "category": "shopping", "category2": "", "format": "",
            "style": default_style_id(cfg), "language": "ko", "source_url": "", "source_script": "",
        },
        "options": {"zero_text": True, "safe_margin": True},
        "subject_anchor": "",
        "analysis": {"hook_technique": "", "retention_psychology": "", "skeleton": ""},
        "plan": {"titles": [], "description": "", "hashtags": []},
        "scenes": [empty_scene(i) for i in range(1, cfg["spec"]["scenes"] + 1)],
        "render": {"crop_scale": cfg["spec"]["crop_scale"], "fit": "cover",
                   "sub_size": cfg["layout"]["sub_size"], "sub_chars_per_line": cfg["layout"]["sub_chars_per_line"]},
        "metadata": {},
    }


def normalize_project(p: Dict[str, Any], cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """누락 필드를 기본값으로 채우고 옛 키(제미나이 시절)를 변환."""
    cfg = cfg or load_config()
    base = default_project(cfg)
    out = copy.deepcopy(base)
    for k in ("meta", "options", "analysis", "plan", "render"):
        if isinstance(p.get(k), dict):
            out[k].update(p[k])
    for k in ("subject_anchor", "metadata"):
        if k in p:
            out[k] = p[k]
    m = out["meta"]
    m["style"] = LEGACY_STYLE_KEYS.get(m["style"], m["style"])
    m["category"] = LEGACY_CATEGORY_KEYS.get(m["category"], m["category"])
    m["category2"] = LEGACY_CATEGORY_KEYS.get(m["category2"], m["category2"])
    if m["style"] not in cfg["styles"]:
        m["style"] = default_style_id(cfg)
    if m["category"] not in cfg["categories"]:
        m["category"] = "shopping"
    if m["category2"] not in cfg["categories"]:
        m["category2"] = ""
    if m["language"] not in cfg["languages"]:
        m["language"] = "ko"
    n = cfg["spec"]["scenes"]
    scenes = p.get("scenes") if isinstance(p.get("scenes"), list) else []
    out["scenes"] = []
    for i in range(n):
        src = scenes[i] if i < len(scenes) and isinstance(scenes[i], dict) else {}
        out["scenes"].append(_normalize_scene(src, i + 1))
    return out


def strip_time_marker(s: str) -> str:
    return TIME_MARKER_RE.sub("", s or "").strip()


def strip_suffix(s: str) -> str:
    """Claude 가 붙였을 수 있는 --no / --ar 접미사 제거 (시스템이 다시 붙인다)."""
    return re.sub(r"\s*--(?:no|ar)\b.*$", "", (s or "").strip(), flags=re.I | re.S).strip()


def _split_narration(s: str) -> List[str]:
    parts = [x.strip() for x in re.split(r"\[[^\]]*s\]", s) if x.strip()]
    return parts


def _normalize_scene(src: Dict[str, Any], i: int) -> Dict[str, Any]:
    sc = empty_scene(i)
    beats = src.get("beats")
    if not isinstance(beats, list):
        nar = src.get("narration") or src.get("script") or ""
        if isinstance(nar, list):
            beats = nar
        elif isinstance(nar, str) and nar.strip():
            beats = _split_narration(nar) or [nar.strip()]
        else:
            beats = []
    beats = [strip_time_marker(str(b)) for b in beats][:3]
    sc["beats"] = beats + [""] * (3 - len(beats))
    sc["frame1"] = strip_suffix(src.get("frame1") or src.get("frame_1") or src.get("frame1_prompt") or "")
    sc["frame2"] = strip_suffix(src.get("frame2") or src.get("frame_2") or src.get("frame2_prompt") or "")
    cuts = src.get("cuts") if isinstance(src.get("cuts"), list) else src.get("angles") or []
    for j in range(3):
        c = cuts[j] if j < len(cuts) else {}
        if isinstance(c, str):
            c = {"type": "", "prompt": c}
        sc["cuts"][j] = {"type": str(c.get("type", "") or ""), "prompt": strip_suffix(str(c.get("prompt", "") or ""))}
    if "done" in src:
        sc["done"] = src["done"]
    return sc


# --------------------------------------------------------------------------- counting
def scene_text(scene: Dict[str, Any]) -> str:
    return " ".join(b.strip() for b in scene.get("beats", []) if b and b.strip())


def count_units(text: str, lang: str, cfg: Dict[str, Any]) -> int:
    unit = cfg["languages"][lang]["unit"]
    if lang == "ko":
        return len(text)
    if unit == "words":
        return len(re.findall(r"\S+", text))
    return len(re.sub(r"\s+", "", text))


def total_units(project: Dict[str, Any], cfg: Dict[str, Any]) -> int:
    lang = project["meta"]["language"]
    return sum(count_units(scene_text(s), lang, cfg) for s in project["scenes"])


def is_shopping(project: Dict[str, Any], cfg: Dict[str, Any]) -> bool:
    m = project["meta"]
    return any(cfg["categories"].get(k, {}).get("shopping") for k in (m["category"], m["category2"]) if k)


# --------------------------------------------------------------------------- prompt composition
def _trim(s: str) -> str:
    return re.sub(r"[\s.,;]+$", "", (s or "").strip())


def _sentence(s: str) -> str:
    s = (s or "").strip()
    return s if not s or re.search(r"[.!?]$", s) else s + "."


def compose_frame(cfg: Dict[str, Any], project: Dict[str, Any], desc: str) -> str:
    style = cfg["styles"][project["meta"]["style"]]
    parts = [style["anchor"]]
    if project.get("subject_anchor", "").strip():
        parts.append(_trim(project["subject_anchor"]))
    if (desc or "").strip():
        parts.append(_trim(desc))
    if project["options"].get("safe_margin", True):
        parts.append(cfg["suffix"]["safe_margin"])
    text = ", ".join(parts)
    if project["options"].get("zero_text", True):
        text += " " + cfg["suffix"]["zero_text"]
    return text


def compose_omni(cfg: Dict[str, Any], project: Dict[str, Any], scene: Dict[str, Any]) -> str:
    style = cfg["styles"][project["meta"]["style"]]
    om = cfg["omni"]
    zero = project["options"].get("zero_text", True)
    safe = project["options"].get("safe_margin", True)
    lines = [om["header"] + (om["header_zero"] if zero else "") + ":", ""]
    for i in range(3):
        c = scene["cuts"][i] if i < len(scene["cuts"]) else {"prompt": ""}
        lines.append(f'{cfg["time_labels"][i]}: {cfg["cut_connectors"][i]} {_sentence(c.get("prompt", ""))}'.rstrip())
        lines.append("")
    polish = [style["video_feel"], om["polish_base"]]
    if safe:
        polish.append(om["polish_safe"])
    if zero:
        polish.append(om["polish_zero"])
    lines.append("Visual Polish: " + ", ".join(polish) + ".")
    return "\n".join(lines)


def scene_package(cfg: Dict[str, Any], project: Dict[str, Any], idx: int) -> Dict[str, str]:
    sc = project["scenes"][idx]
    return {
        "narration": scene_text(sc),
        "frame1": compose_frame(cfg, project, sc["frame1"]),
        "frame2": compose_frame(cfg, project, sc["frame2"]),
        "omni": compose_omni(cfg, project, sc),
    }


def all_prompts_text(cfg: Dict[str, Any], project: Dict[str, Any]) -> str:
    st = cfg["styles"][project["meta"]["style"]]
    out = ["=" * 57, "AI SHORTS PROMPT EXPORT", f'Topic: {project["meta"]["topic"]}',
           f'Style: {st["number"]}. {st["name"]}', "Rule: 45s (6 scenes x 7.5s) | Method B (3 cuts x 2.5s)",
           f'Zero-Text: {"ENFORCED" if project["options"].get("zero_text", True) else "OFF"}',
           f'Safe margin (1.06x crop): {"APPLIED" if project["options"].get("safe_margin", True) else "OFF"}',
           "=" * 57, ""]
    for i in range(len(project["scenes"])):
        pk = scene_package(cfg, project, i)
        out += [f"[Scene {i + 1:02d}]  narration: {pk['narration']}", "", "[Frame 1 (0s)]", pk["frame1"], "",
                "[Frame 2 (2.5s)]", pk["frame2"], "", "[Omni 1.2 video prompt]", pk["omni"], "", "-" * 57, ""]
    return "\n".join(out)


# --------------------------------------------------------------------------- master prompt
def _structure(cfg: Dict[str, Any], bp1: Dict[str, Any], bp2: Optional[Dict[str, Any]]) -> str:
    keys = cfg["blueprint_keys"]
    roles = cfg["scene_roles"]
    lines = []
    for i, (k, label) in enumerate(keys):
        t = roles[i]["time"]
        if bp2 is None:
            lines.append(f"- [Scene {i + 1:02d} / {t}] {label}: {bp1[k]}")
        elif i < 3:
            lines.append(f"- [Scene {i + 1:02d} / {t} (1차)] {label}: {bp1[k]}")
        else:
            tag = ["2차 전환", "2차 반전", "2차 착지"][i - 3]
            lines.append(f"- [Scene {i + 1:02d} / {t} ({tag})] {label}: {bp2[k]}")
    if bp2 is not None:
        lines.append(f"* 연출 지침: 초반 22.5초까지는 '{bp1['name']}'의 톤으로 몰입시키고, "
                     f"22.5초 이후부터 '{bp2['name']}'의 문법으로 급커브를 틀어 시청자에게 강렬한 인상을 남길 것.")
    return "\n".join(lines)


def build_master_prompt(cfg: Dict[str, Any], project: Dict[str, Any]) -> str:
    m = project["meta"]
    lang = cfg["languages"][m["language"]]
    style = cfg["styles"][m["style"]]
    bp1 = cfg["categories"][m["category"]]
    bp2 = cfg["categories"][m["category2"]] if m["category2"] and m["category2"] != m["category"] else None
    spec = cfg["spec"]
    src = (m.get("source_script") or "").strip()[:6000]
    url = (m.get("source_url") or "").strip()
    shop = is_shopping(project, cfg)

    if src:
        task = ("제공된 [원본 벤치마킹 대본]의 구조적 성공 공식(훅·시청 유지 심리·반전 구조)을 역설계(Reverse-Engineering)한 뒤, "
                "내용은 그대로 베끼지 말고 '왜 떡상했는지'의 뼈대만 복제해 아래 [타깃 소재]로 완전히 새로 재구성하세요.")
    else:
        task = "원본 소스 대본이 없으므로, 선택한 카테고리의 스토리 뼈대를 바탕으로 [타깃 소재]에 맞춰 처음부터 대본을 설계하세요."

    if project.get("subject_anchor", "").strip():
        subject_rule = (f"- 주인공/제품 외형 앵커(전 씬 고정, 시스템이 모든 프레임 프롬프트에 자동 삽입): {project['subject_anchor'].strip()}. "
                        "씬 묘사에서 외형을 다시 설명하지 말고 같은 대상이 일관되게 등장한다는 전제로 행동과 구도만 쓰세요.")
    else:
        subject_rule = ("- 주인공/제품이 반복 등장하면 subject_anchor에 영문 외형 키워드(성별·연령·의상·색·재질)를 한 번만 정의하세요. "
                        "시스템이 모든 프레임 프롬프트에 자동 삽입해 씬마다 외형이 달라지지 않게 합니다.")

    fmt = cfg["formats"].get(m.get("format", ""))
    format_block = f"- 트렌드 포맷 적용: {fmt['name']} ({fmt['keywords']}) - {fmt['guide']}" if fmt else ""
    cta_block = (f"- [쇼핑 카테고리 전용 필수 규칙] Scene 06의 마지막 beat에 다음 의미의 제휴 전환 문구를 {lang['name']}로 자연스럽게 넣을 것: \"{lang['cta']}\""
                 if shop else "")

    if bp2 is None:
        category_line = f"{bp1['name']} (단일 모드)"
    else:
        category_line = f"1차 {bp1['name']} + 2차 {bp2['name']} (합성 크로스오버)"

    source_line = ("아래 [원본 벤치마킹 대본]" if src else "없음 (카테고리 뼈대로 신규 설계)") + (f" (URL: {url})" if url else "")
    source_block = f'### 원본 벤치마킹 대본\n"""\n{src}\n"""' if src else ""

    cut_plan = "\n".join(f"  - Scene {r['id']:02d} ({r['time']}) {r['role']}: {r['cuts']}" for r in cfg["scene_roles"])
    camera_lib = "\n".join(f"  - {x}" for x in cfg["camera_library"])

    schema = fill(cfg["schema_template"], {"lang_name": lang["name"]})
    return fill(cfg["master_template"], {
        "task_line": task,
        "length_rule": lang["length_rule"],
        "lang_desc": lang["desc"],
        "crop_scale": f"{spec['crop_scale']:g}",
        "safe_pct": str(spec["safe_zone_pct"]),
        "margin_pct": str(spec["margin_pct"]),
        "cut_plan": cut_plan,
        "camera_lib": camera_lib,
        "style_name": f"{style['number']}. {style['name']} ({style['name_en']})",
        "subject_rule": subject_rule,
        "structure": _structure(cfg, bp1, bp2),
        "format_block": format_block,
        "cta_block": cta_block,
        "topic": m["topic"] or "(미입력)",
        "category_line": category_line,
        "source_line": source_line,
        "source_block": source_block,
        "schema": schema,
    })


def recommended_model(cfg: Dict[str, Any], project: Dict[str, Any], task: str = "script") -> Dict[str, str]:
    if task == "metadata":
        return cfg["models"]["metadata"]
    m = project["meta"]
    if m.get("category2") and m["category2"] != m["category"]:
        return cfg["models"]["crossover"]
    return cfg["models"]["default"]


# --------------------------------------------------------------------------- metadata prompt
def build_metadata_prompt(cfg: Dict[str, Any], project: Dict[str, Any], languages: List[str]) -> str:
    m = project["meta"]
    shop = is_shopping(project, cfg)
    bp1 = cfg["categories"][m["category"]]
    bp2 = cfg["categories"][m["category2"]] if m["category2"] and m["category2"] != m["category"] else None
    category_line = bp1["name"] if bp2 is None else f"{bp1['name']} + {bp2['name']}"
    pin = " (쇼핑 카테고리: 쇼핑 태그/프로필 링크 구매 유도 문구 필수)" if shop else ""
    rules = "\n".join(f"  - {p['name']}: {p['rule'].replace('{{shopping_pin}}', pin)}" for p in cfg["platforms"].values())
    note = ("- 쇼핑 카테고리이므로 고정댓글에는 반드시 구매 유도 문구를 넣고 플랫폼별 위치 안내를 맞추세요 "
            "(YouTube: 하단 쇼핑 태그·고정댓글 링크 / Instagram: 프로필 링크 / TikTok: 좌측 하단 노란 장바구니)." if shop else "")
    script = "\n".join(f"Scene {i + 1:02d}: {scene_text(s)}" for i, s in enumerate(project["scenes"]))
    langs = ", ".join(f"{k}({cfg['languages'][k]['name']})" for k in languages if k in cfg["languages"])
    return fill(cfg["metadata_template"], {
        "category_line": category_line, "topic": m["topic"] or "(미입력)", "languages": langs,
        "platform_rules": rules, "shopping_note": note, "script": script,
    })


# --------------------------------------------------------------------------- Claude response import
def extract_json(text: str) -> Optional[Any]:
    for blk in re.findall(r"```(?:json|JSON)?\s*([\s\S]*?)```", text or ""):
        try:
            return json.loads(blk)
        except ValueError:
            continue
    a, b = (text or "").find("{"), (text or "").rfind("}")
    if a >= 0 and b > a:
        try:
            return json.loads(text[a:b + 1])
        except ValueError:
            return None
    return None


def parse_claude_response(text: str, cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Claude 의 JSON 응답 -> 프로젝트 조각(analysis/plan/top_title/subject_anchor/scenes)."""
    cfg = cfg or load_config()
    data = extract_json(text)
    if not isinstance(data, dict) or not isinstance(data.get("scenes"), list):
        raise ValueError("응답에서 scenes 배열이 있는 JSON 을 찾지 못했습니다.")
    out: Dict[str, Any] = {"scenes": [_normalize_scene(s if isinstance(s, dict) else {}, i + 1)
                                       for i, s in enumerate(data["scenes"][: cfg["spec"]["scenes"]])]}
    while len(out["scenes"]) < cfg["spec"]["scenes"]:
        out["scenes"].append(empty_scene(len(out["scenes"]) + 1))
    for k in ("analysis", "plan"):
        if isinstance(data.get(k), dict):
            out[k] = data[k]
    for k in ("top_title", "subject_anchor"):
        if isinstance(data.get(k), str):
            out[k] = data[k].strip()
    return out


def apply_response(project: Dict[str, Any], parsed: Dict[str, Any]) -> Dict[str, Any]:
    p = copy.deepcopy(project)
    p["scenes"] = parsed["scenes"]
    for k in ("analysis", "plan"):
        if k in parsed:
            p[k].update(parsed[k])
    if parsed.get("top_title"):
        p["meta"]["top_title"] = parsed["top_title"]
    if parsed.get("subject_anchor"):
        p["subject_anchor"] = parsed["subject_anchor"]
    return p


# --------------------------------------------------------------------------- validation
def validate_project(cfg: Dict[str, Any], project: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []

    def add(level: str, code: str, msg: str, scene: Optional[int] = None) -> None:
        issues.append({"level": level, "code": code, "msg": msg, "scene": scene})

    m = project["meta"]
    lang = cfg["languages"][m["language"]]
    unit = "단어" if lang["unit"] == "words" else "자"
    n = len(project["scenes"])
    if n != cfg["spec"]["scenes"]:
        add("error", "scene_count", f"씬이 {n}개입니다. 정확히 {cfg['spec']['scenes']}개여야 합니다.")
    total = total_units(project, cfg)
    if total == 0:
        add("warn", "empty_script", "대본이 비어 있습니다.")
    elif total < lang["min"] or total > lang["max"]:
        add("error", "total_chars", f"총 {total}{unit} - 목표 {lang['min']}~{lang['max']}{unit} 범위를 벗어났습니다 (45초 1.2배속 기준).")
    else:
        add("ok", "total_chars", f"총 {total}{unit} (목표 {lang['min']}~{lang['max']}{unit})")

    for i, sc in enumerate(project["scenes"], start=1):
        filled = [b for b in sc["beats"] if b.strip()]
        if total and len(filled) != 3:
            add("error", "beats", f"Scene {i:02d}: 비트가 {len(filled)}개입니다 (3개 필요: 0~2.5s / 2.5~5s / 5~7.5s).", i)
        u = count_units(scene_text(sc), m["language"], cfg)
        if total and (u < lang["scene_min"] or u > lang["scene_max"]):
            add("warn", "scene_chars", f"Scene {i:02d}: {u}{unit} (권장 {lang['scene_min']}~{lang['scene_max']}{unit})", i)
        prompts = [("frame1", sc["frame1"]), ("frame2", sc["frame2"])] + [(f"cut{j + 1}", c["prompt"]) for j, c in enumerate(sc["cuts"])]
        has_any = any(p.strip() for _, p in prompts)
        for name, ptxt in prompts:
            if has_any and not ptxt.strip():
                add("error", "prompt_missing", f"Scene {i:02d}: {name} 프롬프트가 비어 있습니다.", i)
                continue
            if CJK_RE.search(ptxt):
                add("error", "zero_text_cjk", f"Scene {i:02d} {name}: 한글/일문/중문 문자가 있습니다. 프롬프트는 영문만 허용(Zero-Text).", i)
            words = sorted({w for w in re.findall(r"[A-Za-z]+", ptxt.lower()) if w in BANNED_PROMPT_WORDS})
            if words:
                add("warn", "zero_text_word", f"Scene {i:02d} {name}: 문자 연상 단어 {', '.join(words)} - AI가 글자를 그려 넣을 수 있습니다.", i)
            if EXTREME_CLOSEUP_RE.search(ptxt):
                add("warn", "extreme_closeup", f"Scene {i:02d} {name}: 익스트림 클로즈업은 1.06배 크롭 시 피사체 잘림 위험 (Medium close-up + 여백 권장).", i)
        for j, c in enumerate(sc["cuts"]):
            if EXTREME_CLOSEUP_RE.search(c.get("type", "")):
                add("warn", "extreme_closeup", f"Scene {i:02d} cut{j + 1} 화각 '{c['type']}': 안전 마진 규칙과 충돌합니다.", i)

    if is_shopping(project, cfg) and n:
        last = scene_text(project["scenes"][-1]).lower()
        if not all(mk.lower() in last for mk in lang["cta_markers"]):
            add("error", "cta", f"쇼핑 카테고리인데 Scene 06에 쇼핑 CTA({lang['cta']})가 없습니다.")
        else:
            add("ok", "cta", "Scene 06 쇼핑 CTA 확인")
    if not project["meta"].get("top_title", "").strip():
        add("warn", "top_title", "상단 노란 타이틀 문구가 비어 있습니다.")
    return issues


def inject_cta(cfg: Dict[str, Any], project: Dict[str, Any]) -> Dict[str, Any]:
    """Scene 06 마지막 비트 끝에 CTA 문장을 덧붙인다 (이미 있으면 그대로)."""
    p = copy.deepcopy(project)
    lang = cfg["languages"][p["meta"]["language"]]
    last = p["scenes"][-1]
    if all(mk.lower() in scene_text(last).lower() for mk in lang["cta_markers"]):
        return p
    idx = 2
    base = last["beats"][idx].strip()
    last["beats"][idx] = (base + " " + lang["cta"]).strip()
    return p


# --------------------------------------------------------------------------- CLI
def _load_project(path: Optional[str], cfg: Dict[str, Any]) -> Dict[str, Any]:
    if not path:
        return default_project(cfg)
    with open(path, encoding="utf-8") as f:
        return normalize_project(json.load(f), cfg)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="AI 쇼츠 파이프라인 프롬프트 엔진")
    ap.add_argument("cmd", choices=["master", "package", "validate", "metadata", "parse", "sync-config", "cta"])
    ap.add_argument("--project", help="프로젝트 JSON (대시보드에서 내보낸 파일 / samples/*.json)")
    ap.add_argument("--response", help="Claude 응답 텍스트 파일 (parse 용)")
    ap.add_argument("--langs", default="ko", help="metadata 대상 언어 (예: ko,en,ja,zh)")
    ap.add_argument("--topic"); ap.add_argument("--category"); ap.add_argument("--category2")
    ap.add_argument("--style"); ap.add_argument("--lang"); ap.add_argument("--source", help="벤치마킹 대본 텍스트 파일")
    a = ap.parse_args(argv)
    cfg = load_config()
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")  # Windows 콘솔
        except Exception:
            pass

    if a.cmd == "sync-config":
        print("written:", sync_config_js(cfg))
        return 0
    proj = _load_project(a.project, cfg)
    for k, key in (("topic", "topic"), ("category", "category"), ("category2", "category2"), ("style", "style"), ("lang", "language")):
        v = getattr(a, k)
        if v:
            proj["meta"][key] = v
    if a.source:
        proj["meta"]["source_script"] = Path(a.source).read_text(encoding="utf-8")
    proj = normalize_project(proj, cfg)

    if a.cmd == "master":
        print(build_master_prompt(cfg, proj))
    elif a.cmd == "package":
        print(all_prompts_text(cfg, proj))
    elif a.cmd == "metadata":
        print(build_metadata_prompt(cfg, proj, [x.strip() for x in a.langs.split(",") if x.strip()]))
    elif a.cmd == "cta":
        print(json.dumps(inject_cta(cfg, proj), ensure_ascii=False, indent=2))
    elif a.cmd == "parse":
        if not a.response:
            ap.error("--response 가 필요합니다")
        merged = apply_response(proj, parse_claude_response(Path(a.response).read_text(encoding="utf-8"), cfg))
        out = a.project or "project_from_claude.json"
        Path(out).write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
        print("saved:", out)
    elif a.cmd == "validate":
        icons = {"ok": "[OK]  ", "warn": "[WARN]", "error": "[ERR] ", "info": "[i]   "}
        bad = 0
        for it in validate_project(cfg, proj):
            print(icons[it["level"]], it["msg"])
            bad += it["level"] == "error"
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
