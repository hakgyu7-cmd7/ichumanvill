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
    return { id: i, beats: ['', '', ''], frame1: '', frame2: '', refs: [], cuts: [0, 1, 2].map(() => ({ type: '', prompt: '' })) };
  }
  function defaultProject(cfg) {
    const scenes = [];
    for (let i = 1; i <= cfg.spec.scenes; i++) scenes.push(emptyScene(i));
    return {
      version: 3,
      meta: { topic: '', top_title: '', category: cfg.default_category || 'general', category2: '', format: '', style: defaultStyleId(cfg),
        language: 'ko', source_url: '', source_script: '' },
      options: { zero_text: true, safe_margin: true },
      assets: [],
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
    sc.refs = Array.isArray(src.refs) ? src.refs.map((x) => String(x)) : [];
    if ('done' in src) sc.done = src.done;
    return sc;
  }
  function normalizeProject(p, cfg) {
    p = p || {};
    const out = defaultProject(cfg);
    ['meta', 'options', 'analysis', 'plan', 'render'].forEach((k) => { if (p[k] && typeof p[k] === 'object' && !Array.isArray(p[k])) Object.assign(out[k], clone(p[k])); });
    if ('metadata' in p) out.metadata = clone(p.metadata);
    const m = out.meta;
    m.style = LEGACY_STYLE_KEYS[m.style] || m.style;
    m.category = LEGACY_CATEGORY_KEYS[m.category] || m.category;
    m.category2 = LEGACY_CATEGORY_KEYS[m.category2] || m.category2;
    if (!has(cfg.styles, m.style)) m.style = defaultStyleId(cfg);
    if (!has(cfg.categories, m.category)) m.category = cfg.default_category || 'general';
    if (!has(cfg.categories, m.category2)) m.category2 = '';
    if (!has(cfg.languages, m.language)) m.language = 'ko';
    const scenes = Array.isArray(p.scenes) ? p.scenes : [];
    out.scenes = [];
    for (let i = 0; i < cfg.spec.scenes; i++) {
      const src = i < scenes.length && scenes[i] && typeof scenes[i] === 'object' ? scenes[i] : {};
      out.scenes.push(normalizeScene(src, i + 1));
    }
    out.assets = normalizeAssets(p.assets);
    const legacy = String(p.subject_anchor || '').trim();
    if (legacy && !out.assets.length) {   // 옛 '주인공 외형 앵커' -> 모든 씬에 연결된 asset 1개
      out.assets = [{ id: 'main', type: 'character', name: '주인공/핵심 대상', label: '', appearance: stripSuffix(legacy).replace(/[ .,;]+$/, ''), keywords: '', done: false }];
      out.scenes.forEach((sc) => { sc.refs = ['main']; });
    }
    const ids = out.assets.map((a) => a.id);
    out.scenes.forEach((sc) => { sc.refs = uniq(sc.refs).filter((r) => ids.indexOf(r) >= 0); });
    return out;
  }
  const uniq = (items) => Array.from(new Set(items));
  const ASSET_TYPES = ['character', 'object', 'place'];
  const slug = (s) => String(s || '').trim().toLowerCase().replace(/[^a-z0-9_]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 30);
  function normalizeAssets(items) {
    const out = [], used = new Set();
    (Array.isArray(items) ? items : []).forEach((a, idx) => {
      if (!a || typeof a !== 'object' || Array.isArray(a)) return;
      const base = slug(String(a.id || a.label || '')) || ('asset' + (idx + 1));
      let aid = base, k = 2;
      while (used.has(aid)) { aid = base + '_' + k; k++; }
      used.add(aid);
      const t = String(a.type || 'object').trim().toLowerCase();
      let kw = a.keywords === undefined ? '' : a.keywords;
      if (Array.isArray(kw)) kw = kw.map((x) => String(x)).join(', ');
      out.push({ id: aid, type: ASSET_TYPES.indexOf(t) >= 0 ? t : 'object', name: String(a.name || '').trim(), label: String(a.label || '').trim(),
        appearance: stripSuffix(String(a.appearance || '')), keywords: String(kw || '').trim(), done: !!a.done });
    });
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

  function sceneAssets(project, refs) { const ids = refs || []; return (project.assets || []).filter((a) => ids.indexOf(a.id) >= 0); }
  function composeFrame(cfg, project, desc, refs) {
    const style = cfg.styles[project.meta.style];
    const parts = [style.anchor];
    sceneAssets(project, refs).forEach((a) => { if (a.appearance.trim()) parts.push(trim(a.appearance)); });
    if ((desc || '').trim()) parts.push(trim(desc));
    if (project.options.safe_margin !== false) parts.push(cfg.suffix.safe_margin);
    let text = parts.join(', ');
    if (project.options.zero_text !== false) text += ' ' + cfg.suffix.zero_text;
    return text;
  }
  function composeReference(cfg, project, asset, kind) {
    const ref = cfg.reference;
    const parts = [cfg.styles[project.meta.style].anchor];
    if (asset.appearance.trim()) parts.push(trim(asset.appearance));
    parts.push(ref.types[asset.type][kind]);
    let text = parts.join(', ');
    if (project.options.zero_text !== false) text += ' ' + cfg.suffix.zero_text_core + ' --ar ' + (kind === 'main' ? ref.ar_main : ref.ar_sheet);
    return text;
  }
  function referencePrompts(cfg, project) {
    return (project.assets || []).map((a) => ({
      id: a.id, type: a.type, name: a.name, label: a.label,
      scenes: project.scenes.map((sc, i) => ((sc.refs || []).indexOf(a.id) >= 0 ? i + 1 : 0)).filter(Boolean),
      main: composeReference(cfg, project, a, 'main'), sheet: composeReference(cfg, project, a, 'sheet')
    }));
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
    return { narration: sceneText(sc), frame1: composeFrame(cfg, project, sc.frame1, sc.refs), frame2: composeFrame(cfg, project, sc.frame2, sc.refs), omni: composeOmni(cfg, project, sc) };
  }
  function pad2(n) { return String(n).padStart(2, '0'); }
  function allPromptsText(cfg, project) {
    const st = cfg.styles[project.meta.style];
    const out = ['='.repeat(57), 'AI SHORTS PROMPT EXPORT', 'Topic: ' + project.meta.topic,
      'Style: ' + st.number + '. ' + st.name, 'Rule: 45s (6 scenes x 7.5s) | Method B (3 cuts x 2.5s)',
      'Zero-Text: ' + (project.options.zero_text !== false ? 'ENFORCED' : 'OFF'),
      'Safe margin (1.06x crop): ' + (project.options.safe_margin !== false ? 'APPLIED' : 'OFF'), '='.repeat(57), ''];
    referencePrompts(cfg, project).forEach((r) => {
      out.push('[기준 이미지] ' + (r.name || r.id) + ' (' + r.type + ') - 등장 씬: ' + (r.scenes.join(', ') || '-'), '', '[Reference - main]', r.main, '', '[Reference - sheet]', r.sheet, '', '-'.repeat(57), '');
    });
    project.scenes.forEach((_, i) => {
      const pk = scenePackage(cfg, project, i);
      out.push('[Scene ' + pad2(i + 1) + ']  narration: ' + pk.narration, '', '[Frame 1 (0s)]', pk.frame1, '', '[Frame 2 (2.5s)]', pk.frame2, '',
        '[Omni 1.2 video prompt]', pk.omni, '', '-'.repeat(57), '');
    });
    return out.join('\n');
  }

  // ------------------------------------------------------------------ master prompt
  function structure(cfg, bp1, bp2, hasSrc) {
    const keys = cfg.blueprint_keys, roles = cfg.scene_roles, lines = [];
    keys.forEach((kv, i) => {
      const k = kv[0], label = kv[1], t = roles[i].time;
      if (!bp2) lines.push('- [Scene ' + pad2(i + 1) + ' / ' + t + '] ' + label + ': ' + bp1[k]);
      else if (i < 3) lines.push('- [Scene ' + pad2(i + 1) + ' / ' + t + ' (1차)] ' + label + ': ' + bp1[k]);
      else lines.push('- [Scene ' + pad2(i + 1) + ' / ' + t + ' (' + ['2차 전환', '2차 반전', '2차 착지'][i - 3] + ')] ' + label + ': ' + bp2[k]);
    });
    if (bp2) lines.push("* 연출 지침: 초반 22.5초까지는 '" + bp1.name + "'의 톤으로 몰입시키고, 22.5초 이후부터 '" + bp2.name + "'의 문법으로 급커브를 틀어 시청자에게 강렬한 인상을 남길 것.");
    if (hasSrc) lines.push('* 원본 대본의 구조적 리듬(훅 → 전개 → 반전)이 위 뼈대와 다르면 원본의 리듬을 우선하고, 위 뼈대는 보조 기준으로만 쓰세요.');
    return lines.join('\n');
  }
  function assetRuleText(project) {
    if (!(project.assets || []).length) {
      return '- [기준 이미지 규칙] 2개 이상의 씬에 등장하거나 스토리의 핵심인 인물·사물·장소는 assets 배열에 정의하세요. ' +
        '각 asset: id(영문 소문자·숫자·_), type(character/object/place), name(한국어 이름), label(영문 짧은 호칭 예: the plastic cook figure), ' +
        'appearance(영문 외형 고정 키워드 - 성별·연령·체형·의상·색·재질·특징을 구체적으로, 배경·동작·화각은 제외), ' +
        'keywords(대본에서 이 대상을 가리키는 한국어 단어들을 쉼표로). 각 씬의 refs 에 그 씬에 등장하는 asset id 를 넣으세요. ' +
        '시스템이 appearance 를 해당 씬의 모든 프레임 프롬프트에 자동 삽입하고 기준 이미지 프롬프트도 자동 생성하므로, ' +
        '씬 묘사(frame/cuts)에서는 외형을 다시 설명하지 말고 label 로만 지칭합니다.';
    }
    const lines = ['- [기준 이미지 규칙] 이미 정의된 기준 이미지 대상입니다(그대로 유지하세요. 시스템이 외형을 해당 씬의 모든 프레임 프롬프트에 자동 삽입합니다):'];
    project.assets.forEach((a) => lines.push('  · ' + a.id + ' (' + a.type + ') ' + a.name + ' / ' + a.label + ': ' + a.appearance));
    lines.push('  새로 필요한 반복 대상이 있으면 assets 에 추가하고, 씬 묘사(frame/cuts)에서는 외형을 다시 설명하지 말고 label 로만 지칭하세요. 각 씬의 refs 에 등장하는 asset id 를 넣으세요.');
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
    const assetRule = assetRuleText(project);
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
      style_name: style.number + '. ' + style.name + ' (' + style.name_en + ')', asset_rule: assetRule,
      structure: structure(cfg, bp1, bp2, !!src), format_block: formatBlock, cta_block: ctaBlock, topic: m.topic || '(미지정 - 원본과 겹치지 않는 새 소재를 직접 정해 주세요)',
      category_line: categoryLine, source_line: sourceLine, source_block: sourceBlock, schema
    });
  }
  function recommendedModel(cfg, project, task) {
    if (task === 'metadata') return cfg.models.metadata;
    const m = project.meta;
    if (m.category2 && m.category2 !== m.category) return cfg.models.crossover;
    return cfg.models.default;
  }

  // ------------------------------------------------------------------ 기준 이미지(등장 대상) 분석
  function buildAssetPrompt(cfg, project) {
    const st = cfg.styles[project.meta.style];
    const existing = (project.assets || []).length
      ? '- 이미 정의된 asset(유지하고 필요한 것만 추가): ' + project.assets.map((a) => a.id + '=' + (a.label || a.name)).join(', ') : '';
    const lines = [];
    project.scenes.forEach((sc, i) => {
      lines.push('Scene ' + pad2(i + 1) + ': ' + sceneText(sc));
      lines.push('  frame1: ' + sc.frame1);
      lines.push('  frame2: ' + sc.frame2);
      lines.push('  cuts: ' + sc.cuts.filter((c) => c.prompt.trim()).map((c) => c.prompt).join(' / '));
    });
    return fill(cfg.asset_template, { style_name: st.number + '. ' + st.name + ' (' + st.name_en + ')', existing_assets: existing, scenes_text: lines.join('\n') });
  }
  function parseAssetsResponse(text, cfg) {
    const data = extractJson(text);
    if (!data || typeof data !== 'object' || !Array.isArray(data.assets)) throw new Error('응답에서 assets 배열이 있는 JSON 을 찾지 못했습니다.');
    const refs = {};
    const sr = data.scene_refs;
    if (sr && typeof sr === 'object' && !Array.isArray(sr)) {
      Object.keys(sr).forEach((k) => {
        if (!/^\s*\d+\s*$/.test(k)) return;
        const i = parseInt(k, 10);
        if (i >= 1 && i <= cfg.spec.scenes && Array.isArray(sr[k])) refs[String(i)] = sr[k].map((x) => String(x));
      });
    }
    return { assets: normalizeAssets(data.assets), scene_refs: refs };
  }
  function applyAssets(project, parsed) {
    const p = clone(project);
    const done = {};
    (p.assets || []).forEach((a) => { done[a.id] = a.done; });
    p.assets = parsed.assets.map((a) => Object.assign({}, a, { done: !!(has(done, a.id) ? done[a.id] : a.done) }));
    const ids = p.assets.map((a) => a.id);
    p.scenes.forEach((sc, idx) => {
      const k = String(idx + 1);
      const src = has(parsed.scene_refs || {}, k) ? parsed.scene_refs[k] : (sc.refs || []);
      sc.refs = uniq(src).filter((r) => ids.indexOf(r) >= 0);
    });
    return p;
  }
  function assetTokens(a) {
    return [a.name, a.label].concat(a.keywords.split(/[,\n]+/)).map((t) => t.trim().toLowerCase()).filter((t) => Array.from(t).length >= 2);
  }
  function linkAssets(project) {
    const p = clone(project);
    p.scenes.forEach((sc) => {
      const hay = [sceneText(sc), sc.frame1, sc.frame2].concat(sc.cuts.map((c) => c.prompt)).join(' ').toLowerCase();
      sc.refs = p.assets.filter((a) => (sc.refs || []).indexOf(a.id) >= 0 || assetTokens(a).some((t) => hay.indexOf(t) >= 0)).map((a) => a.id);
    });
    return p;
  }
  function suggestRecurring(cfg, project, minScenes, limit) {
    minScenes = minScenes || 3; limit = limit || 12;
    const stop = new Set(cfg.recurring_stop_words || []);
    const covered = new Set();
    (project.assets || []).forEach((a) => assetTokens(a).forEach((t) => (t.match(/[a-z]{4,}/g) || []).forEach((w) => covered.add(w))));
    const counts = {};
    project.scenes.forEach((sc) => {
      const words = new Set();
      [sc.frame1, sc.frame2].concat(sc.cuts.map((c) => c.prompt)).forEach((txt) => {
        (String(txt || '').toLowerCase().match(/[a-z]{4,}/g) || []).forEach((w) => { if (!stop.has(w) && !covered.has(w)) words.add(w); });
      });
      words.forEach((w) => { counts[w] = (counts[w] || 0) + 1; });
    });
    const items = Object.keys(counts).filter((w) => counts[w] >= minScenes).map((w) => ({ word: w, scenes: counts[w] }));
    items.sort((a, b) => (b.scenes - a.scenes) || (a.word < b.word ? -1 : a.word > b.word ? 1 : 0));
    return items.slice(0, limit);
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
    if (typeof data.top_title === 'string') out.top_title = data.top_title.trim();
    if (Array.isArray(data.assets)) out.assets = normalizeAssets(data.assets);
    else if (typeof data.subject_anchor === 'string' && data.subject_anchor.trim()) {   // 옛 형식
      out.assets = normalizeAssets([{ id: 'main', type: 'character', name: '주인공/핵심 대상', appearance: data.subject_anchor }]);
      out.scenes.forEach((sc) => { sc.refs = ['main']; });
    }
    return out;
  }
  function applyResponse(project, parsed) {
    const p = clone(project);
    p.scenes = parsed.scenes;
    ['analysis', 'plan'].forEach((k) => { if (parsed[k]) Object.assign(p[k], parsed[k]); });
    if (parsed.top_title) p.meta.top_title = parsed.top_title;
    if ('assets' in parsed) {
      const done = {};
      (p.assets || []).forEach((a) => { done[a.id] = a.done; });
      p.assets = parsed.assets.map((a) => Object.assign({}, a, { done: !!(has(done, a.id) ? done[a.id] : a.done) }));
    }
    const ids = (p.assets || []).map((a) => a.id);
    p.scenes.forEach((sc) => { sc.refs = uniq(sc.refs || []).filter((r) => ids.indexOf(r) >= 0); });
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

    const linked = new Set();
    project.scenes.forEach((sc) => (sc.refs || []).forEach((r) => linked.add(r)));
    (project.assets || []).forEach((a) => {
      const nm = a.name || a.id;
      if (!a.appearance.trim()) add('warn', 'asset_empty', "기준 이미지 '" + nm + "': 외형 묘사(appearance)가 비어 있습니다.");
      if (CJK_RE.test(a.appearance) || CJK_RE.test(a.label)) add('error', 'asset_cjk', "기준 이미지 '" + nm + "': 외형/라벨은 영문만 허용(Zero-Text).");
      if (!linked.has(a.id)) add('warn', 'asset_unlinked', "기준 이미지 '" + nm + "'이(가) 어느 씬에도 연결되지 않았습니다.");
    });
    if (!(project.assets || []).length && project.scenes.some((sc) => sc.frame1.trim())) add('warn', 'no_assets', "등장인물/사물 기준 이미지가 없습니다. '기준 이미지' 단계에서 대본을 분석해 정의하세요(씬마다 외형이 달라지는 원인).");

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
    sceneText, countUnits, totalUnits, isShopping, composeFrame, composeOmni, composeReference, referencePrompts, sceneAssets, normalizeAssets,
    buildAssetPrompt, parseAssetsResponse, applyAssets, linkAssets, suggestRecurring, scenePackage, allPromptsText,
    buildMasterPrompt, recommendedModel, buildMetadataPrompt, extractJson, parseClaudeResponse, applyResponse,
    injectCta, validateProject
  };
});
