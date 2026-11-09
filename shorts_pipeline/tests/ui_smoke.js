// 브라우저 스모크 테스트: node tests/ui_smoke.js <서버URL> <file://대시보드URL> <클립.mp4> <음성.wav> <산출물폴더>
// (Playwright 필요: npm i -g playwright, NODE_PATH 지정)
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const [SERVER, FILEURL, CLIP, WAV, OUT, REFPNG, FONTFILE] = process.argv.slice(2);
const FIX = path.join(__dirname, 'fixtures');
let failed = 0; const ok = (c, m) => { if (!c) { failed++; console.log('FAIL:', m); } else console.log('ok  :', m); };
const eq = (a, b, m) => ok(a === b, `${m} (기대 ${JSON.stringify(b)}, 실제 ${JSON.stringify(a)})`);

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1500, height: 1000 }, acceptDownloads: true });
  await ctx.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: new URL(SERVER).origin });
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
  eq((await pg.$$('#stepper .step')).length, 7, '스테퍼 7단계(기준 이미지 포함)');
  ok((await txt('#stepper .step:nth-child(3)')).includes('기준 이미지'), '3단계 = 기준 이미지');
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


  // ===== 기준 이미지 (등장 인물·사물 일관성)
  await pg.fill('#claude-reply', fs.readFileSync(path.join(FIX, 'claude_reply.txt'), 'utf8')); await pg.click('[data-act="importReply"]'); await pg.waitForTimeout(300);
  ok((await txt('#toast')).includes('기준 이미지 대상 3개'), 'Claude 응답에 포함된 assets 3개 가져오기');
  await tab('assets');
  eq((await pg.$$('[data-asset]')).length, 3, '기준 이미지 카드 3개(인물/사물/장소)');
  ok((await txt('#ref-0-main')).startsWith('Hyper-detailed collectible PVC figure') && (await txt('#ref-0-main')).includes('full-body character reference image'), '인물 기준 이미지 프롬프트(화풍 앵커 + 전신 기준)');
  ok((await txt('#ref-0-main')).endsWith('--no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16'), '기준 이미지 Zero-Text 접미사 + 9:16');
  ok((await txt('#ref-0-sheet')).includes('turnaround reference sheet') && (await txt('#ref-0-sheet')).endsWith('--ar 16:9'), '3면 턴어라운드 시트 프롬프트 + 16:9');
  ok((await txt('#ref-1-main')).includes('single hero object reference image'), '사물 기준 이미지 프롬프트');
  ok((await txt('#ref-2-main')).includes('establishing reference image'), '장소 기준 이미지 프롬프트');
  await pg.fill('textarea[data-bind="assets.0.appearance"]', 'a male figure with a bright red scarf');
  ok((await txt('#ref-0-main')).includes('a male figure with a bright red scarf'), '외형 수정이 기준 이미지 프롬프트에 즉시 반영');
  await tab('visual');
  ok((await txt('#fin-0-frame1')).includes('a male figure with a bright red scarf'), '외형 수정이 연결된 씬 프레임 프롬프트에 자동 삽입');
  ok((await txt('#fin-0-frame1')).includes('tiny miniature studio-apartment kitchen'), 'Scene 01 에는 장소(주방) 외형도 삽입');
  ok(!(await txt('#fin-3-frame1')).includes('tiny miniature studio-apartment kitchen'), '연결되지 않은 Scene 04 에는 주방 외형 없음');
  ok((await txt('#content')).includes('기준 이미지') && (await txt('#content')).includes('아직 생성되지 않았습니다'), '기준 이미지 미생성 경고 배너');
  ok((await txt('details[data-scene="0"]')).includes('이 씬 이미지에 참조로 첨부할 기준 이미지'), '씬 카드에 첨부할 기준 이미지 안내');
  await tab('assets');
  await pg.click('label.chip:has([data-ref="2:3"])'); await pg.waitForTimeout(250);
  await tab('visual'); ok((await txt('#fin-3-frame1')).includes('tiny miniature studio-apartment kitchen'), '씬 연결 체크 시 해당 씬에 외형 삽입');
  await tab('assets'); await pg.click('label.chip:has([data-ref="2:3"])'); await pg.waitForTimeout(250);
  await tab('visual'); ok(!(await txt('#fin-3-frame1')).includes('tiny miniature studio-apartment kitchen'), '연결 해제 시 외형 제거');

  // 추가/삭제/검증
  await tab('assets'); await pg.click('[data-act="addAsset"][data-t="object"]'); await pg.waitForTimeout(250);
  eq((await pg.$$('[data-asset]')).length, 4, '사물 추가');
  ok((await txt('#issues')).includes('외형 묘사(appearance)가 비어 있습니다') && (await txt('#issues')).includes('어느 씬에도 연결되지 않았습니다'), '빈 외형/미연결 경고');
  await pg.click('[data-asset="obj"] [data-act="delAsset"]'); await pg.waitForTimeout(250);
  eq((await pg.$$('[data-asset]')).length, 3, '삭제');
  await pg.fill('input[data-bind="assets.1.label"]', '한글 라벨'); ok((await txt('#issues')).includes('영문만 허용'), '한글 라벨은 오류'); await pg.fill('input[data-bind="assets.1.label"]', 'the small silver pot');

  // 업로드/미리보기/삭제
  await pg.setInputFiles('input[data-upload="ref"][data-id="hero"]', REFPNG); await pg.waitForTimeout(900);
  ok((await pg.$('[data-asset="hero"] img[src*="/media/refs/hero.png"]')) !== null, '기준 이미지 업로드 후 썸네일 표시');
  await pg.click('[data-act="delRef"][data-id="hero"]'); await pg.waitForTimeout(700);
  eq(await pg.$('[data-asset="hero"] img'), null, '기준 이미지 삭제');
  await pg.click('[data-act="copyAssetAnalysis"]'); await pg.waitForTimeout(300);
  const clip = await pg.evaluate(() => navigator.clipboard.readText());
  ok(clip.includes('[기준 이미지 분석 지침]') && clip.includes('Scene 01: 라면 끓일 때마다') && clip.includes('scene_refs'), '대본 분석 프롬프트 복사(실제 클립보드 내용 확인)');

  // 분석 결과 가져오기
  await pg.fill('#asset-reply', fs.readFileSync(path.join(FIX, 'assets_reply.txt'), 'utf8')); await pg.click('[data-act="importAssets"]'); await pg.waitForTimeout(300);
  eq((await pg.$$('[data-asset]')).length, 3, '분석 결과 가져오기 -> 등장 대상 3개');
  ok(await pg.isVisible('[data-asset="hero_man"]') && await pg.isVisible('[data-asset="pot_2"]'), 'id 정규화(공백/중복 처리)');
  await pg.fill('#asset-reply', '자산 없음'); await pg.click('[data-act="importAssets"]'); await pg.waitForTimeout(200);
  ok((await txt('#toast')).includes('assets 배열'), '잘못된 분석 응답은 에러 토스트');
  await tab('script');

  // ===== 카메라 구도 경고 / 정책 안전 (Flow 차단 대응)
  await tab('visual');
  ok((await txt('#fin-0-frame1')).includes('all characters are clearly adult'), '인물 대상이 있는 씬에는 성인 명시 문구 자동 삽입');
  await pg.uncheck('input[data-check="options.adult_safe"]'); await pg.waitForTimeout(250);
  ok(!(await txt('#fin-0-frame1')).includes('all characters are clearly adult'), '성인 문구 옵션 해제 시 삽입 안 됨');
  await pg.check('input[data-check="options.adult_safe"]'); await pg.waitForTimeout(250);
  const f3 = 'textarea[data-bind="scenes.2.frame1"]';
  await pg.click('details[data-scene="2"] summary'); await pg.waitForTimeout(200);
  await pg.fill(f3, 'macro close-up of a pot lid'); ok(!(await txt('#issues')).includes('익스트림 클로즈업'), "흔한 'macro close-up' 은 경고하지 않음");
  await pg.fill(f3, 'extreme close-up of a pot lid'); ok((await txt('#issues')).includes('익스트림 클로즈업'), '익스트림 클로즈업은 경고');
  await pg.uncheck('input[data-check="options.camera_warn"]'); await pg.waitForTimeout(250);
  ok(!(await txt('#issues')).includes('익스트림 클로즈업'), '구도 경고 옵션을 끄면 경고 없음');
  await pg.check('input[data-check="options.camera_warn"]'); await pg.waitForTimeout(250);
  await pg.click('[data-act="fixCamera"]'); await pg.waitForTimeout(250);
  eq(await pg.inputValue(f3), 'close-up with generous negative space of a pot lid', '구도 표현 자동 교정');
  ok(!(await txt('#issues')).includes('익스트림 클로즈업'), '교정 후 경고 사라짐');
  const f6 = 'textarea[data-bind="scenes.5.frame1"]';
  await pg.click('details[data-scene="5"] summary'); await pg.waitForTimeout(200);
  await pg.fill(f6, 'a little boy and a cute girl in the kitchen');
  ok((await txt('#issues')).includes('미성년자 관련 콘텐츠로 차단될 수 있습니다') && (await txt('#issues')).includes('어려 보일 수 있는 표현'), '미성년자/어려 보이는 표현 정책 경고');
  await pg.click('details[data-scene="5"] details.acc summary'); await pg.waitForTimeout(200);
  await pg.click('[data-act="copyPolicyFix"][data-i="5"]'); await pg.waitForTimeout(250);
  const fixClip = await pg.evaluate(() => navigator.clipboard.readText());
  ok(fixClip.includes('[정책 안전 재작성]') && fixClip.includes('Scene 06') && fixClip.includes('little boy'), '정책 안전 재작성 프롬프트(위험 단어 포함) 복사');
  await pg.fill('#fix-5', '```json\n{"frame1": "an adult man standing in the kitchen --no text", "assets": [{"id": "hero_man", "appearance": "a 35-year-old adult male PVC figure with short black hair"}]}\n```');
  await pg.click('[data-act="applyPolicyFix"][data-i="5"]'); await pg.waitForTimeout(300);
  eq(await pg.inputValue(f6), 'an adult man standing in the kitchen', '재작성 결과 적용(--no 접미사 제거)');
  ok(!(await txt('#issues')).includes('little boy'), '적용 후 정책 경고 해소');
  await tab('assets'); ok((await pg.inputValue('textarea[data-bind="assets.0.appearance"]')).includes('35-year-old adult'), '재작성 결과의 인물 외형(성인 연령)도 기준 이미지에 반영');
  await pg.fill('textarea[data-bind="assets.0.appearance"]', 'a male figure with short black hair');
  ok((await txt('#issues')).includes('연령(adult / 30-year-old 등) 명시가 없습니다'), '인물 외형에 성인 연령이 없으면 경고');
  await pg.fill('textarea[data-bind="assets.0.appearance"]', 'a 30-year-old adult male PVC figure with short black hair');
  await tab('script');

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
  // 설정값이 실제로 전달되는지 (처리 버튼을 누르면 화면을 먼저 다시 그려 값이 초기화되던 버그의 회귀 방지)
  await pg.fill('input[data-au="speed"]', '1'); await pg.uncheck('input[data-au="sil"]');
  const [req1] = await Promise.all([pg.waitForRequest('**/api/audio/process'), pg.click('[data-act="processVoice"]')]);
  const b1 = req1.postDataJSON();
  ok(b1.speed === 1 && b1.remove_silence === false && !('fit_seconds' in b1), '처리 요청에 입력한 속도/무음 설정이 그대로 전달: ' + JSON.stringify(b1));
  await pg.waitForTimeout(2500);
  ok((await txt('#content')).includes('길이 점검') && (await txt('#content')).includes('음성 3.0초'), '원속도 + 무음 유지 = 3.0초 (설정이 결과에 반영)');
  eq(await pg.inputValue('input[data-au="speed"]'), '1', '처리 후에도 입력한 속도 유지');
  ok(!(await pg.isChecked('input[data-au="sil"]')), '처리 후에도 무음 제거 해제 상태 유지');
  await pg.check('input[data-au="fit"]'); await pg.waitForTimeout(200);
  ok(await pg.isDisabled('input[data-au="speed"]'), '자동 속도 선택 시 속도 입력 비활성');
  const [req2] = await Promise.all([pg.waitForRequest('**/api/audio/process'), pg.click('[data-act="processVoice"]')]);
  eq(req2.postDataJSON().fit_seconds, 45, '자동 속도: 목표 45초 전달'); await pg.waitForTimeout(2500);
  ok((await txt('#content')).includes('마지막 처리: 속도 0.5x') && (await txt('#content')).includes('제한됨'), '3초 음성을 45초로 늘리면 0.5x 로 제한됨을 안내');
  await pg.click('[data-act="calibrateTiming"]'); await pg.waitForTimeout(300);
  ok(!(await txt('#m-chars')).includes('320~350') && (await txt('#issues')).includes('실측 TTS 속도'), '실측 속도 보정: 목표 글자수 범위가 바뀌고 점검 기준도 변경');
  await pg.click('[data-act="resetTiming"]'); await pg.waitForTimeout(300);
  ok((await txt('#m-chars')).endsWith('/ 320~350'), '보정 해제 시 기본 범위(320~350) 복귀: ' + await txt('#m-chars'));
  await tab('render');
  ok((await txt('#content')).includes('씬 클립 1/6'), '렌더 점검: 클립 1/6');
  // 레터박스 / 타이틀 / 자막 스타일 조정 (미리보기 즉시 반영)
  await pg.fill('input[data-bind="render.top_bar"]', '300'); await pg.fill('input[data-bind="render.bottom_bar"]', '200');
  ok((await txt('#pv-info')).includes('상단 300px') && (await txt('#pv-info')).includes('하단 200px'), '레터박스 높이 변경이 미리보기에 반영');
  ok((await txt('#content')).includes('1420px'), '영상 영역 높이 자동 계산(1920-300-200)');
  await pg.fill('input[data-bind="render.bar_color"]', '#112233');
  eq(await pg.$eval('#cv', (e) => e.style.background), 'rgb(17, 34, 51)', '바 색상 반영');
  await pg.fill('input[data-bind="render.title_color"]', '#00ff00');
  eq(await pg.$eval('#pv-title', (e) => e.style.color), 'rgb(0, 255, 0)', '타이틀 색 반영');
  await pg.fill('input[data-bind="render.sub_size"]', '80');
  ok(parseFloat(await pg.$eval('#pv-sb span', (e) => e.style.fontSize)) > 15, '자막 크기 반영');
  await pg.fill('input[data-bind="render.sub_color"]', '#ffff00');
  eq(await pg.$eval('#pv-sb span', (e) => e.style.color), 'rgb(255, 255, 0)', '자막 글자 색 반영');
  await pg.uncheck('input[data-check="render.sub_box"]'); await pg.waitForTimeout(250);
  eq(await pg.$eval('#pv-sb span', (e) => e.style.background), 'none', '자막 배경 박스 해제');
  await pg.fill('input[data-bind="render.top_bar"]', '900'); await pg.fill('input[data-bind="render.bottom_bar"]', '900');
  ok((await txt('#content')).includes('400px 이상이어야 합니다'), '영상 영역이 400px 미만이면 경고');
  await pg.fill('input[data-bind="render.top_bar"]', '300'); await pg.fill('input[data-bind="render.bottom_bar"]', '200');
  ok((await pg.$$eval('select[data-bind="render.sub_font"] option', (o) => o.length)) >= 1, '글꼴 선택 목록');
  if (FONTFILE) {
    await pg.setInputFiles('input[data-upload="font"]', FONTFILE); await pg.waitForTimeout(900);
    const spec = await pg.$eval('select[data-bind="render.title_font"] optgroup[label^="assets"] option', (o) => o.value);
    ok(spec.startsWith('assets:'), '업로드한 글꼴이 assets 그룹 목록에 표시: ' + spec);
    await pg.selectOption('select[data-bind="render.title_font"]', spec); await pg.waitForTimeout(200);
    await pg.waitForFunction(() => Array.from(document.fonts).some((f) => f.family.indexOf('pv_') === 0 && f.status === 'loaded'), null, { timeout: 8000 });
    ok(true, '선택한 글꼴이 미리보기에 실제로 로드됨');
  }
  await pg.check('#rd-partial'); await pg.click('[data-act="startRender"]');
  await pg.waitForFunction(() => /렌더링 완료|\[오류\]/.test(document.getElementById('rd-log').textContent), null, { timeout: 90000 });
  ok((await txt('#rd-log')).includes('렌더링 완료'), '부분 렌더 완료: ' + (await txt('#rd-log')).slice(-80));
  await pg.waitForTimeout(800); ok((await pg.$('#content video')) !== null, '결과 영상 플레이어');
  await pg.screenshot({ path: path.join(OUT, 'ui_render_done.png') });
  await pg.click('[data-act="resetRender"]'); await pg.waitForTimeout(250);
  eq(await pg.inputValue('input[data-bind="render.top_bar"]'), '240', '스타일 기본값 복원(상단 바)');
  eq(await pg.inputValue('input[data-bind="render.sub_size"]'), '52', '스타일 기본값 복원(자막 크기)');

  // ---- 메타데이터
  await tab('meta'); await pg.click('[data-act="metaLang"][data-k="en"]');
  eq(await pg.inputValue('input[data-meta="title"]'), '', '메타데이터 없는 언어 탭은 빈 칸');
  await pg.click('[data-act="metaLang"][data-k="ko"]'); await pg.fill('#meta-reply', fs.readFileSync(path.join(FIX, 'meta_reply.txt'), 'utf8')); await pg.click('[data-act="importMeta"]'); await pg.waitForTimeout(300);
  eq(await pg.inputValue('input[data-meta="title"]'), '새 제목', '메타데이터 응답 적용');
  await pg.click('[data-act="metaPlat"][data-k="instagram"]'); eq(await pg.inputValue('input[data-meta="title"]'), 'i', '플랫폼 탭 전환');

  // ---- 내보내기 / 불러오기 (v2 호환)
  const [dl] = await Promise.all([pg.waitForEvent('download'), pg.click('[data-act="exportJson"]')]);
  const exported = JSON.parse(fs.readFileSync(await dl.path(), 'utf8'));
  eq(exported.scenes.length, 6, '내보낸 JSON 씬 6개'); ok(exported.assets.length === 3 && !('subject_anchor' in exported), '내보낸 JSON 에 assets 포함, 옛 subject_anchor 없음'); eq(exported.meta.style, 'claymation', '내보낸 JSON 화풍'); eq(exported.meta.category, 'history', '내보낸 JSON 카테고리');
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
