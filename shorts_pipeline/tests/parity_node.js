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
    cta: core.injectCta(cfg, p)
  };
  if (c.response) { const parsed = core.parseClaudeResponse(c.response, cfg); r.parsed = parsed; r.applied = core.applyResponse(p, parsed); }
  return r;
});
process.stdout.write(JSON.stringify(out));
