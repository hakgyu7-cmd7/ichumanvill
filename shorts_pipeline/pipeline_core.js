/*
 * pipeline_core.js - prompt_engine.py 와 동일한 로직의 브라우저/Node 공용 구현 (DOM 의존 없음).
 * 규칙/템플릿은 config.js(= config.json) 에서만 가져온다. 두 구현이 같은 출력을 내는지는
 * tests/test_pipeline.py (parity 테스트)가 검증한다. 로직을 바꿀 때는 Python 쪽도 함께 바꿀 것.
 */
(function (root, factory) {
  const core = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = core;
  else root.PipelineCore = core;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const LEGACY_STYLE_KEYS = {
    '피규어_디오라마': 'diorama', '시네마틱_실사': 'cinematic', '클레이메이션': 'claymation',
    '스톱모션_클레이': 'claymation', '3D_CGI': 'hyperreal_3d', '빈티지_흑백': 'vintage_1930',
    '과학_매크로': 'macro_medical', '미니멀_광고': 'minimal_ad', 'vintage_1930s': 'vintage_1930'
  };
  const LEGACY_CATEGORY_KEYS = {
    '쇼핑_꿀템': 'shopping', '역사_비화': 'history', '재난_시뮬레이션': 'disaster', '재난_시뮬': 'disaster',
    'B급_병맛': 'bgrade', '인체_뇌과학': 'body_brain', '건축_공간공학': 'architecture'
  };
  const BANNED_PROMPT_WORDS = ['text', 'texts', 'letter', 'letters', 'word', 'words', 'caption', 'subtitle', 'subtitles',
    'signage', 'sign', 'signs', 'writing', 'written', 'typography', 'font', 'logo', 'logos',
    'label', 'banner', 'headline', 'headlines', 'poster', 'newspaper', 'slogan', 'handwriting'];
  const EXTREME_CLOSEUP_RE = /\b(extreme|tight)[- ](close[- ]?up|macro)\b|\bmacro close[- ]?up\b/i;
  const CJK_RE = /[ᄀ-ᇿ぀-ヿ㄰-㆏㐀-䶿一-鿿가-힯]/;
  const TIME_MARKER_RE = /^\s*\[[^\]]*\]\s*/;

  const clone = (o) => JSON.parse(JSON.stringify(o));
  const has = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
  const ulen = (s) => Array.from(s).length;

  // ------------------------------------------------------------------ template
  function fill(lines, values) {
    const out = [];
    for (const line of lines) {
      const m = /^\s*\{\{(\w+)\}\}\s*$/.exec(line);
      if (m && has(values, m[1]) && values[m[1]] === '') continue;
      out.push(line.replace(/\{\{(\w+)\}\}/g, (mm, k) => (has(values, k) ? String(values[k]) : mm)));
    }
    return out.join('\n');
  }

  // ------------------------------------------------------------------ project model
  function defaultStyleId(cfg) {
    for (const k of Object.keys(cfg.styles)) if (cfg.styles[k].default) return k;
    return Object.keys(cfg.styles)[0];
  }
  function emptyScene(i) {
    return { id: i, beats: ['', '', ''], frame1: '', frame2: '', cuts: [0, 1, 2].map(() => ({ type: '', prompt: '' })) };
  }
  function defaultProject(cfg) {
    const scenes = [];
    for (let i = 1; i <= cfg.spec.scenes; i++) scenes.push(emptyScene(i));
    return {
      version: 3,
      meta: { topic: '', top_title: '', category: 'shopping', category2: '', format: '', style: defaultStyleId(cfg),
        language: 'ko', source_url: '', source_script: '' },
      options: { zero_text: true, safe_margin: true },
      subject_anchor: '',
      analysis: { hook_technique: '', retention_psychology: '', skeleton: '' },
      plan: { titles: [], description: '', hashtags: [] },
      scenes,
      render: { crop_scale: cfg.spec.crop_scale, fit: 'cover', sub_size: cfg.layout.sub_size, sub_chars_per_line: cfg.layout.sub_chars_per_line },
      metadata: {}
    };
  }
  function stripTimeMarker(s) { return String(s || '').replace(TIME_MARKER_RE, '').trim(); }
  function stripSuffix(s) { return String(s || '').trim().replace(/\s*--(?:no|ar)\b[\s\S]*$/i, '').trim(); }
  function splitNarration(s) { return s.split(/\[[^\]]*s\]/).map((x) => x.trim()).filter(Boolean); }

  function normalizeScene(src, i) {
    const sc = emptyScene(i);
    let beats = src.beats;
    if (!Array.isArray(beats)) {
      const nar = src.narration || src.script || '';
      if (Array.isArray(nar)) beats = nar;
      else if (typeof nar === 'string' && nar.trim()) beats = splitNarration(nar).length ? splitNarration(nar) : [nar.trim()];
      else beats = [];
    }
    beats = beats.map((b) => stripTimeMarker(String(b))).slice(0, 3);
    while (beats.length < 3) beats.push('');
    sc.beats = beats;
    sc.frame1 = stripSuffix(src.frame1 || src.frame_1 || src.frame1_prompt || '');
    sc.frame2 = stripSuffix(src.frame2 || src.frame_2 || src.frame2_prompt || '');
    const cuts = Array.isArray(src.cuts) ? src.cuts : (src.angles || []);
    for (let j = 0; j < 3; j++) {
      let c = j < cuts.length ? cuts[j] : {};
      if (typeof c === 'string') c = { type: '', prompt: c };
      sc.cuts[j] = { type: String(c.type || ''), prompt: stripSuffix(String(c.prompt || '')) };
    }
    if ('done' in src) sc.done = src.done;
    return sc;
  }
  function normalizeProject(p, cfg) {
    p = p || {};
    const out = defaultProject(cfg);
    ['meta', 'options', 'analysis', 'plan', 'render'].forEach((k) => { if (p[k] && typeof p[k] === 'object' && !Array.isArray(p[k])) Object.assign(out[k], clone(p[k])); });
    ['subject_anchor', 'metadata'].forEach((k) => { if (k in p) out[k] = clone(p[k]); });
    const m = out.meta;
    m.style = LEGACY_STYLE_KEYS[m.style] || m.style;
    m.category = LEGACY_CATEGORY_KEYS[m.category] || m.category;
    m.category2 = LEGACY_CATEGORY_KEYS[m.category2] || m.category2;
    if (!has(cfg.styles, m.style)) m.style = defaultStyleId(cfg);
    if (!has(cfg.categories, m.category)) m.category = 'shopping';
    if (!has(cfg.categories, m.category2)) m.category2 = '';
    if (!has(cfg.languages, m.language)) m.language = 'ko';
    const scenes = Array.isArray(p.scenes) ? p.scenes : [];
    out.scenes = [];
    for (let i = 0; i < cfg.spec.scenes; i++) {
      const src = i < scenes.length && scenes[i] && typeof scenes[i] === 'object' ? scenes[i] : {};
      out.scenes.push(normalizeScene(src, i + 1));
    }
    return out;
  }

  // ------------------------------------------------------------------ counting
  function sceneText(scene) {
    return scene.beats.filter((b) => b && b.trim()).map((b) => b.trim()).join(' ');
  }
  function countUnits(text, lang, cfg) {
    const unit = cfg.languages[lang].unit;
    if (lang === 'ko') return ulen(text);
    if (unit === 'words') return (text.match(/\S+/g) || []).length;
    return ulen(text.replace(/\s+/g, ''));
  }
  function totalUnits(project, cfg) {
    const lang = project.meta.language;
    return project.scenes.reduce((a, s) => a + countUnits(sceneText(s), lang, cfg), 0);
  }
  function isShopping(project, cfg) {
    const m = project.meta;
    return [m.category, m.category2].some((k) => k && cfg.categories[k] && cfg.categories[k].shopping);
  }

  // ------------------------------------------------------------------ composition
  const trim = (s) => String(s || '').trim().replace(/[\s.,;]+$/, '');
  const sentence = (s) => { s = String(s || '').trim(); return !s || /[.!?]$/.test(s) ? s : s + '.'; };

  function composeFrame(cfg, project, desc) {
    const style = cfg.styles[project.meta.style];
    const parts = [style.anchor];
    if ((project.subject_anchor || '').trim()) parts.push(trim(project.subject_anchor));
    if ((desc || '').trim()) parts.push(trim(desc));
    if (project.options.safe_margin !== false) parts.push(cfg.suffix.safe_margin);
    let text = parts.join(', ');
    if (project.options.zero_text !== false) text += ' ' + cfg.suffix.zero_text;
    return text;
  }
  function composeOmni(cfg, project, scene) {
    const style = cfg.styles[project.meta.style];
    const om = cfg.omni;
    const zero = project.options.zero_text !== false;
    const safe = project.options.safe_margin !== false;
    const lines = [om.header + (zero ? om.header_zero : '') + ':', ''];
    for (let i = 0; i < 3; i++) {
      const c = i < scene.cuts.length ? scene.cuts[i] : { prompt: '' };
      lines.push((cfg.time_labels[i] + ': ' + cfg.cut_connectors[i] + ' ' + sentence(c.prompt || '')).replace(/\s+$/, ''));
      lines.push('');
    }
    const polish = [style.video_feel, om.polish_base];
    if (safe) polish.push(om.polish_safe);
    if (zero) polish.push(om.polish_zero);
    lines.push('Visual Polish: ' + polish.join(', ') + '.');
    return lines.join('\n');
  }
  function scenePackage(cfg, project, idx) {
    const sc = project.scenes[idx];
    return { narration: sceneText(sc), frame1: composeFrame(cfg, project, sc.frame1), frame2: composeFrame(cfg, project, sc.frame2), omni: composeOmni(cfg, project, sc) };
  }
  function pad2(n) { return String(n).padStart(2, '0'); }
  function allPromptsText(cfg, project) {
    const st = cfg.styles[project.meta.style];
    const out = ['='.repeat(57), 'AI SHORTS PROMPT EXPORT', 'Topic: ' + project.meta.topic,
      'Style: ' + st.number + '. ' + st.name, 'Rule: 45s (6 scenes x 7.5s) | Method B (3 cuts x 2.5s)',
      'Zero-Text: ' + (project.options.zero_text !== false ? 'ENFORCED' : 'OFF'),
      'Safe margin (1.06x crop): ' + (project.options.safe_margin !== false ? 'APPLIED' : 'OFF'), '='.repeat(57), ''];
    project.scenes.forEach((_, i) => {
      const pk = scenePackage(cfg, project, i);
      out.push('[Scene ' + pad2(i + 1) + ']  narration: ' + pk.narration, '', '[Frame 1 (0s)]', pk.frame1, '', '[Frame 2 (2.5s)]', pk.frame2, '',
        '[Omni 1.2 video prompt]', pk.omni, '', '-'.repeat(57), '');
    });
    return out.join('\n');
  }

  // ------------------------------------------------------------------ master prompt
  function structure(cfg, bp1, bp2) {
    const keys = cfg.blueprint_keys, roles = cfg.scene_roles, lines = [];
    keys.forEach((kv, i) => {
      const k = kv[0], label = kv[1], t = roles[i].time;
      if (!bp2) lines.push('- [Scene ' + pad2(i + 1) + ' / ' + t + '] ' + label + ': ' + bp1[k]);
      else if (i < 3) lines.push('- [Scene ' + pad2(i + 1) + ' / ' + t + ' (1차)] ' + label + ': ' + bp1[k]);
      else lines.push('- [Scene ' + pad2(i + 1) + ' / ' + t + ' (' + ['2차 전환', '2차 반전', '2차 착지'][i - 3] + ')] ' + label + ': ' + bp2[k]);
    });
    if (bp2) lines.push("* 연출 지침: 초반 22.5초까지는 '" + bp1.name + "'의 톤으로 몰입시키고, 22.5초 이후부터 '" + bp2.name + "'의 문법으로 급커브를 틀어 시청자에게 강렬한 인상을 남길 것.");
    return lines.join('\n');
  }
  function buildMasterPrompt(cfg, project) {
    const m = project.meta;
    const lang = cfg.languages[m.language];
    const style = cfg.styles[m.style];
    const bp1 = cfg.categories[m.category];
    const bp2 = m.category2 && m.category2 !== m.category ? cfg.categories[m.category2] : null;
    const spec = cfg.spec;
    const src = (m.source_script || '').trim().slice(0, 6000);
    const url = (m.source_url || '').trim();
    const shop = isShopping(project, cfg);
    const task = src
      ? "제공된 [원본 벤치마킹 대본]의 구조적 성공 공식(훅·시청 유지 심리·반전 구조)을 역설계(Reverse-Engineering)한 뒤, 내용은 그대로 베끼지 말고 '왜 떡상했는지'의 뼈대만 복제해 아래 [타깃 소재]로 완전히 새로 재구성하세요."
      : '원본 소스 대본이 없으므로, 선택한 카테고리의 스토리 뼈대를 바탕으로 [타깃 소재]에 맞춰 처음부터 대본을 설계하세요.';
    const subjectRule = (project.subject_anchor || '').trim()
      ? '- 주인공/제품 외형 앵커(전 씬 고정, 시스템이 모든 프레임 프롬프트에 자동 삽입): ' + project.subject_anchor.trim() + '. 씬 묘사에서 외형을 다시 설명하지 말고 같은 대상이 일관되게 등장한다는 전제로 행동과 구도만 쓰세요.'
      : '- 주인공/제품이 반복 등장하면 subject_anchor에 영문 외형 키워드(성별·연령·의상·색·재질)를 한 번만 정의하세요. 시스템이 모든 프레임 프롬프트에 자동 삽입해 씬마다 외형이 달라지지 않게 합니다.';
    const fmt = cfg.formats[m.format || ''];
    const formatBlock = fmt ? '- 트렌드 포맷 적용: ' + fmt.name + ' (' + fmt.keywords + ') - ' + fmt.guide : '';
    const ctaBlock = shop ? '- [쇼핑 카테고리 전용 필수 규칙] Scene 06의 마지막 beat에 다음 의미의 제휴 전환 문구를 ' + lang.name + '로 자연스럽게 넣을 것: "' + lang.cta + '"' : '';
    const categoryLine = bp2 ? '1차 ' + bp1.name + ' + 2차 ' + bp2.name + ' (합성 크로스오버)' : bp1.name + ' (단일 모드)';
    const sourceLine = (src ? '아래 [원본 벤치마킹 대본]' : '없음 (카테고리 뼈대로 신규 설계)') + (url ? ' (URL: ' + url + ')' : '');
    const sourceBlock = src ? '### 원본 벤치마킹 대본\n"""\n' + src + '\n"""' : '';
    const cutPlan = cfg.scene_roles.map((r) => '  - Scene ' + pad2(r.id) + ' (' + r.time + ') ' + r.role + ': ' + r.cuts).join('\n');
    const cameraLib = cfg.camera_library.map((x) => '  - ' + x).join('\n');
    const schema = fill(cfg.schema_template, { lang_name: lang.name });
    return fill(cfg.master_template, {
      task_line: task, length_rule: lang.length_rule, lang_desc: lang.desc, crop_scale: String(spec.crop_scale),
      safe_pct: String(spec.safe_zone_pct), margin_pct: String(spec.margin_pct), cut_plan: cutPlan, camera_lib: cameraLib,
      style_name: style.number + '. ' + style.name + ' (' + style.name_en + ')', subject_rule: subjectRule,
      structure: structure(cfg, bp1, bp2), format_block: formatBlock, cta_block: ctaBlock, topic: m.topic || '(미입력)',
      category_line: categoryLine, source_line: sourceLine, source_block: sourceBlock, schema
    });
  }
  function recommendedModel(cfg, project, task) {
    if (task === 'metadata') return cfg.models.metadata;
    const m = project.meta;
    if (m.category2 && m.category2 !== m.category) return cfg.models.crossover;
    return cfg.models.default;
  }

  // ------------------------------------------------------------------ metadata prompt
  function buildMetadataPrompt(cfg, project, languages) {
    const m = project.meta;
    const shop = isShopping(project, cfg);
    const bp1 = cfg.categories[m.category];
    const bp2 = m.category2 && m.category2 !== m.category ? cfg.categories[m.category2] : null;
    const categoryLine = bp2 ? bp1.name + ' + ' + bp2.name : bp1.name;
    const pin = shop ? ' (쇼핑 카테고리: 쇼핑 태그/프로필 링크 구매 유도 문구 필수)' : '';
    const rules = Object.keys(cfg.platforms).map((k) => '  - ' + cfg.platforms[k].name + ': ' + cfg.platforms[k].rule.split('{{shopping_pin}}').join(pin)).join('\n');
    const note = shop ? '- 쇼핑 카테고리이므로 고정댓글에는 반드시 구매 유도 문구를 넣고 플랫폼별 위치 안내를 맞추세요 (YouTube: 하단 쇼핑 태그·고정댓글 링크 / Instagram: 프로필 링크 / TikTok: 좌측 하단 노란 장바구니).' : '';
    const script = project.scenes.map((s, i) => 'Scene ' + pad2(i + 1) + ': ' + sceneText(s)).join('\n');
    const langs = languages.filter((k) => has(cfg.languages, k)).map((k) => k + '(' + cfg.languages[k].name + ')').join(', ');
    return fill(cfg.metadata_template, { category_line: categoryLine, topic: m.topic || '(미입력)', languages: langs, platform_rules: rules, shopping_note: note, script });
  }

  // ------------------------------------------------------------------ Claude response import
  function extractJson(text) {
    text = text || '';
    const re = /```(?:json|JSON)?\s*([\s\S]*?)```/g;
    let mt;
    while ((mt = re.exec(text)) !== null) { try { return JSON.parse(mt[1]); } catch (e) { /* next */ } }
    const a = text.indexOf('{'), b = text.lastIndexOf('}');
    if (a >= 0 && b > a) { try { return JSON.parse(text.slice(a, b + 1)); } catch (e) { return null; } }
    return null;
  }
  function parseClaudeResponse(text, cfg) {
    const data = extractJson(text);
    if (!data || typeof data !== 'object' || !Array.isArray(data.scenes)) throw new Error('응답에서 scenes 배열이 있는 JSON 을 찾지 못했습니다.');
    const out = { scenes: data.scenes.slice(0, cfg.spec.scenes).map((s, i) => normalizeScene(s && typeof s === 'object' ? s : {}, i + 1)) };
    while (out.scenes.length < cfg.spec.scenes) out.scenes.push(emptyScene(out.scenes.length + 1));
    ['analysis', 'plan'].forEach((k) => { if (data[k] && typeof data[k] === 'object') out[k] = data[k]; });
    ['top_title', 'subject_anchor'].forEach((k) => { if (typeof data[k] === 'string') out[k] = data[k].trim(); });
    return out;
  }
  function applyResponse(project, parsed) {
    const p = clone(project);
    p.scenes = parsed.scenes;
    ['analysis', 'plan'].forEach((k) => { if (parsed[k]) Object.assign(p[k], parsed[k]); });
    if (parsed.top_title) p.meta.top_title = parsed.top_title;
    if (parsed.subject_anchor) p.subject_anchor = parsed.subject_anchor;
    return p;
  }
  function injectCta(cfg, project) {
    const p = clone(project);
    const lang = cfg.languages[p.meta.language];
    const last = p.scenes[p.scenes.length - 1];
    const text = sceneText(last).toLowerCase();
    if (lang.cta_markers.every((mk) => text.indexOf(mk.toLowerCase()) >= 0)) return p;
    last.beats[2] = (last.beats[2].trim() + ' ' + lang.cta).trim();
    return p;
  }

  // ------------------------------------------------------------------ validation
  function validateProject(cfg, project) {
    const issues = [];
    const add = (level, code, msg, scene) => issues.push({ level, code, msg, scene: scene === undefined ? null : scene });
    const m = project.meta;
    const lang = cfg.languages[m.language];
    const unit = lang.unit === 'words' ? '단어' : '자';
    const n = project.scenes.length;
    if (n !== cfg.spec.scenes) add('error', 'scene_count', '씬이 ' + n + '개입니다. 정확히 ' + cfg.spec.scenes + '개여야 합니다.');
    const total = totalUnits(project, cfg);
    if (total === 0) add('warn', 'empty_script', '대본이 비어 있습니다.');
    else if (total < lang.min || total > lang.max) add('error', 'total_chars', '총 ' + total + unit + ' - 목표 ' + lang.min + '~' + lang.max + unit + ' 범위를 벗어났습니다 (45초 1.2배속 기준).');
    else add('ok', 'total_chars', '총 ' + total + unit + ' (목표 ' + lang.min + '~' + lang.max + unit + ')');

    project.scenes.forEach((sc, idx) => {
      const i = idx + 1;
      const filled = sc.beats.filter((b) => b.trim());
      if (total && filled.length !== 3) add('error', 'beats', 'Scene ' + pad2(i) + ': 비트가 ' + filled.length + '개입니다 (3개 필요: 0~2.5s / 2.5~5s / 5~7.5s).', i);
      const u = countUnits(sceneText(sc), m.language, cfg);
      if (total && (u < lang.scene_min || u > lang.scene_max)) add('warn', 'scene_chars', 'Scene ' + pad2(i) + ': ' + u + unit + ' (권장 ' + lang.scene_min + '~' + lang.scene_max + unit + ')', i);
      const prompts = [['frame1', sc.frame1], ['frame2', sc.frame2]].concat(sc.cuts.map((c, j) => ['cut' + (j + 1), c.prompt]));
      const hasAny = prompts.some((p) => p[1].trim());
      prompts.forEach(([name, ptxt]) => {
        if (hasAny && !ptxt.trim()) { add('error', 'prompt_missing', 'Scene ' + pad2(i) + ': ' + name + ' 프롬프트가 비어 있습니다.', i); return; }
        if (CJK_RE.test(ptxt)) add('error', 'zero_text_cjk', 'Scene ' + pad2(i) + ' ' + name + ': 한글/일문/중문 문자가 있습니다. 프롬프트는 영문만 허용(Zero-Text).', i);
        const set = new Set((ptxt.toLowerCase().match(/[A-Za-z]+/g) || []).filter((w) => BANNED_PROMPT_WORDS.indexOf(w) >= 0));
        const words = Array.from(set).sort();
        if (words.length) add('warn', 'zero_text_word', 'Scene ' + pad2(i) + ' ' + name + ': 문자 연상 단어 ' + words.join(', ') + ' - AI가 글자를 그려 넣을 수 있습니다.', i);
        if (EXTREME_CLOSEUP_RE.test(ptxt)) add('warn', 'extreme_closeup', 'Scene ' + pad2(i) + ' ' + name + ': 익스트림 클로즈업은 1.06배 크롭 시 피사체 잘림 위험 (Medium close-up + 여백 권장).', i);
      });
      sc.cuts.forEach((c, j) => {
        if (EXTREME_CLOSEUP_RE.test(c.type || '')) add('warn', 'extreme_closeup', 'Scene ' + pad2(i) + ' cut' + (j + 1) + " 화각 '" + c.type + "': 안전 마진 규칙과 충돌합니다.", i);
      });
    });

    if (isShopping(project, cfg) && n) {
      const last = sceneText(project.scenes[n - 1]).toLowerCase();
      if (!lang.cta_markers.every((mk) => last.indexOf(mk.toLowerCase()) >= 0)) add('error', 'cta', '쇼핑 카테고리인데 Scene 06에 쇼핑 CTA(' + lang.cta + ')가 없습니다.');
      else add('ok', 'cta', 'Scene 06 쇼핑 CTA 확인');
    }
    if (!(project.meta.top_title || '').trim()) add('warn', 'top_title', '상단 노란 타이틀 문구가 비어 있습니다.');
    return issues;
  }

  return {
    fill, defaultStyleId, emptyScene, defaultProject, normalizeProject, normalizeScene, stripTimeMarker, stripSuffix,
    sceneText, countUnits, totalUnits, isShopping, composeFrame, composeOmni, scenePackage, allPromptsText,
    buildMasterPrompt, recommendedModel, buildMetadataPrompt, extractJson, parseClaudeResponse, applyResponse,
    injectCta, validateProject
  };
});
