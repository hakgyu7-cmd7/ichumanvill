// Python(prompt_engine.py) 과 JS(pipeline_core.js) 출력 비교용: stdin 으로 케이스 목록(JSON)을 받아 결과를 stdout 으로 낸다.
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..');
const cfg = JSON.parse(fs.readFileSync(path.join(root, 'config.json'), 'utf8'));
const core = require(path.join(root, 'pipeline_core.js'));
const cases = JSON.parse(fs.readFileSync(0, 'utf8'));
const out = cases.map((c) => {
  const p = core.normalizeProject(c.project, cfg);
  const r = {
    project: p,
    master: core.buildMasterPrompt(cfg, p),
    metadata: core.buildMetadataPrompt(cfg, p, c.langs || ['ko']),
    all_prompts: core.allPromptsText(cfg, p),
    packages: p.scenes.map((_, i) => core.scenePackage(cfg, p, i)),
    validate: core.validateProject(cfg, p),
    total: core.totalUnits(p, cfg),
    shopping: core.isShopping(p, cfg),
    model: core.recommendedModel(cfg, p, 'script'),
    cta: core.injectCta(cfg, p),
    refs: core.referencePrompts(cfg, p),
    asset_prompt: core.buildAssetPrompt(cfg, p),
    linked: core.linkAssets(p),
    suggest: core.suggestRecurring(cfg, p),
    range: core.charRange(cfg, p),
    length_rule: core.lengthRuleText(cfg, p),
    policy_fix: p.scenes.map((_, i) => core.buildPolicyFixPrompt(cfg, p, i))
  };
  if (c.scene_fix) { r.scene_fixed = core.applySceneFix(p, c.scene_fix.idx, c.scene_fix.text); }
  if (c.assets_response) { const pa = core.parseAssetsResponse(c.assets_response, cfg); r.parsed_assets = pa; r.applied_assets = core.applyAssets(p, pa); }
  if (c.response) { const parsed = core.parseClaudeResponse(c.response, cfg); r.parsed = parsed; r.applied = core.applyResponse(p, parsed); }
  return r;
});
process.stdout.write(JSON.stringify(out));
