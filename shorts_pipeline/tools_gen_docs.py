#!/usr/bin/env python3
"""tools_gen_docs.py - samples/*.json + config.json 에서 docs/ 예시 문서를 자동 생성한다.
   python tools_gen_docs.py        (config.json / samples 를 고친 뒤 실행. config.js 도 함께 갱신)
"""
import json
import sys
from pathlib import Path

import prompt_engine as pe

BASE = Path(__file__).resolve().parent


def build_examples(cfg) -> str:
    out = ["# 프롬프트 예시 모음 (엔진 자동 생성)", "",
           "> 이 문서는 `python tools_gen_docs.py` 가 `samples/*.json` 과 `config.json` 에서 **자동 생성**합니다. 직접 고치지 말고 샘플/설정을 고친 뒤 다시 생성하세요.",
           "> 모든 Frame 프롬프트는 `화풍 앵커 → 그 씬에 등장하는 기준 이미지 대상의 외형 → 장면 묘사 → 안전 마진 → --no 접미사` 순서로 합성되고, Omni 프롬프트는 연결 문구와 화풍 질감이 자동 합성됩니다.", ""]
    for name in ("ramen_bgrade", "airfryer_shopping"):
        p = pe.normalize_project(json.loads((BASE / "samples" / f"{name}.json").read_text(encoding="utf-8")), cfg)
        m, st = p["meta"], cfg["styles"][p["meta"]["style"]]
        cats = cfg["categories"][m["category"]]["name"] + (f" + {cfg['categories'][m['category2']]['name']}" if m["category2"] else "")
        out += [f"## 케이스: {m['topic']}", "", f"- 카테고리: {cats}", f"- 화풍: {st['number']}. {st['name']}", f"- 상단 타이틀: {m['top_title']}",
                f"- 대본 분량: {pe.total_units(p, cfg)}자 (목표 320~350)", "",
                "### 6씬 대본 (2.5초 비트)", "", "| 씬 | 0.0~2.5s | 2.5~5.0s | 5.0~7.5s | 글자수 |", "|---|---|---|---|---|"]
        for i, sc in enumerate(p["scenes"], 1):
            out.append(f"| {i:02d} | " + " | ".join(sc["beats"]) + f" | {pe.count_units(pe.scene_text(sc), 'ko', cfg)} |")
        out.append("")
        out += ["### 기준 이미지 (등장 대상별 - 씬 이미지보다 먼저 생성)", ""]
        for r in pe.reference_prompts(cfg, p):
            out += [f"**{r['name'] or r['id']}** ({r['type']}) - 등장 씬: {', '.join(str(x) for x in r['scenes']) or '-'}", "",
                    "대표 1컷", "```", r["main"], "```", "3면 턴어라운드 시트(선택)", "```", r["sheet"], "```", ""]
        for i in range(6):
            pk = pe.scene_package(cfg, p, i)
            out += [f"### Scene {i + 1:02d} - {cfg['scene_roles'][i]['role']} ({cfg['scene_roles'][i]['time']})", "", f"**대사**: {pk['narration']}", "",
                    "**Frame 1 (0s)**", "```", pk["frame1"], "```", "**Frame 2 (2.5s)**", "```", pk["frame2"], "```",
                    "**Omni 1.2 (I2V, 7.5초)**", "```", pk["omni"], "```", ""]
        out += ["---", ""]
    return "\n".join(out)


def main() -> int:
    cfg = pe.load_config()
    docs = BASE / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "prompt_examples.md").write_text(build_examples(cfg), encoding="utf-8")
    shop = pe.normalize_project(json.loads((BASE / "samples" / "airfryer_shopping.json").read_text(encoding="utf-8")), cfg)
    (docs / "master_prompt_example_shopping.md").write_text(
        "# 마스터 프롬프트 예시 (쇼핑 · 단일 모드 · 한국어)\n\n> 대시보드 2단계 [마스터 프롬프트 복사]가 만드는 것과 동일한 텍스트입니다. Claude(웹/앱)에 그대로 붙여넣으세요.\n\n```text\n"
        + pe.build_master_prompt(cfg, shop) + "\n```\n", encoding="utf-8")
    print("written: docs/prompt_examples.md, docs/master_prompt_example_shopping.md,", pe.sync_config_js(cfg).name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
