// 브라우저 스모크 테스트: node tests/ui_smoke.js <서버URL> <file://대시보드URL> <클립.mp4> <음성.wav> <산출물폴더>
// (Playwright 필요: npm i -g playwright, NODE_PATH 지정)
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const [SERVER, FILEURL, CLIP, WAV, OUT] = process.argv.slice(2);
const FIX = path.join(__dirname, 'fixtures');
let failed = 0; const ok = (c, m) => { if (!c) { failed++; console.log('FAIL:', m); } else console.log('ok  :', m); };
const eq = (a, b, m) => ok(a === b, `${m} (기대 ${JSON.stringify(b)}, 실제 ${JSON.stringify(a)})`);

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1500, height: 1000 }, acceptDownloads: true });
  const pg = await ctx.newPage(); const errs = [];
  pg.on('console', m => { if (m.type() === 'error') errs.push(m.text()); }); pg.on('pageerror', e => errs.push('pageerror: ' + e.message));
  pg.on('dialog', d => d.accept());
  const tab = async (id) => { await pg.click(`[data-act="tab"][data-id="${id}"]`); await pg.waitForTimeout(250); };
  const txt = async (sel) => (await pg.textContent(sel)).trim();

  // ---- 서버 모드
  await pg.route('**/api/trends*', r => {
    const u = r.request().url();
    r.fulfill({ json: u.includes('sources=reddit')
      ? { items: [{ platform: '레딧 r/x', title: 'LIVE 레딧 주제 테스트', keyword: 'k', cat: 'history', live: true }], status: { reddit: { live: true, note: '수집 성공', count: 1 } }, manual_links: [] }
      : { items: [{ platform: '쿠팡', title: 'LIVE 상품 테스트', keyword: 'k', cat: 'shopping', live: true }], status: { coupang: { live: true, note: '수집 성공', count: 1 } }, manual_links: [] } });
  });
  await pg.route('**/api/outliers', r => r.fulfill({ json: { items: [{ platform: 'YouTube', video_id: 'abcdefghijk', url: 'https://www.youtube.com/shorts/abcdefghijk', title: '떡상 영상', channel: 'ch', views: 5000000, subscribers: 100000, ratio: 50, grade: 'viral', duration: 30 }] } }));
  await pg.route('**/api/transcript', r => r.fulfill({ json: { text: '추출된 원본 대본 텍스트', method: 'mock', video_id: 'abcdefghijk' } }));
  await pg.goto(SERVER); await pg.waitForSelector('#stepper .step'); await pg.waitForTimeout(600);
  eq((await pg.$$('#stepper .step')).length, 6, '스테퍼 6단계');
  ok((await txt('#srv-txt')).includes('연결됨'), '서버 연결 표시');

  // ===== 기본은 레퍼런스 쇼츠 (쇼핑 아님)
  eq(await txt('#mode-seg .on'), '🎬 레퍼런스 쇼츠', '기본 모드 = 레퍼런스 쇼츠');
  eq(await txt('#m-chars'), '330자 / 320~350', '첫 실행 샘플은 레퍼런스형(라면, 330자)');
  ok(!(await pg.isVisible('#m-cta-wrap')), '레퍼런스 모드에서는 쇼핑 CTA 지표 숨김');
  ok((await txt('#stepper .step:first-child')).includes('레퍼런스'), '1단계 이름 = 레퍼런스');
  ok(await pg.isVisible('input[data-bind="meta.source_url"]'), '1단계 최상단에 레퍼런스 링크 입력');
  eq(await pg.$('[data-src="coupang"]'), null, '레퍼런스 모드에는 쿠팡/틱톡 수집 UI 없음');
  await tab('script');
  ok(!(await pg.innerHTML('select[data-bind="meta.category"]')).includes('쇼핑'), '레퍼런스 모드 카테고리 목록에 쇼핑 없음');
  eq(await pg.$('[data-act="injectCta"]'), null, '레퍼런스 모드에는 CTA 삽입 버튼 없음');
  ok(!(await pg.inputValue('#master-box')).includes('쇼핑 카테고리 전용'), '레퍼런스 마스터 프롬프트에 쇼핑 규칙 없음');
  ok((await pg.inputValue('#master-box')).includes('원본의 리듬을 우선'), '레퍼런스 대본이 있으면 원본 리듬 우선 지시');

  // 대본 편집 -> 지표 실시간 갱신
  const b0 = 'input[data-bind="scenes.0.beats.0"]'; const orig = await pg.inputValue(b0);
  await pg.fill(b0, '짧게'); ok((await txt('#m-chars')).startsWith('3') && (await txt('#m-chars')) !== '330자 / 320~350', '비트 수정 시 총 글자수 즉시 변경: ' + await txt('#m-chars'));
  ok((await txt('#issues')).includes('범위를 벗어났습니다'), '범위 이탈 시 오류 점검 표시');
  await pg.fill(b0, orig); eq(await txt('#m-chars'), '330자 / 320~350', '원복');
  await pg.selectOption('select[data-bind="meta.category"]', 'disaster'); await pg.selectOption('select[data-bind="meta.category2"]', 'bgrade'); await pg.waitForTimeout(200);
  ok((await pg.inputValue('#master-box')).includes('합성 크로스오버'), '합성(크로스오버) 모드');
  await pg.selectOption('select[data-bind="meta.category2"]', ''); await pg.selectOption('select[data-bind="meta.category"]', 'general');

  // 레퍼런스 모드 소재 아이디어(레딧) - 목 API
  await tab('source'); await pg.click('[data-act="fetchTrends"]'); await pg.waitForTimeout(400);
  ok((await txt('#trend-list')).includes('LIVE 레딧 주제 테스트'), '레퍼런스 모드 소재 아이디어(레딧) LIVE 표시');
  await pg.click('[data-act="pickTopic"]'); await pg.waitForTimeout(300);
  eq(await pg.inputValue('input[data-bind="meta.topic"]'), 'LIVE 레딧 주제 테스트', '주제로 선택 -> 새 주제 입력칸 반영');

  // 떡상 탐색 -> 레퍼런스로 선택 -> 대본 자동 채움
  await pg.fill('#ol-q', 'kitchen gadget'); await pg.fill('#ol-key', 'FAKEKEY'); await pg.click('[data-act="searchOutliers"]'); await pg.waitForTimeout(400);
  ok((await txt('#ol-res')).includes('50x') && (await txt('#ol-res')).includes('떡상 영상'), '떡상 탐색 결과 표');
  await pg.click('[data-act="pickOutlier"]'); await pg.waitForTimeout(600);
  eq(await pg.inputValue('input[data-bind="meta.source_url"]'), 'https://www.youtube.com/shorts/abcdefghijk', '레퍼런스 URL 반영');
  eq(await pg.inputValue('textarea[data-bind="meta.source_script"]'), '추출된 원본 대본 텍스트', '대본 자동 추출 결과 반영');
  await tab('script'); await tab('source');
  eq(await pg.inputValue('textarea[data-bind="meta.source_script"]'), '추출된 원본 대본 텍스트', '탭 이동 후에도 레퍼런스 대본 유지');
  await pg.fill('#vs-v', '5200000'); await pg.fill('#vs-s', '200000'); ok((await txt('#vs-out')).includes('26.0배'), 'V/S 계산기');
  await tab('script'); ok((await pg.inputValue('#master-box')).includes('추출된 원본 대본 텍스트') && (await pg.inputValue('#master-box')).includes('역설계'), '레퍼런스 대본이 마스터 프롬프트에 포함');
  ok((await txt('#content')).includes('레퍼런스 대본 13자'), '2단계 상단에 레퍼런스 요약 배너');

  // Claude 응답 가져오기 (레퍼런스 모드)
  await pg.fill('#claude-reply', fs.readFileSync(path.join(FIX, 'claude_reply.txt'), 'utf8'));
  await pg.click('[data-act="importReply"]'); await pg.waitForTimeout(300);
  eq(await pg.inputValue(b0), '라면 끓일 때마다 물 맞추기 실패한다면', '응답 JSON 가져오기(시간 표기 제거)');
  ok(!(await txt('#issues')).includes('쇼핑 카테고리인데'), '레퍼런스 모드는 CTA 없어도 오류 아님');
  await pg.fill('#claude-reply', 'JSON 없는 응답'); await pg.click('[data-act="importReply"]'); await pg.waitForTimeout(200);
  ok((await txt('#toast')).includes('찾지 못했습니다'), 'JSON 없는 응답은 에러 토스트');

  // ===== 쇼핑 쇼츠는 별도 모드
  await pg.click('[data-act="setMode"][data-m="shopping"]'); await pg.waitForTimeout(300);
  eq(await txt('#mode-seg .on'), '🛒 쇼핑 쇼츠', '쇼핑 모드 전환');
  ok(await pg.isVisible('#m-cta-wrap') && (await txt('#m-cta')) === '누락!', '쇼핑 모드: CTA 없는 대본이면 누락 표시');
  ok((await txt('#issues')).includes('쇼핑 카테고리인데'), '쇼핑 모드: CTA 누락 오류');
  ok((await pg.inputValue('#master-box')).includes('쇼핑 카테고리 전용'), '쇼핑 모드 마스터 프롬프트에 CTA 규칙');
  eq(await pg.inputValue('select[data-bind="meta.category"]'), 'shopping', '쇼핑 모드 1차 카테고리 = 쇼핑 고정');
  await pg.click('[data-act="injectCta"]'); await pg.waitForTimeout(200);
  ok((await pg.inputValue('input[data-bind="scenes.5.beats.2"]')).includes('고정 댓글'), 'CTA 자동 삽입');
  eq(await txt('#m-cta'), '주입 완료', 'CTA 주입 후 상태');
  await tab('source');
  ok((await pg.$('[data-src="coupang"]')) !== null && (await pg.$('[data-src="tiktok"]')) !== null, '쇼핑 모드 1단계: 쿠팡/틱톡 수집 UI');
  const srcText = await txt('#content');
  ok(srcText.indexOf('쇼핑 상품 트렌드') >= 0 && srcText.indexOf('쇼핑 상품 트렌드') < srcText.indexOf('레퍼런스 영상'), '쇼핑 모드 1단계: 상품 트렌드가 위');
  await pg.click('[data-act="fetchTrends"]'); await pg.waitForTimeout(400);
  ok((await txt('#trend-list')).includes('LIVE 상품 테스트'), '쇼핑 모드 쿠팡 LIVE 표시');
  await pg.click('[data-act="pickTopic"]'); await pg.waitForTimeout(300);
  eq(await pg.inputValue('input[data-bind="meta.topic"]'), 'LIVE 상품 테스트', '상품 선택 -> 기획 탭 반영');
  await pg.click('[data-act="setMode"][data-m="reference"]'); await pg.waitForTimeout(300);
  eq(await txt('#mode-seg .on'), '🎬 레퍼런스 쇼츠', '레퍼런스 모드로 복귀');
  await tab('script'); eq(await pg.inputValue('select[data-bind="meta.category"]'), 'history', '복귀 시 원래 카테고리(주제 선택 시 지정된 history) 복원');

  // 화풍 변경 -> 전 씬 프롬프트 즉시 변경
  await tab('visual');
  ok((await txt('#fin-0-frame1')).startsWith('Hyper-detailed collectible PVC figure'), '디오라마 앵커로 시작');
  ok((await txt('#fin-0-frame1')).endsWith('--no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16'), 'Zero-Text 접미사로 끝남');
  await tab('script'); await pg.selectOption('select[data-bind="meta.style"]', 'claymation'); await tab('visual');
  ok((await txt('#fin-5-frame2')).startsWith('Handmade stop-motion claymation'), '화풍 변경이 6씬 모두에 반영');
  ok((await txt('#fin-2-omni')).includes('Authentic stop-motion frame jitter') && (await txt('#fin-2-omni')).includes('[2.5s - 5.0s]: Instant hard cut'), 'Omni 프롬프트 합성');
  await pg.fill('textarea[data-bind="scenes.0.frame1"]', '한글 섞인 프롬프트 sign');
  ok((await txt('#issues')).includes('Zero-Text'), '한글/문자 단어 프롬프트 경고');

  // 미리보기
  await pg.evaluate(() => { const r = document.getElementById('pv-range'); r.value = 19; r.dispatchEvent(new Event('input', { bubbles: true })); });
  ok((await txt('#pv-ct')).startsWith('Scene 03 · Cut 2'), '미리보기 타임라인: 19초 = Scene 03 Cut 2 -> ' + await txt('#pv-ct'));

  // ---- 업로드 / 음성 / 렌더 (실제 서버 + ffmpeg)
  await tab('visual'); await pg.click('details[data-scene="0"] summary').catch(() => {});
  await pg.setInputFiles('input[data-upload="clip"][data-i="0"]', CLIP); await pg.waitForTimeout(1200);
  ok((await txt('#m-clips')).startsWith('1/'), '클립 업로드 후 헤더 클립 수 갱신: ' + await txt('#m-clips'));
  ok((await pg.$('#clip-0 video')) !== null, '업로드한 클립 미리보기 video');
  await tab('audio'); await pg.setInputFiles('input[data-upload="voice_raw"]', WAV); await pg.waitForTimeout(800);
  await pg.click('[data-act="processVoice"]'); await pg.waitForTimeout(2500);
  ok((await txt('#content')).includes('voice.mp3') && (await pg.$('#content audio')) !== null, '음성 처리 후 voice.mp3 + 플레이어');
  await tab('render');
  ok((await txt('#content')).includes('씬 클립 1/6'), '렌더 점검: 클립 1/6');
  await pg.check('#rd-partial'); await pg.click('[data-act="startRender"]');
  await pg.waitForFunction(() => /렌더링 완료|\[오류\]/.test(document.getElementById('rd-log').textContent), null, { timeout: 90000 });
  ok((await txt('#rd-log')).includes('렌더링 완료'), '부분 렌더 완료: ' + (await txt('#rd-log')).slice(-80));
  await pg.waitForTimeout(800); ok((await pg.$('#content video')) !== null, '결과 영상 플레이어');
  await pg.screenshot({ path: path.join(OUT, 'ui_render_done.png') });

  // ---- 메타데이터
  await tab('meta'); await pg.click('[data-act="metaLang"][data-k="en"]');
  eq(await pg.inputValue('input[data-meta="title"]'), '', '메타데이터 없는 언어 탭은 빈 칸');
  await pg.click('[data-act="metaLang"][data-k="ko"]'); await pg.fill('#meta-reply', fs.readFileSync(path.join(FIX, 'meta_reply.txt'), 'utf8')); await pg.click('[data-act="importMeta"]'); await pg.waitForTimeout(300);
  eq(await pg.inputValue('input[data-meta="title"]'), '새 제목', '메타데이터 응답 적용');
  await pg.click('[data-act="metaPlat"][data-k="instagram"]'); eq(await pg.inputValue('input[data-meta="title"]'), 'i', '플랫폼 탭 전환');

  // ---- 내보내기 / 불러오기 (v2 호환)
  const [dl] = await Promise.all([pg.waitForEvent('download'), pg.click('[data-act="exportJson"]')]);
  const exported = JSON.parse(fs.readFileSync(await dl.path(), 'utf8'));
  eq(exported.scenes.length, 6, '내보낸 JSON 씬 6개'); eq(exported.meta.style, 'claymation', '내보낸 JSON 화풍'); eq(exported.meta.category, 'history', '내보낸 JSON 카테고리');
  await pg.setInputFiles('#file-in', path.join(FIX, 'legacy_v2_export.json')); await pg.waitForTimeout(500);
  await tab('script');
  eq(await pg.inputValue('input[data-bind="meta.top_title"]'), '아직도 종이호일 태우세요?', 'v2(제미나이) 내보내기 JSON 변환');
  ok((await pg.inputValue('input[data-bind="scenes.0.beats.1"]')).length > 0, 'v2 단문 대본을 3비트로 자동 분할');
  await pg.setInputFiles('#file-in', path.join(OUT, 'exported_dummy.json')).catch(() => {});
  await pg.reload(); await pg.waitForSelector('#stepper .step');
  eq(await pg.inputValue('input[data-bind="meta.top_title"]').catch(() => null) !== undefined, true, '새로고침 후 복원 시도');
  await tab('script'); eq(await pg.inputValue('input[data-bind="meta.top_title"]'), '아직도 종이호일 태우세요?', '새로고침해도 작업 내용 유지(localStorage)');

  ok(errs.length === 0, '서버 모드 콘솔 에러 없음 ' + JSON.stringify(errs));

  // ---- 오프라인(file://) 모드
  const pg2 = await ctx.newPage(); const errs2 = []; pg2.on('console', m => { if (m.type() === 'error') errs2.push(m.text()); }); pg2.on('pageerror', e => errs2.push(e.message));
  await pg2.goto(FILEURL); await pg2.waitForSelector('#stepper .step'); await pg2.waitForTimeout(500);
  ok((await pg2.textContent('#srv-txt')).includes('오프라인'), '오프라인 표시');
  ok((await pg2.textContent('#trend-list')).includes('샘플'), '오프라인 트렌드는 샘플 표시');
  for (const id of ['script', 'visual', 'audio', 'render', 'meta']) { await pg2.click(`[data-act="tab"][data-id="${id}"]`); await pg2.waitForTimeout(150); }
  await pg2.click('[data-act="tab"][data-id="script"]');
  ok((await pg2.inputValue('#master-box')).length > 3000, '오프라인에서도 마스터 프롬프트 생성');
  await pg2.setViewportSize({ width: 390, height: 844 }); await pg2.waitForTimeout(300);
  await pg2.screenshot({ path: path.join(OUT, 'ui_mobile.png') });
  ok(errs2.length === 0, 'file:// 모드 콘솔 에러 없음 ' + JSON.stringify(errs2));

  await browser.close();
  console.log(failed ? `\n${failed}건 실패` : '\n모든 UI 스모크 검사 통과');
  process.exit(failed ? 1 : 0);
})().catch(e => { console.error('테스트 중단:', e); process.exit(2); });
