# AI Shorts Pipeline Studio v3

AI 유튜브 쇼츠 자동 제작 파이프라인. **45초(1.2배속·무음 삭제) · 6씬 · 씬당 7.5초 · 2.5초마다 화각 전환(방법 B, 총 18컷)** 규격으로
대본 → Google Flow(Omni 1.2) 이미지/영상 프롬프트 → 음성 → 1080×1920 합성 → 플랫폼 메타데이터까지 **영상 제작 순서대로** 진행합니다.

**제작 유형은 두 가지로 분리되어 있습니다** (화면 상단 스위치로 전환).

| 모드 | 우선순위 | 흐름 |
|---|---|---|
| 🎬 **레퍼런스 쇼츠 (기본)** | 최우선 | 떡상 영상 링크 → 대본 추출 → **레퍼런스 구조를 역설계해 새 주제로 새 대본** → 이미지·영상 제작 → 최종 편집 |
| 🛒 **쇼핑 쇼츠 (별도)** | 그다음 | 쿠팡·틱톡 상품 선택 → 쇼핑 카테고리 대본 + Scene 06 제휴 CTA → 제작 → 편집 → 쇼핑 고정댓글 |

쇼핑 전용 요소(쇼핑 카테고리, Scene 06 CTA, 쿠팡·틱톡 수집, 제휴 고정댓글 문구)는 **쇼핑 쇼츠 모드에서만** 나타나고 적용됩니다.

> 제미나이에서 작업하던 v2.6 코드가 대화 후반으로 갈수록 누락·충돌이 생겨 처음 대화부터 다시 분석해 새로 만든 버전입니다.

```
① 소재 발굴 → ② 기획·대본 → ③ 이미지·영상(Flow) → ④ 음성 → ⑤ 합성(렌더) → ⑥ 메타데이터
 트렌드/떡상/    마스터 프롬프트   Frame1·Frame2·Omni    TTS·1.2배속   레터박스·자막     YouTube·Reels·TikTok
 벤치마킹 대본    → Claude → 6씬   프롬프트 + 클립 업로드   · 무음 제거    · FFmpeg         × ko/en/ja/zh
```

---

## 1. 제미나이 버전에서 바로잡은 것

| 구분 | 제미나이 v2.6 (문제) | v3 (수정) |
|---|---|---|
| 대시보드 | 소스 URL, 크롤링, 카테고리(단일/합성), 언어, Frame1/Frame2 프롬프트, 음성, 렌더 화면이 **없음**. 메타데이터 "재생성"은 토스트만 띄우는 가짜 버튼 | 제작 순서 6개 탭 + 모든 단계 기능 구현, 실제 서버 연동 |
| 규격 일치 | 샘플 대본이 "335자"라고 주석했지만 **실제 253자**. 라면 샘플은 "332자"라고 했지만 **실제 459자(≈61초)** → 45초 규격 위반 | 글자수 검증기 + 규격에 맞게 다시 쓴 샘플 (325자 / 330자) |
| 식별자 | Python은 `피규어_디오라마`, HTML은 `diorama` → 둘이 어긋남 | `config.json` 한 곳, Python/JS가 같은 템플릿 사용(동일 출력 자동 테스트) |
| 규칙 충돌 | 안전 마진 규칙(익스트림 클로즈업 금지)과 샘플의 `Extreme Close-up` 화각이 충돌. 샘플 프롬프트에 간판·텍스트 묘사 잔존 | 검증기가 경고(⚠️), 샘플은 규칙에 맞게 정정 |
| 크롤러 | 하드코딩 목록을 "크롤링"이라고 표기 | 실제 수집 시도 + 성공한 것만 `LIVE`, 실패 시 `샘플`로 표시하고 사유 안내 |
| 소스 영상 | 링크를 넣는 UI/자막 추출 없음 | V/S 떡상 탐색, 자막 자동 추출(3단계 폴백), 대본 역설계 프롬프트 |
| 스티처 | 자막이 씬당 1개 고정, 9:16 클립에 좌우 검은 기둥(decrease), 따옴표/콜론 이스케이프 문제, 폰트 없으면 실패 | 2.5초 비트 단위 자막(18개), 가로 꽉 채움(cover), 텍스트 파일 방식, 폰트 자동 대체, 클립 길이 자동 보정 |
| 카테고리 | 6개(후기엔 10개 목록과 불일치) | 12개 + 합성(크로스오버) + 트렌드 포맷 4종 |

## 2. 빠른 시작 (Windows)

1. **Python 3.9+** (python.org, 설치 시 *Add python.exe to PATH* 체크) 와 **FFmpeg** (`winget install Gyan.FFmpeg`, 새 터미널에서 `ffmpeg -version` 확인)
2. 이 폴더(`shorts_pipeline/`)를 원하는 곳에 두고 터미널에서:
   ```bash
   python server.py --check      # 환경 점검 ([OK]/[필요] 표시)
   python server.py              # 대시보드 실행 (브라우저가 자동으로 열림)
   ```
   (Windows는 `start_dashboard.bat` 더블클릭도 가능)
3. `assets/` 에 `Pretendard-Black.ttf`, `Pretendard-Bold.ttf` 넣기 (없어도 시스템 한글 폰트로 대체됨 → `assets/README.md`)
4. (선택) `pip install youtube-transcript-api yt-dlp` — 유튜브 자막 자동 추출

> `web_dashboard.html` 을 **더블클릭(file://)** 으로 열어도 대본·프롬프트·메타데이터 작업은 됩니다(오프라인 모드).
> 크롤링, 떡상 탐색, 자막 추출, 클립/음성 업로드, 렌더링은 `python server.py` 로 연 화면에서만 동작합니다.

## 3. 단계별 사용법

### ① 레퍼런스 (쇼핑 모드에서는 "소재 발굴")
**🎬 레퍼런스 쇼츠 모드 (기본)** — 화면 순서:
1. **레퍼런스 영상 → 대본 추출 (최상단)**: 떡상 영상 링크 입력 → [자막/대본 자동 추출](youtube-transcript-api → yt-dlp 자막 → faster-whisper). 실패하면 설명 더보기 → *스크립트 표시* 텍스트를 붙여넣으면 됩니다. 아래에 **새로 만들 영상의 주제**를 적습니다(비우면 Claude가 같은 장르의 새 소재를 제안).
2. **떡상(V/S) 영상 찾기**: YouTube Data API v3 키 필요(Google Cloud Console → API 및 서비스 → YouTube Data API v3 → 사용자 인증 정보 → API 키, 무료 일 10,000 쿼터 / 호출 1회 ≈ 102). `V/S = 조회수 ÷ 구독자수`, 10배 이상 추천. [레퍼런스로 선택]을 누르면 링크와 대본이 바로 채워집니다. 키는 브라우저에만 저장되며 환경변수 `YOUTUBE_API_KEY` 로 줘도 됩니다.
3. **소재 아이디어(선택)**: 레퍼런스 없이 새 주제가 필요할 때 레딧 인기글에서 찾기. 실제 수집에 성공한 항목만 `LIVE`, 막히면 `샘플`로 대체하고 사유를 표시합니다.

**🛒 쇼핑 쇼츠 모드** — 쿠팡 베스트 / 틱톡 상품 수집이 최상단(가장 안정적인 방법은 직접 확인한 상품명을 **[직접 추가]** 하는 하이브리드), 그 아래 떡상 탐색과 (선택) 레퍼런스.

### ② 새 대본 (쇼핑 모드: 기획 · 대본)
1. 새 영상 주제/상단 타이틀/**카테고리**(기본 "자유 주제" - 레퍼런스 구조 우선, 2차를 고르면 합성)/트렌드 포맷/**화풍 7종**/언어(ko·en·ja·zh) 선택
2. **[마스터 프롬프트 복사]** → Claude(웹/앱)에 붙여넣기. 레퍼런스 대본이 있으면 프롬프트에 포함되고 "원본의 리듬 우선" 지시가 붙습니다. 권장 모델: 단일=Sonnet 5.5, 합성=Opus 5.5
3. Claude의 JSON 응답을 붙여넣고 **[씬 가져오기]** → 6씬 × 3비트 대본, Frame1/Frame2, 3컷, 분석, 제목 후보가 채워짐
4. 6씬 대본을 편집(실시간 글자수 · 목표 범위 표시). 쇼핑 모드에서만 Scene 06 CTA 자동 검사/삽입

### ③ 이미지 · 영상 (Google Flow / Omni 1.2)
- 씬마다 **Frame 1(0s) · Frame 2(2.5s) 이미지 프롬프트**와 **Omni 1.2 영상 프롬프트**가 완성형으로 나옵니다(복사 버튼).
  화풍 앵커·안전 마진·`--no text…` 접미사·컷 연결 문구는 자동 합성되므로, 화풍을 바꾸면 6씬 전체가 즉시 바뀝니다.
- Flow에서 생성한 7.5초 클립을 씬 카드에 끌어놓으면 `input/sceneN.mp4` 로 저장됩니다.

### ④ 음성
- TTS 입력 대본(비트/씬/한 덩어리) 복사 → 로컬 TTS(Pinokio Qwen3-TTS 등)로 생성 → `voice_raw` 업로드 → **[처리]** 로 무음 제거 + 1.2배속 → `voice.mp3` (길이 45±3초 점검)

### ⑤ 합성
- 점검 목록(FFmpeg·클립 6/6·음성·폰트·규칙 오류) 확인 → **[최종 렌더링 시작]** → `output/final_shorts.mp4`
- 서버 없이: 프로젝트 JSON 내보내기 후 `python shorts_stitcher.py --project projects/내프로젝트.json`

### ⑥ 메타데이터
- 확정 대본으로 **YouTube Shorts / Instagram Reels / TikTok** × 한/영/일/중 프롬프트(권장 Haiku 5.5) 복사 → 응답 붙여넣기 → 제목·캡션·고정댓글 편집/복사. 쇼핑이면 고정댓글 기본 문구 자동 채움.
- 자동 업로드는 **의도적으로 제외**했습니다(수동 업로드 체크리스트 제공).

## 4. 확정 규격

| 항목 | 값 |
|---|---|
| 러닝타임 | 45초(43~46), 1.2배속 + 무음 삭제 전제, 6씬 × 7.5초 |
| 대본 분량 | ko 공백 포함 **320~350자**(씬 50~58자) / en 90~100단어 / ja 300~330자 / zh 280~310자. 씬 글자수 = 비트 3개를 공백 1칸으로 이은 길이 |
| 방법 B | 씬당 7.5초 단일 클립 안에서 0.0/2.5/5.0초에 화각 전환 → 총 18컷. Frame 1(0s), Frame 2(2.5s) + Omni 3컷 프롬프트 |
| 화풍 7종 | 7 고정밀 피규어&디오라마(기본) · 1 시네마틱 · 2 클레이 · 3 하이퍼리얼 3D · 4 1930s 흑백 · 5 메디컬 매크로 · 6 미니멀 광고. 전 프레임 앞에 앵커 자동 삽입 |
| Zero-Text | 프롬프트에 문자 묘사 금지 + `--no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16` 자동 접미사 |
| 워터마크 | 1.06배 확대 크롭 + 피사체 중앙 70% / 가장자리 15% 여백 문구(익스트림 클로즈업 금지) |
| 쇼핑 CTA | **쇼핑 쇼츠 모드(1차/2차에 `쇼핑`)에서만** Scene 06 마지막 비트에 "제품 정보는 하단 쇼핑 태그와 고정 댓글 확인!" (언어별 번역 문구) |
| 레터박스 | 1080×1920: 상단 0~240(노란 `#FFE500` 타이틀) · 영상 240~1520(1280px) · 자막 하단 바 바로 위 y=1500 기준 아래 정렬 · 하단 1520~1920(UI 보호존) |
| 카테고리 | **자유 주제(기본, 레퍼런스 구조 재구성)**, 역사 비화, 재난 시뮬, B급 병맛, 인체·뇌과학, 건축·공간, 심해·우주, 심리, 기괴한 생태계, 극한 직업, 미해결 미스터리, 미래 기술 + 🛒 쇼핑(쇼핑 모드 전용) (13개) |
| 트렌드 포맷 | 시각적 만족 카타르시스, 딜레마 밸런스 게임, 타임랩스 역사/진화, 비공식 순위 랭킹 |
| 모델 매핑 | Sonnet 5.5(대본/프롬프트) · Opus 5.5(합성·고난도 기획) · Haiku 5.5(다국어·메타데이터) — 핸드오프 문서 기준 표기 |

## 5. 파일 구조

```
shorts_pipeline/
├─ config.json            ★ 모든 규칙/화풍/카테고리/템플릿의 단일 원천 (수정 후 python tools_gen_docs.py)
├─ config.js              config.json + 샘플 + 시드 (자동 생성 - file:// 대시보드용)
├─ prompt_engine.py       대본·프롬프트·메타데이터 엔진, 검증기, Claude 응답 파서 (CLI 포함)
├─ pipeline_core.js       prompt_engine.py 와 동일 로직의 JS 구현 (대시보드용)
├─ source_tools.py        V/S 떡상 탐색(YouTube API), 자막 추출
├─ trend_crawler.py       쿠팡/틱톡/레딧/유튜브 수집 (live 여부를 정직하게 표시)
├─ audio_tools.py         무음 제거 + 1.2배속, 길이 점검, (선택) edge-tts
├─ shorts_stitcher.py     FFmpeg 합성: 6클립 + 음성 + 타이틀 + 비트 자막
├─ server.py              로컬 서버 (127.0.0.1 전용) + 환경 점검(--check)
├─ web_dashboard.html     제작 순서 6탭 대시보드
├─ samples/               ramen_bgrade.json (레퍼런스형 · 병맛, 330자 - 첫 실행 샘플) · airfryer_shopping.json (쇼핑 모드 · CTA, 325자)
├─ data/trends_seed.json  수집 실패 시 쓰는 샘플 소재(수정 가능)
├─ docs/                  자동 생성 예시: prompt_examples.md, master_prompt_example_shopping.md
├─ assets/  input/  output/  projects/   폰트 · 클립/음성 · 결과물 · 서버 저장 프로젝트
└─ tests/                 python -m unittest discover -s tests -v   (50+ 테스트, UI 스모크 포함)
```

## 6. CLI

```bash
python prompt_engine.py master   --project samples/airfryer_shopping.json    # 마스터 프롬프트 출력
python prompt_engine.py package  --project samples/ramen_bgrade.json         # 6씬 Frame1/Frame2/Omni 완성 프롬프트
python prompt_engine.py validate --project samples/ramen_bgrade.json         # 규칙 검증 (종료코드 1 = 오류)
python prompt_engine.py metadata --project samples/airfryer_shopping.json --langs ko,en
python prompt_engine.py parse    --response claude_reply.txt --project my.json   # Claude 응답 가져오기
python shorts_stitcher.py --project samples/ramen_bgrade.json --dry-run      # FFmpeg 명령만 확인
python shorts_stitcher.py --project projects/my.json --fit contain --crop 1.08
python audio_tools.py tts_raw.wav input/voice.mp3                            # 무음 제거 + 1.2배속
python trend_crawler.py --offline                                            # 수집기 확인
python source_tools.py outliers "kitchen gadget" --min-ratio 10              # YOUTUBE_API_KEY 필요
```

## 7. 규칙을 바꾸고 싶을 때

`config.json` 을 수정(화풍 앵커, 카테고리 뼈대, 글자수, CTA 문구, 레이아웃 px …)하고 `python tools_gen_docs.py` 를 실행하면 `config.js`와 `docs/`가 갱신됩니다.
`python -m unittest discover -s tests` 가 Python과 JS 출력이 같은지, `config.js`가 최신인지 확인합니다.

## 8. 확인이 필요한 부분 (솔직한 한계)

**제가 결정한 것 (원하시면 바꾸세요)**
- 합성 영상 채움 기본값은 `cover`(가로 꽉 채움). 제미나이 코드는 `decrease`라 9:16 클립에 좌우 검은 기둥이 생겼습니다. 원본 비율을 지키려면 대시보드 5단계에서 `contain`.
- **세로 안전구역 불일치**: 9:16 원본을 1080×1280 상자에 cover 로 넣고 1.06배 크롭하면 원본의 **세로 62.9%만** 보입니다. 규격의 "중앙 70%"보다 좁아서 피사체를 세로 중앙 약 60% 안에 두는 게 안전합니다(미리보기 주황 경고). 규격 숫자는 그대로 두었습니다.
- 익스트림 클로즈업은 "금지"가 아니라 **경고**로 처리합니다(AVD용 초근접 컷 규칙과 충돌했기 때문).
- 쇼핑 CTA 문구는 핸드오프 문서 버전("제품 정보는 하단 쇼핑 태그와 고정 댓글 확인!")을 채택했습니다.
- 카테고리는 "10대 영구 카테고리" + 기존 블루프린트의 인체·뇌과학/건축·공간 + 기본값용 "자유 주제"(레퍼런스 구조 우선)를 합쳐 13개입니다.
- 쇼핑 모드는 쇼핑이 항상 1차 카테고리입니다(기존 "역사 → 쇼핑" 합성은 "쇼핑 1차 + 역사 2차"로 바뀝니다).

**검증하지 못한 것**
- **Windows 실행**: 개발/테스트는 Linux에서 했습니다. Windows 폰트 경로 이스케이프(`C\:/…`)는 단위 테스트로 형식만 확인했고 실제 렌더는 못 해봤습니다.
- **쿠팡 수집**: 봇 차단(403)이 흔해 실시간 수집이 되지 않을 수 있습니다(구현은 하되 실패 시 샘플+사유 표시). **틱톡 크리에이티브 센터는 공식 API가 없어 자동 수집을 하지 않습니다**(수동 링크 제공).
- **YouTube API / 자막 추출 / 레딧**: 실제 네트워크 호출은 하지 않고 목(mock) 응답으로만 테스트했습니다. 실제 키로 첫 호출 시 오류가 나면 알려주세요.
- **Claude CLI 실행 버튼, edge-tts 버튼**: 실험 기능이며 실제 실행 검증은 하지 못했습니다(없을 때의 에러 경로만 테스트).
- Google Flow(Omni 1.2)의 워터마크 위치·컷 전환 품질은 서비스 변화에 따라 달라질 수 있습니다(확실하지 않음). 이 도구는 프롬프트와 후처리만 담당합니다.

## 9. 새 세션에서 이어서 작업할 때

제미나이의 "이어서해줘" 대신, 이 폴더의 **`README.md`(규격·결정 사항)** 와 **`config.json`(규칙 원본)**, **`tests/`(동작 명세)** 를 읽히면 됩니다.
작업 상태는 `projects/*.json`(서버 저장) 또는 [내보내기]한 프로젝트 JSON에 모두 들어 있고, 대시보드는 브라우저에도 자동 저장합니다.
제미나이 v2.6 대시보드에서 내보낸 JSON도 [불러오기]로 읽어 v3 형식으로 변환합니다(Frame1/2와 3비트 분할은 직접 확인 필요).
