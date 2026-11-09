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
  python prompt_engine.py refs     --project samples/ramen_bgrade.json      # 등장 대상별 기준 이미지 프롬프트
  python prompt_engine.py assets-prompt --project my.json                    # 대본 분석(등장 대상 추출) 프롬프트
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
    return {"id": i, "beats": ["", "", ""], "frame1": "", "frame2": "", "refs": [],
            "cuts": [{"type": "", "prompt": ""} for _ in range(3)]}


def default_project(cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    cfg = cfg or load_config()
    return {
        "version": 3,
        "meta": {
            "topic": "", "top_title": "", "category": cfg.get("default_category", "general"), "category2": "", "format": "",
            "style": default_style_id(cfg), "language": "ko", "source_url": "", "source_script": "",
        },
        "options": {"zero_text": True, "safe_margin": True},
        "assets": [],
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
    if "metadata" in p:
        out["metadata"] = p["metadata"]
    m = out["meta"]
    m["style"] = LEGACY_STYLE_KEYS.get(m["style"], m["style"])
    m["category"] = LEGACY_CATEGORY_KEYS.get(m["category"], m["category"])
    m["category2"] = LEGACY_CATEGORY_KEYS.get(m["category2"], m["category2"])
    if m["style"] not in cfg["styles"]:
        m["style"] = default_style_id(cfg)
    if m["category"] not in cfg["categories"]:
        m["category"] = cfg.get("default_category", "general")
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
    out["assets"] = normalize_assets(p.get("assets"))
    legacy = str(p.get("subject_anchor") or "").strip()
    if legacy and not out["assets"]:  # 옛 '주인공 외형 앵커' -> 모든 씬에 연결된 asset 1개
        out["assets"] = [{"id": "main", "type": "character", "name": "주인공/핵심 대상", "label": "", "appearance": strip_suffix(legacy).rstrip(" .,;"),
                          "keywords": "", "done": False}]
        for sc in out["scenes"]:
            sc["refs"] = ["main"]
    ids = [a["id"] for a in out["assets"]]
    for sc in out["scenes"]:
        sc["refs"] = [r for r in _uniq(sc["refs"]) if r in ids]
    return out


def _uniq(items: List[str]) -> List[str]:
    seen: List[str] = []
    for x in items:
        if x not in seen:
            seen.append(x)
    return seen


ASSET_TYPES = ("character", "object", "place")


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", (s or "").strip().lower()).strip("_")[:30]


def normalize_assets(items: Any) -> List[Dict[str, Any]]:
    """등장 대상(인물/사물/장소) 목록 정규화: id 중복 제거, 타입/외형/키워드 기본값."""
    out: List[Dict[str, Any]] = []
    used: set = set()
    for n, a in enumerate(items if isinstance(items, list) else [], start=1):
        if not isinstance(a, dict):
            continue
        base = _slug(str(a.get("id") or a.get("label") or "")) or f"asset{n}"
        aid, k = base, 2
        while aid in used:
            aid, k = f"{base}_{k}", k + 1
        used.add(aid)
        t = str(a.get("type") or "object").strip().lower()
        kw = a.get("keywords", "")
        if isinstance(kw, list):
            kw = ", ".join(str(x) for x in kw)
        out.append({"id": aid, "type": t if t in ASSET_TYPES else "object", "name": str(a.get("name") or "").strip(),
                    "label": str(a.get("label") or "").strip(), "appearance": strip_suffix(str(a.get("appearance") or "")),
                    "keywords": str(kw or "").strip(), "done": bool(a.get("done", False))})
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
    refs = src.get("refs")
    sc["refs"] = [str(x) for x in refs] if isinstance(refs, list) else []
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


def scene_assets(project: Dict[str, Any], refs: Optional[List[str]]) -> List[Dict[str, Any]]:
    ids = list(refs or [])
    return [a for a in project.get("assets", []) if a["id"] in ids]


def compose_frame(cfg: Dict[str, Any], project: Dict[str, Any], desc: str, refs: Optional[List[str]] = None) -> str:
    """화풍 앵커 -> 이 씬에 등장하는 기준 이미지 대상들의 외형 -> 장면 묘사 -> 안전 마진 -> --no 접미사."""
    style = cfg["styles"][project["meta"]["style"]]
    parts = [style["anchor"]]
    for a in scene_assets(project, refs):
        if a["appearance"].strip():
            parts.append(_trim(a["appearance"]))
    if (desc or "").strip():
        parts.append(_trim(desc))
    if project["options"].get("safe_margin", True):
        parts.append(cfg["suffix"]["safe_margin"])
    text = ", ".join(parts)
    if project["options"].get("zero_text", True):
        text += " " + cfg["suffix"]["zero_text"]
    return text


def compose_reference(cfg: Dict[str, Any], project: Dict[str, Any], asset: Dict[str, Any], kind: str = "main") -> str:
    """기준 이미지 프롬프트: kind='main'(대표 1컷, 9:16) | 'sheet'(3면 턴어라운드, 16:9)."""
    ref = cfg["reference"]
    parts = [cfg["styles"][project["meta"]["style"]]["anchor"]]
    if asset["appearance"].strip():
        parts.append(_trim(asset["appearance"]))
    parts.append(ref["types"][asset["type"]][kind])
    text = ", ".join(parts)
    if project["options"].get("zero_text", True):
        text += " " + cfg["suffix"]["zero_text_core"] + " --ar " + ref["ar_main" if kind == "main" else "ar_sheet"]
    return text


def reference_prompts(cfg: Dict[str, Any], project: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    for a in project.get("assets", []):
        scenes = [i + 1 for i, sc in enumerate(project["scenes"]) if a["id"] in sc.get("refs", [])]
        out.append({"id": a["id"], "type": a["type"], "name": a["name"], "label": a["label"], "scenes": scenes,
                    "main": compose_reference(cfg, project, a, "main"), "sheet": compose_reference(cfg, project, a, "sheet")})
    return out


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
        "frame1": compose_frame(cfg, project, sc["frame1"], sc.get("refs")),
        "frame2": compose_frame(cfg, project, sc["frame2"], sc.get("refs")),
        "omni": compose_omni(cfg, project, sc),
    }


def all_prompts_text(cfg: Dict[str, Any], project: Dict[str, Any]) -> str:
    st = cfg["styles"][project["meta"]["style"]]
    out = ["=" * 57, "AI SHORTS PROMPT EXPORT", f'Topic: {project["meta"]["topic"]}',
           f'Style: {st["number"]}. {st["name"]}', "Rule: 45s (6 scenes x 7.5s) | Method B (3 cuts x 2.5s)",
           f'Zero-Text: {"ENFORCED" if project["options"].get("zero_text", True) else "OFF"}',
           f'Safe margin (1.06x crop): {"APPLIED" if project["options"].get("safe_margin", True) else "OFF"}',
           "=" * 57, ""]
    for r in reference_prompts(cfg, project):
        out += [f"[기준 이미지] {r['name'] or r['id']} ({r['type']}) - 등장 씬: {', '.join(str(x) for x in r['scenes']) or '-'}", "",
                "[Reference - main]", r["main"], "", "[Reference - sheet]", r["sheet"], "", "-" * 57, ""]
    for i in range(len(project["scenes"])):
        pk = scene_package(cfg, project, i)
        out += [f"[Scene {i + 1:02d}]  narration: {pk['narration']}", "", "[Frame 1 (0s)]", pk["frame1"], "",
                "[Frame 2 (2.5s)]", pk["frame2"], "", "[Omni 1.2 video prompt]", pk["omni"], "", "-" * 57, ""]
    return "\n".join(out)


# --------------------------------------------------------------------------- master prompt
def _structure(cfg: Dict[str, Any], bp1: Dict[str, Any], bp2: Optional[Dict[str, Any]], has_src: bool = False) -> str:
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
    if has_src:
        lines.append("* 원본 대본의 구조적 리듬(훅 → 전개 → 반전)이 위 뼈대와 다르면 원본의 리듬을 우선하고, 위 뼈대는 보조 기준으로만 쓰세요.")
    return "\n".join(lines)


def _asset_rule(project: Dict[str, Any]) -> str:
    if not project.get("assets"):
        return ("- [기준 이미지 규칙] 2개 이상의 씬에 등장하거나 스토리의 핵심인 인물·사물·장소는 assets 배열에 정의하세요. "
                "각 asset: id(영문 소문자·숫자·_), type(character/object/place), name(한국어 이름), label(영문 짧은 호칭 예: the plastic cook figure), "
                "appearance(영문 외형 고정 키워드 - 성별·연령·체형·의상·색·재질·특징을 구체적으로, 배경·동작·화각은 제외), "
                "keywords(대본에서 이 대상을 가리키는 한국어 단어들을 쉼표로). 각 씬의 refs 에 그 씬에 등장하는 asset id 를 넣으세요. "
                "시스템이 appearance 를 해당 씬의 모든 프레임 프롬프트에 자동 삽입하고 기준 이미지 프롬프트도 자동 생성하므로, "
                "씬 묘사(frame/cuts)에서는 외형을 다시 설명하지 말고 label 로만 지칭합니다.")
    lines = ["- [기준 이미지 규칙] 이미 정의된 기준 이미지 대상입니다(그대로 유지하세요. 시스템이 외형을 해당 씬의 모든 프레임 프롬프트에 자동 삽입합니다):"]
    for a in project["assets"]:
        lines.append(f"  · {a['id']} ({a['type']}) {a['name']} / {a['label']}: {a['appearance']}")
    lines.append("  새로 필요한 반복 대상이 있으면 assets 에 추가하고, 씬 묘사(frame/cuts)에서는 외형을 다시 설명하지 말고 label 로만 지칭하세요. 각 씬의 refs 에 등장하는 asset id 를 넣으세요.")
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

    asset_rule = _asset_rule(project)

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
        "asset_rule": asset_rule,
        "structure": _structure(cfg, bp1, bp2, bool(src)),
        "format_block": format_block,
        "cta_block": cta_block,
        "topic": m["topic"] or "(미지정 - 원본과 겹치지 않는 새 소재를 직접 정해 주세요)",
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


# --------------------------------------------------------------------------- 기준 이미지(등장 대상) 분석
def build_asset_prompt(cfg: Dict[str, Any], project: Dict[str, Any]) -> str:
    st = cfg["styles"][project["meta"]["style"]]
    existing = ""
    if project.get("assets"):
        existing = "- 이미 정의된 asset(유지하고 필요한 것만 추가): " + ", ".join(f"{a['id']}={a['label'] or a['name']}" for a in project["assets"])
    lines = []
    for i, sc in enumerate(project["scenes"], start=1):
        lines.append(f"Scene {i:02d}: {scene_text(sc)}")
        lines.append(f"  frame1: {sc['frame1']}")
        lines.append(f"  frame2: {sc['frame2']}")
        lines.append("  cuts: " + " / ".join(c["prompt"] for c in sc["cuts"] if c["prompt"].strip()))
    return fill(cfg["asset_template"], {"style_name": f"{st['number']}. {st['name']} ({st['name_en']})",
                                        "existing_assets": existing, "scenes_text": "\n".join(lines)})


def parse_assets_response(text: str, cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    cfg = cfg or load_config()
    data = extract_json(text)
    if not isinstance(data, dict) or not isinstance(data.get("assets"), list):
        raise ValueError("응답에서 assets 배열이 있는 JSON 을 찾지 못했습니다.")
    refs: Dict[str, List[str]] = {}
    sr = data.get("scene_refs")
    if isinstance(sr, dict):
        for k, v in sr.items():
            try:
                i = int(k)
            except (TypeError, ValueError):
                continue
            if 1 <= i <= cfg["spec"]["scenes"] and isinstance(v, list):
                refs[str(i)] = [str(x) for x in v]
    return {"assets": normalize_assets(data["assets"]), "scene_refs": refs}


def apply_assets(project: Dict[str, Any], parsed: Dict[str, Any]) -> Dict[str, Any]:
    p = copy.deepcopy(project)
    done = {a["id"]: a.get("done", False) for a in p.get("assets", [])}
    p["assets"] = [dict(a, done=bool(done.get(a["id"], a.get("done", False)))) for a in parsed["assets"]]
    ids = [a["id"] for a in p["assets"]]
    for i, sc in enumerate(p["scenes"], start=1):
        src = parsed.get("scene_refs", {}).get(str(i), sc.get("refs", []))
        sc["refs"] = [r for r in _uniq(src) if r in ids]
    return p


def asset_tokens(a: Dict[str, Any]) -> List[str]:
    toks = [a["name"], a["label"]] + re.split(r"[,\n]+", a["keywords"])
    return [t.strip().lower() for t in toks if len(t.strip()) >= 2]


def link_assets(project: Dict[str, Any]) -> Dict[str, Any]:
    """대본/프롬프트에 asset 의 이름·라벨·키워드가 나오는 씬에 자동 연결 (기존 연결은 유지)."""
    p = copy.deepcopy(project)
    for sc in p["scenes"]:
        hay = " ".join([scene_text(sc), sc["frame1"], sc["frame2"]] + [c["prompt"] for c in sc["cuts"]]).lower()
        sc["refs"] = [a["id"] for a in p["assets"] if a["id"] in sc.get("refs", []) or any(t in hay for t in asset_tokens(a))]
    return p


def suggest_recurring(cfg: Dict[str, Any], project: Dict[str, Any], min_scenes: int = 3, limit: int = 12) -> List[Dict[str, Any]]:
    """여러 씬 프롬프트에 반복되는 영문 단어 힌트 (이미 asset 으로 정의된 단어 제외). 휴리스틱이므로 참고용."""
    stop = set(cfg.get("recurring_stop_words", []))
    covered: set = set()
    for a in project.get("assets", []):
        for t in asset_tokens(a):
            covered.update(re.findall(r"[a-z]{4,}", t))
    counts: Dict[str, int] = {}
    for sc in project["scenes"]:
        words: set = set()
        for txt in [sc["frame1"], sc["frame2"]] + [c["prompt"] for c in sc["cuts"]]:
            words.update(w for w in re.findall(r"[a-z]{4,}", (txt or "").lower()) if w not in stop and w not in covered)
        for w in words:
            counts[w] = counts.get(w, 0) + 1
    items = [{"word": w, "scenes": n} for w, n in counts.items() if n >= min_scenes]
    items.sort(key=lambda x: (-x["scenes"], x["word"]))
    return items[:limit]


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
    if isinstance(data.get("top_title"), str):
        out["top_title"] = data["top_title"].strip()
    if isinstance(data.get("assets"), list):
        out["assets"] = normalize_assets(data["assets"])
    elif isinstance(data.get("subject_anchor"), str) and data["subject_anchor"].strip():  # 옛 형식
        out["assets"] = normalize_assets([{"id": "main", "type": "character", "name": "주인공/핵심 대상", "appearance": data["subject_anchor"]}])
        for sc in out["scenes"]:
            sc["refs"] = ["main"]
    return out


def apply_response(project: Dict[str, Any], parsed: Dict[str, Any]) -> Dict[str, Any]:
    p = copy.deepcopy(project)
    p["scenes"] = parsed["scenes"]
    for k in ("analysis", "plan"):
        if k in parsed:
            p[k].update(parsed[k])
    if parsed.get("top_title"):
        p["meta"]["top_title"] = parsed["top_title"]
    if "assets" in parsed:
        done = {a["id"]: a.get("done", False) for a in p.get("assets", [])}
        p["assets"] = [dict(a, done=bool(done.get(a["id"], a.get("done", False)))) for a in parsed["assets"]]
    ids = [a["id"] for a in p.get("assets", [])]
    for sc in p["scenes"]:
        sc["refs"] = [r for r in _uniq(sc.get("refs", [])) if r in ids]
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

    linked = {r for sc in project["scenes"] for r in sc.get("refs", [])}
    for a in project.get("assets", []):
        nm = a["name"] or a["id"]
        if not a["appearance"].strip():
            add("warn", "asset_empty", f"기준 이미지 '{nm}': 외형 묘사(appearance)가 비어 있습니다.")
        if CJK_RE.search(a["appearance"]) or CJK_RE.search(a["label"]):
            add("error", "asset_cjk", f"기준 이미지 '{nm}': 외형/라벨은 영문만 허용(Zero-Text).")
        if a["id"] not in linked:
            add("warn", "asset_unlinked", f"기준 이미지 '{nm}'이(가) 어느 씬에도 연결되지 않았습니다.")
    if not project.get("assets") and any(sc["frame1"].strip() for sc in project["scenes"]):
        add("warn", "no_assets", "등장인물/사물 기준 이미지가 없습니다. '기준 이미지' 단계에서 대본을 분석해 정의하세요(씬마다 외형이 달라지는 원인).")

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
    ap.add_argument("cmd", choices=["master", "package", "validate", "metadata", "parse", "sync-config", "cta", "assets-prompt", "refs"])
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
    elif a.cmd == "assets-prompt":
        print(build_asset_prompt(cfg, proj))
    elif a.cmd == "refs":
        for r in reference_prompts(cfg, proj):
            print(f"[{r['id']}] {r['name']} ({r['type']}) 등장 씬: {r['scenes']}\n  main : {r['main']}\n  sheet: {r['sheet']}\n")
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
