# AI 숏드라마 제작 교실

유튜브 쇼츠·인스타그램 릴스에서 보던 **AI 숏폼 드라마**를 기획부터 업로드까지 12단계로 따라 하며 직접 만드는 개인 실습 교재예요. (2026년 10월 23일 기준)

- **`index.html`**: 체크리스트, 내 작품 기획서(프롬프트 자동 생성), 복사 버튼이 있는 실습 페이지예요. 브라우저로 열면 바로 쓸 수 있고, 진행 상황은 그 브라우저에 저장돼요.
- **이 README**: 같은 내용을 읽기 좋게 옮긴 글 버전이에요. 체크박스(☐)는 진행 상황을 적어 보는 칸이에요.
- Claude 아티팩트로 열면 진행 상황이 계정에 저장되고 AI 코치(대본·샷리스트 자동 생성, 질문하기)도 쓸 수 있어요.

> AI 도구의 가격·무료 한도·기능은 몇 주 단위로 바뀌어요. 결제하거나 수익화를 시작하기 전에는 각 서비스의 공식 페이지를 다시 확인하세요.

---

유튜브 쇼츠와 인스타그램 릴스에서 보던 AI 숏폼 드라마를 직접 만들어 봐요. 기획부터 업로드까지 12단계로 나눴어요. 예제 작품 「알바생의 정체」를 그대로 따라 하면 60초짜리 첫 편이 완성되고, 두 번째 편은 내 이야기로 만듭니다.

- **작품**: 나의 첫 AI 숏드라마
- **분량**: 60초 · 12컷
- **화면**: 9:16 세로
- **첫 편 소요**: 8~12시간

시작하기 전에 · 3분

## 2026년 10월, AI 숏드라마는 여기까지 왔어요

AI 숏드라마는 9:16 세로 화면에 1~3분짜리 이야기를 담은 영상이에요. 첫 3초에 시선을 잡고, 갈등과 반전을 빠르게 지나, 다음 화가 궁금하게 끝나는 게 공식이에요. 배우와 촬영 대신 이미지·영상 생성 AI로 장면을 만들고, AI 음성으로 대사를 입혀요.

- **만들기는 쉬워졌어요.** 2026년 10월 전 세계에 출시된 Kling 4.0은 한 번에 최대 30초를 만들고, 키프레임 10장과 참고 자료 15개를 넣을 수 있어요. 한국어를 포함한 여러 언어의 립싱크도 지원한다고 발표했어요.
- **그만큼 경쟁도 치열해요.** 중국에서는 2026년 1분기에 공개된 숏드라마 약 12만 8천 편 가운데 95% 이상이 AI 작품이었어요. 그런데 춘제 기간 분석을 보면 AI 작품이 실사 작품보다 50배 많았는데도 전체 조회수는 실사가 25배 많았어요. 승부는 도구보다 이야기와 감정에서 나요. 이 교실이 기획과 대본에 시간을 많이 쓰는 이유예요.
- **국내도 움직이고 있어요.** 숏드라마 플랫폼 비글루는 2026년 7월 AI 숏드라마 제작 플랫폼 ‘비글루 스튜디오’ 베타를 공개했고, SNS 피드에서도 AI 숏폼이 빠르게 늘고 있어요.

### 예전 강의를 볼 때 주의할 변화

| 바뀐 것                   | 내용                                                                                                           | 이 교실에서는                     |
|---------------------------|----------------------------------------------------------------------------------------------------------------|-----------------------------------|
| **Sora 종료**             | OpenAI의 Sora 앱은 2026년 4월 서비스를 끝냈어요.                                                               | Sora가 나오는 강의는 건너뛰세요.  |
| **Kling 4.0** (10월)      | 30초 생성, 키프레임·참고 자료 확대, 한국어 립싱크 지원 발표                                                    | 기본 영상 도구                    |
| **Veo 3.1 · Gemini Omni** | Google Flow에서 Veo 3.1(Lite·Fast·Quality)과 5월에 공개된 Gemini Omni Flash를 써요.                            | 보조 영상 도구                    |
| **나노바나나 2 · Pro**    | Gemini 앱의 이미지 생성·편집 기능. 인물 일관성은 Pro가 더 좋아요.                                              | 캐릭터·장면 이미지                |
| **CapCut 유료화**         | 자동 자막 같은 AI 기능 상당수가 유료 요금제로 옮겨 갔어요.                                                     | 자막은 Vrew 무료 범위로           |
| **YouTube 기준** (7월)    | 틀만 바꾼 대량 반복 영상, 불쾌·충격 영상, 민감 주제를 말하는 AI 인물 영상은 수익을 낼 수 없다고 명확히 했어요. | STEP 12와 ‘꼭 지킬 규칙’에서 설명 |

시작 1 · 2분

## 내 제작 방식 고르기

고른 방식에 맞는 도구가 단계마다 ‘내 방식’으로 표시돼요. 언제든 바꿀 수 있어요.

#### 무료 체험 · 0원

일단 한 편 만들어 보고 싶을 때

- 이미지: Gemini 무료(나노바나나)
- 영상: Kling 무료 크레딧, Google Flow 무료 하루 50크레딧
- 음성: Kling 영상 속 대사, Typecast 무료 범위
- 편집: CapCut 기본 기능, Vrew 자막
- 음악: YouTube 오디오 보관함

워터마크가 붙고 하루 생성량이 적어 완성까지 4~7일 걸려요. 무료 결과물은 대부분 상업적으로 쓸 수 없어요.

#### 가성비 · 월 2.5만 원 안팎

꾸준히 올리면서 수익화를 준비할 때

- Google AI Plus 월 11,000원 (나노바나나 Pro, Flow 포함)
- Kling Standard 월 \$8.80 (660크레딧, 첫 달 할인)
- 음성: Kling 대사 + 필요한 컷만 Typecast
- 편집: CapCut + Vrew

한 편에 영상을 20~30번 생성하면 Kling 크레딧이 빠듯할 수 있어요. 시안은 Flow로 만들어 아끼세요.

#### 본격 연재 · 월 7만 원부터

주 2~3편씩 시리즈를 올릴 때

- Google AI Pro 월 29,000원 (Veo 3.1·Omni 한도 확대)
- Kling Pro 월 \$32.56 (3,000크레딧)
- 음성: Typecast·ElevenLabs 유료로 인물 목소리 통일
- 음악: Suno Pro 월 \$10 (상업적 이용)
- 필요하면 CapCut 유료

쓰지 않는 달은 해지하세요. 결제 전 약관의 상업적 이용 조항을 꼭 확인하세요.

**가격:** 2026년 10월에 확인한 가격이에요. Kling은 달러로 결제하고 첫 달 할인가가 따로 있어요. Google AI Plus는 11월 중순에 혜택이 바뀐다는 보도가 있으니 결제 전에 공식 요금 페이지를 확인하세요.

시작 2 · 30분

## 준비물과 작업 폴더

계정을 한 번에 만들어 두면 작업 흐름이 끊기지 않아요. 모두 무료 가입으로 시작할 수 있어요.

| 용도        | 도구                                   | 주소                                                                        |
|-------------|----------------------------------------|-----------------------------------------------------------------------------|
| 대본        | AI 챗봇 하나 (ChatGPT, Gemini, Claude) | 평소 쓰는 것                                                                |
| 이미지      | Gemini (나노바나나)                    | [gemini.google.com](https://gemini.google.com)                              |
| 영상        | Kling AI                               | [klingai.com](https://klingai.com)                                          |
| 영상 (보조) | Google Flow                            | [labs.google/flow](https://labs.google/flow)                                |
| 음성        | Typecast 또는 ElevenLabs               | [typecast.ai](https://typecast.ai) · [elevenlabs.io](https://elevenlabs.io) |
| 편집·자막   | CapCut, Vrew                           | [capcut.com](https://www.capcut.com) · [vrew.ai](https://vrew.ai)           |

**작업 폴더 구조** · 컴퓨터나 클라우드 드라이브

``` text
알바생의정체/
├─ 01_기획      기획서 · 대본 · 샷리스트
├─ 02_캐릭터    인물별 레퍼런스 3장 + 장소 1장
├─ 03_장면      컷01.png ~ 컷12.png
├─ 04_영상      컷01_v1.mp4 …
├─ 05_음성      컷03_서윤.wav …
├─ 06_사운드    배경음악 · 효과음
├─ 07_편집      편집 프로젝트 · 완성본
└─ 08_업로드    제목 · 설명 · 커버
```

### 준비 체크리스트

- [ ] Google 계정으로 Gemini에 들어가 보기
- [ ] Kling AI에 가입하고 무료 크레딧 확인하기
- [ ] 대본용 AI 챗봇 하나 정하기
- [ ] 음성 서비스(Typecast 또는 ElevenLabs) 가입하기
- [ ] CapCut과 Vrew 설치하기
- [ ] 작업 폴더 8개 만들기

시작 3 · 이 그림 하나만 기억하세요

## 60초 황금 구조

| 구간                    | 할 일                                                       | 예제 「알바생의 정체」                   |
|-------------------------|-------------------------------------------------------------|------------------------------------------|
| **0~3초 훅**            | 가장 센 장면이나 대사로 시작해 스크롤을 멈추게 해요.        | 커피잔이 쾅, “이걸 커피라고 준 거야?!”   |
| **3~15초 상황**         | 누가, 어디서, 무슨 일인지 보여 줘요.                        | 진상 손님 오 부장의 갑질                 |
| **15~30초 갈등**        | 주인공이 몰리는 순간. 시청자의 분노와 궁금증이 가장 커져요. | “사장 나오라 그래!”, 손님들의 수군거림   |
| **30~45초 반전**        | 숨겨진 정체나 진실을 공개해요.                              | 비서: “대표님, 이사회 십 분 전입니다.”   |
| **45~60초 사이다·떡밥** | 통쾌한 한마디로 마무리하고, 다음 화가 궁금하게 끝내요.      | “곧 또 뵙겠네요, 부장님.” → 2화에서 계속 |

### 예제의 편집 타임라인 (실제 길이 비율)

(타임라인 그림) 60초 편집 타임라인. 구조: 훅 0~3초, 상황 3~15초, 갈등 15~30초, 반전 30~45초, 사이다와 떡밥 45~60초. 영상 12컷, 대사 9곳, 음악은 긴장 3~30초, 정적, 반전 테마 35~53초, 엔딩 53~60초. 효과음과 자막 위치 포함.

파란 칸이 컷, 초록 칸이 소리, 호박색 칸이 화면 글자예요. 반전(30초) 직전에 음악을 끊고 문 종소리만 들리게 한 부분을 눈여겨보세요.

## PART 1 · 이야기

STEP 1~4 · 무엇을 보여 줄지 정해요

이야기 · STEP 01 · 약 40분

## STEP 01 · 잘 되는 AI 숏드라마 10편 뜯어보기

**끝나면:** 인기 작품의 공식이 눈에 들어오고, 내가 만들 장르가 정해져요.

유튜브에서 ‘AI 드라마’, ‘AI 숏드라마’, ‘AI 쇼츠 드라마’를 검색하고 필터를 ‘Shorts’로 바꿔 보세요. 인스타그램은 \#ai드라마 \#숏드라마 해시태그를 보면 돼요. 끝까지 본 영상과 넘긴 영상을 나눠 적으면 내가 무엇에 끌리는지 보여요.

### 볼 때 체크할 것

- 길이와 컷 수: 몇 초마다 화면이 바뀌나요?
- 첫 3초에 나온 장면과 대사
- 인물 수와 장소 수
- 반전이 나온 시점 (몇 초쯤?)
- 마지막 장면이 다음 화를 어떻게 부르나요?
- 댓글에 많이 나온 말

### 자주 보이는 인기 공식

- 신분 반전 “알고 보니 ○○”
- 참교육·사이다
- 계약·재벌 로맨스
- 회귀·환생 복수
- 1분 미스터리
- AI 사극 “조선에 ○○가 있었다면”
- 동물·아기 시점 코미디

**벤치마킹 노트** · 메모 앱에 붙여 넣고 영상마다 채우기

``` text
[벤치마킹 노트]
영상 제목 / 링크:
길이:       초 / 컷 수:
첫 3초에 나온 것:
인물 수 / 장소 수:
갈등:
반전 시점(몇 초) / 내용:
마지막 장면(다음 화 유도):
댓글에 많이 나온 말:
내가 가져올 점 한 가지:
```

### STEP 1 체크리스트

- [ ] AI 숏드라마 10편 보기 (끝까지 본 것과 넘긴 것 구분)
- [ ] 벤치마킹 노트 5편 이상 쓰기
- [ ] 따라 하고 싶은 훅 3개 메모하기
- [ ] 내가 만들 장르 하나 고르기

이야기 · STEP 02 · 약 30분

## STEP 02 · 장르·인물·반전 정하기

**끝나면:** 한 줄 요약(로그라인)과 인물 2~3명이 정해져요.

**3·2·1 규칙:** 인물은 3명 이하, 장소는 2곳 이하, 반전은 1개. 인물과 장소가 늘수록 AI가 얼굴과 배경을 헷갈려요.

| AI가 잘하는 장면                        | 아직 어려운 장면                      |
|-----------------------------------------|---------------------------------------|
| 클로즈업 감정 연기 (분노, 충격, 미소)   | 격투·액션, 빠른 몸싸움                |
| 두 사람의 대화                          | 요리·악기·타이핑 같은 빠른 손동작     |
| 고급스러운 공간 (재벌집, 사무실, 카페)  | 여러 사람이 동시에 주고받는 장면      |
| 사극·판타지 배경                        | 간판·문서처럼 정확해야 하는 글자      |
| 천천히 걷기, 돌아보기, 문 열고 들어오기 | 스포츠, 자동차 추격                   |
| 비·눈·노을 같은 분위기 연출             | 소품 위치가 컷마다 똑같아야 하는 장면 |

### 로그라인 공식

\[주인공\] 이 \[상황\] 에서 \[갈등\] 을 겪는데, 사실은 \[반전\] 이었다.

**예제:** 카페 알바생 서윤이 진상 손님에게 갑질을 당하는데, 사실 그녀는 그 손님의 회사를 인수하는 그룹의 대표였다.

**아이디어 10개 받기** · ChatGPT · Gemini · Claude

``` text
AI 숏드라마 아이디어 10개를 표로 정리해 줘.
조건: 장르는 [원하는 장르], 길이 60초, 인물 3명 이하, 장소 2곳 이하, 마지막에 반전, 격한 액션 없음, 실존 인물·브랜드 없음.
칸: 제목 / 로그라인(한 줄) / 첫 3초 훅 / 반전 / 2화 떡밥
```

정한 내용은 내 작품 기획서에 적어 두세요. 칸을 채우면 대본 프롬프트가 자동으로 만들어져요. 첫 편을 예제로 만든다면 이 단계는 예제 기획을 읽는 것으로 충분해요.

### STEP 2 체크리스트

- [ ] 장르와 분위기 정하기
- [ ] 로그라인 한 줄 쓰기
- [ ] 인물 2~3명의 이름·나이·성격 정하기
- [ ] 반전과 마지막 한 줄(다음 화 떡밥) 정하기

이야기 · STEP 03 · 약 60분

## STEP 03 · AI와 함께 60초 대본 쓰기

**끝나면:** 컷 번호·시간·대사가 정리된 60초 대본이 생겨요.

### 대본 규칙 4가지

1.  한 컷에 대사는 한 문장, 20자 안팎. 사람은 1초에 4~5글자쯤 말해서 5초 컷에는 20자가 한계예요.
2.  설명하는 대사 대신 표정과 행동으로 보여 주세요. “나 화났어” 대신 커피잔을 쾅.
3.  첫 컷에는 이야기에서 가장 센 순간을 놓으세요.
4.  컷은 10~12개, 컷 하나는 3~8초.

**대본 요청 프롬프트** · ChatGPT · Gemini · Claude

``` text
너는 조회수 높은 세로형(9:16) AI 숏드라마 작가야. 아래 기획으로 60초 분량의 대본을 써 줘.

[기획]
제목: [작품 제목]
장르·분위기: [장르] / [분위기]
주인공: [이름, 나이, 직업, 성격] (외모·의상: [머리, 얼굴 특징, 옷])
상대역: [이름, 나이, 직업, 성격] (외모·의상: [머리, 얼굴 특징, 옷])
장소: [1~2곳]
시작 상황: [처음 벌어지는 일]
갈등: [주인공이 몰리는 상황]
반전: [숨겨진 진실]
마지막 한 줄(다음 화 떡밥): [다음 화가 궁금해지는 대사나 장면]

[규칙]
1) 첫 3초는 이야기에서 가장 강렬한 장면이나 대사(훅)로 시작
2) 구조: 훅 → 상황 → 갈등 고조 → 반전 → 통쾌한 마무리와 다음 화 떡밥
3) 총 10~12컷, 컷당 3~8초, 합계 60초
4) 대사는 한 컷에 한 문장, 20자 안팎의 자연스러운 구어체
5) 인물 3명 이하, 장소 2곳 이하. 격한 액션·복잡한 손동작 대신 표정·시선·짧은 동작 위주
6) 실존 인물·실제 브랜드·기존 작품 캐릭터는 쓰지 않기

[출력 형식] 마크다운 기호 없이 컷마다 아래처럼 써 줘.
[컷 1] 0:00–0:03 | 샷 크기
화면: 보이는 장면
대사: 인물: "대사" (없으면 없음)
소리: 효과음·음악

마지막에 '2화 예고 한 줄'과 '제목 후보 3개'를 붙여 줘.
```

대괄호 \[ \] 부분을 내 기획으로 바꿔 쓰세요. 내 작품 기획서에 적으면 칸이 채워진 프롬프트가 자동으로 만들어져요.

### 다듬기 프롬프트

**훅을 더 세게**

``` text
첫 컷을 서로 다른 3가지 버전으로 다시 써 줘. 버전마다 무엇이 시선을 잡는지 한 줄로 설명해 줘.
```

**대사를 자연스럽게**

``` text
대사를 실제 사람이 말하듯 더 짧고 자연스럽게 고쳐 줘. 대사 하나는 20자 이내로.
```

**반전을 예상 밖으로**

``` text
시청자가 반전을 쉽게 예상하지 못하도록, 반전 두 컷 앞에 작은 복선을 하나 심어 줘.
```

**시간 맞추기**

``` text
소리 내어 읽어 보니 75초가 나와. 60초에 맞게 컷을 줄여 줘. 뺀 컷은 따로 표시해 줘.
```

**팁:** 대본을 소리 내어 읽으며 스톱워치로 재 보세요. 65초가 넘으면 대사를 빨리 읽기보다 컷을 빼는 편이 나아요.

### STEP 3 체크리스트

- [ ] 대본 프롬프트로 초안 받기
- [ ] 다듬기 프롬프트로 2번 이상 고치기
- [ ] 소리 내어 읽으며 60초(±5초) 맞추기
- [ ] 최종 대본을 01_기획 폴더에 저장하기

이야기 · STEP 04 · 약 40분

## STEP 04 · 콘티와 샷리스트 만들기

**끝나면:** 컷마다 화면 크기·카메라 움직임·대사·길이가 정해진 표가 생겨요.

### 샷 크기 6가지

### 카메라 움직임

| 움직임          | 프롬프트에 쓰는 말       | 이럴 때 써요                  |
|-----------------|--------------------------|-------------------------------|
| 고정            | static camera            | 대사와 표정에 집중할 때       |
| 천천히 다가가기 | slow push-in             | 긴장, 깨달음, 결심            |
| 천천히 물러나기 | slow pull-out            | 고립감, 여운                  |
| 좌우로 훑기     | slow pan left to right   | 공간 소개, 주변 사람들의 반응 |
| 손에 든 카메라  | handheld, slight shake   | 다툼, 혼란, 다급함            |
| 따라가기        | tracking shot            | 걷거나 들어오는 인물          |
| 주위를 돌기     | slow orbit around        | 주인공의 멋진 등장            |
| 급줌            | fast push-in, crash zoom | 반전 순간 (막장 드라마 감성)  |

### 샷리스트는 이런 모양이에요 (예제 앞부분)

| 컷  | 길이 | 샷 크기           | 카메라          | 화면                      | 대사                                        |
|-----|------|-------------------|-----------------|---------------------------|---------------------------------------------|
| 1   | 3초  | 익스트림 클로즈업 | 고정            | 커피잔이 쾅, 커피가 튐    | 오 부장(화면 밖): “이걸 커피라고 준 거야?!” |
| 2   | 5초  | 미디엄 (시점샷)   | 핸드헬드        | 카운터 너머 삿대질        | 오 부장: “연하게 달라고 했잖아! 귀가 없어?” |
| 3   | 4초  | 클로즈업          | 천천히 다가가기 | 서윤이 침착하게 고개 숙임 | 서윤: “죄송합니다. 다시 만들어 드릴게요.”   |
| 4   | 5초  | 바스트샷          | 고정            | 비웃으며 명함을 톡톡      | 오 부장: “됐고, 사장 나오라 그래!”          |

12컷 전체는 예제 패키지의 대본에 있어요.

**대본 → 샷리스트 변환 프롬프트** · ChatGPT · Gemini · Claude

``` text
아래 대본을 AI 영상 제작용 샷리스트로 바꿔 줘.

1) 등장인물마다 '캐릭터 고정 문장'을 영어 한 문장으로 만들어 줘. 나이, 성별, 머리 모양·색, 얼굴 특징, 의상 색, 소품을 넣어.
2) 장소 고정 문장과 스타일 고정 문장도 영어로 하나씩 만들어 줘. 스타일 문장에는 vertical 9:16, no text, no watermark를 넣어.
3) 컷마다 이미지 프롬프트(영어)를 써 줘: 샷 크기 + 캐릭터 고정 문장 + 행동·표정 + 장소 고정 문장 + 스타일 고정 문장. 고정 문장은 글자 하나 바꾸지 말고 그대로 넣어.
4) 컷마다 영상 프롬프트(영어)를 써 줘: 카메라 움직임 + 인물 동작 하나 + 표정 변화 + 배경 움직임. 대사가 있으면 끝에 She says in Korean, calm: "대사" 처럼 한국어 대사를 따옴표로 넣어.
5) 한국어 대사와 효과음도 컷마다 적어 줘.

출력: 맨 위에 고정 문장들, 그 아래 컷마다 '컷 번호 / 길이 / 샷 크기 / 이미지 프롬프트 / 영상 프롬프트 / 대사 / 효과음' 순서로.

[대본]
(여기에 대본을 붙여 넣으세요)
```

**팁:** 같은 크기의 샷이 세 번 넘게 이어지면 지루해져요. 대화는 말하는 사람 클로즈업과 듣는 사람 반응을 번갈아 쓰고, 반전 순간에는 급줌이나 1초 정적을 넣어 보세요.

### STEP 4 체크리스트

- [ ] 컷마다 샷 크기 정하기
- [ ] 컷마다 카메라 움직임 정하기
- [ ] 샷리스트 표 완성하기 (컷·길이·대사)
- [ ] 총 길이가 60초인지 확인하기

## PART 2 · 그림

STEP 5~7 · 얼굴을 고정하고, 장면을 그리고, 움직여요

그림 · STEP 05 · 약 60분

## STEP 05 · 캐릭터 만들기: 얼굴 고정이 생명

**끝나면:** 인물마다 ‘외모 문장(IDENTITY)’과 13칸짜리 캐릭터 시트 1장이 생겨요.

AI 숏드라마에서 가장 흔한 실패는 컷마다 주인공 얼굴이 달라지는 거예요. 영상을 만들기 전에 얼굴과 의상을 고정해 두면 뒤 단계가 훨씬 쉬워져요.

### 외모 문장(IDENTITY) 공식

\[이름, 나이\] + \[분위기: the visual of a top-tier Korean film actress\] + \[얼굴형\] + \[눈: 쌍꺼풀·눈꼬리\] + \[코·입술\] + \[얼굴 지문: 점·흉터·주근깨\] + \[머리\] + \[체형·키\]

‘잘생긴’, ‘예쁜’ 같은 추상적인 말만 쓰면 AI가 가장 흔한 아이돌 얼굴을 만들어서 인물끼리 닮고, Flow의 유명인 차단에도 잘 걸려요. 눈꼬리 방향, 쌍꺼풀 모양, 점이나 흉터 같은 **눈에 보이는 특징**을 넣으면 얼굴이 고정되고 차단도 줄어요. 실존 연예인 이름은 절대 넣지 마세요.

### 13칸 캐릭터 시트 만들기

1.  Flow(또는 Gemini)에서 이미지 모델을 **나노바나나 Pro**로, 비율을 **16:9 가로**로 정해요. 칸이 많아서 가로가 좋아요.
2.  아래 프롬프트의 대괄호를 내 인물로 바꿔 넣어요. 한 장에 **한 사람**만 넣으세요. 두 사람을 한 장에 넣으면 칸이 작아지고 얼굴이 섞여요.
3.  13칸이 다 나오지 않으면 맨 앞에 Exactly 13 panels.를 붙여 다시 뽑아요. 이미지는 AI Pro 구독이면 0크레딧이라 여러 장 뽑아 고르세요.
4.  02_캐릭터 폴더에 ‘서윤_시트.png’처럼 저장해요. 장면 이미지를 만들 때 이 시트를 첨부하고, IDENTITY와 의상 문장도 그대로 함께 넣어요.

**13칸 캐릭터 시트 프롬프트** · Flow·Gemini 이미지 · 나노바나나 Pro · 16:9

``` text
Photorealistic character reference sheet of ONE fictional original Korean [woman/man] who does not resemble any real person. Landscape 16:9, clean light-gray studio background, 13 panels separated by thin white lines, nothing overlapping or cropped.

IDENTITY: [이름], [나이], the visual of a top-tier Korean film [actress/actor]: [얼굴형], [피부], [눈 모양·쌍꺼풀·눈꼬리], [코], [입술], [점·흉터·주근깨 같은 고유 표시], [머리 모양·색], [체형, 키].

WARDROBE (same in every full-body panel): [상의], [하의], [신발], [시계·안경 같은 소품].

LAYOUT:
Left: 1 large chest-up front portrait.
Center top row: head-and-shoulders front, 45-degree three-quarter, 90-degree side profile.
Center bottom row: [대본에 나오는 표정 3개].
Center right: full body front, side, back.
Right column: close-ups of eyes, nose, lips, hair.

CONSISTENCY: exactly the same person in all 13 panels; same bone structure, eye shape, eyelids, nose, lips, distinguishing marks, hairline, haircut, skin tone, age and proportions. Expressions change only through natural muscle movement.

QUALITY: ultra-photorealistic live-action portrait photography, even soft studio lighting, realistic skin microtexture, individual hair strands, natural eye reflections, realistic fabric. Attractive but believable, natural eye size, natural proportions.

AVOID: identity drift, extra people, distorted hands, plastic skin, text, watermark.
```

| 위치          | 칸                             | 쓰는 곳              |
|---------------|--------------------------------|----------------------|
| 왼쪽          | 큰 정면 초상 1칸               | 대표 얼굴 확인       |
| 가운데 윗줄   | 정면 · 3/4 · 옆얼굴            | 클로즈업 컷 레퍼런스 |
| 가운데 아랫줄 | 대본 속 표정 3개               | 감정 연기 컷         |
| 가운데 오른쪽 | 전신 앞 · 옆 · 뒤              | 걷기·등장·뒷모습 컷  |
| 오른쪽        | 눈 · 코 · 입술 · 머리 클로즈업 | 디테일 확인          |

영어가 부담스러우면 한국어로 써도 돼요. Gemini는 한국어 이미지 요청도 잘 알아들어요. 다만 같은 인물은 끝까지 같은 문장을 쓰는 게 핵심이에요.

내 방식별 이미지 도구

- **무료** · Gemini 무료: 나노바나나로 생성하고 대화로 고쳐요. 하루 생성 한도가 적어요.
- **가성비** · Google AI Plus: 나노바나나 Pro를 더 넉넉하게 써요. 인물 일관성이 좋아요.
- **본격** · Google AI Pro: 나노바나나 Pro 한도가 더 많아요. 컷마다 여러 버전을 뽑아 고르세요.

### 얼굴을 지키는 습관 6가지

- 고정 문장은 글자 하나 바꾸지 말고 매번 복사해서 붙여 넣기
- 의상은 단순하게, 색은 정확하게 (베이지 앞치마, 회색 정장)
- 캐릭터 시트를 매번 첨부하기
- 한 인물은 한 대화창에서 이어서 작업하기
- 이상한 결과는 고치려 애쓰지 말고 버리고 다시 만들기
- 연예인 이름이나 지인 사진은 넣지 않기 (영상 생성이 막혀요)

### STEP 5 체크리스트

- [ ] 인물별 외모 문장(IDENTITY)과 의상 문장 쓰기
- [ ] 인물별 13칸 캐릭터 시트 만들기
- [ ] 장소마다 레퍼런스 1장씩 만들기
- [ ] 02_캐릭터 폴더에 이름 붙여 저장하기

그림 · STEP 06 · 약 90분

## STEP 06 · 장면 이미지(키프레임) 만들기

**끝나면:** 컷마다 영상의 첫 화면이 될 9:16 이미지가 1장씩 생겨요.

글만 넣어 바로 영상을 만드는 것보다, 먼저 이미지를 만들고 그 이미지를 움직이는 쪽이 얼굴과 구도를 훨씬 잘 지켜요. 이 이미지를 키프레임이라고 불러요.

### 이미지 프롬프트 공식

\[샷 크기\] + \[캐릭터 고정 문장\] + \[행동·표정\] + \[장소\] + \[조명·시간\] + \[스타일\] + vertical 9:16, no text

### 작업 순서

1.  그 컷에 나오는 인물의 캐릭터 시트를 첨부해요. 두 명이 나오면 두 명 다.
2.  컷의 이미지 프롬프트를 붙여 넣어요.
3.  가장 좋은 결과를 고르고 “표정을 더 화나게”, “카메라를 조금 더 가까이”처럼 대화로 고쳐요.
4.  03_장면 폴더에 ‘컷01.png’처럼 번호로 저장해요.

### 시트를 첨부할 때의 짧은 이미지 프롬프트

캐릭터 시트를 첨부하면 긴 외모 문장을 다 쓰지 않아도 돼요. **얼굴 지문(점·흉터·안경·머리)과 의상**만 괄호로 짚어 주세요. 얼굴이 달라지면 그때 긴 IDENTITY 문장을 앞에 더해요. 두 사람이 나오면 시트를 둘 다 첨부하고 sheets로 바꿔요.

**Flow 키프레임 프롬프트** · 나노바나나 Pro · 9:16 · 시트 첨부

``` text
Use the attached character sheet for identity. Vertical 9:16 [샷 크기] of [이름] (the woman/man from the attached sheet: [얼굴 지문], [의상]), [행동·표정]. Setting: [장소]. Cinematic Korean drama film still, photorealistic, [색감·조명], shallow depth of field. Screens and papers are blank. No text, no watermark.
```

### 좋은 키프레임의 조건

- 동작이 시작되기 직전의 자세 (손을 들기 직전, 고개를 숙이기 직전)
- 손은 단순하게, 가능하면 화면 밖에
- 배경이 깔끔하고 인물이 화면 가운데 근처에
- 얼굴이 캐릭터 시트와 같은 사람으로 보일 것
- 태블릿 화면, 서류, 간판처럼 **글자가 필요한 곳은 비워 두기**. AI는 한글을 뭉개서 그려요. 글자는 편집에서 자막으로 얹어요.

내 방식별 이미지 도구

- **무료** · Gemini 무료. 하루 한도가 적으니 컷 3~4개씩 나눠서 만드세요.
- **가성비** · Google AI Plus의 나노바나나 Pro로 12컷을 하루에 끝낼 수 있어요.
- **본격** · Google AI Pro. 컷마다 2~4개 버전을 뽑아 가장 좋은 것을 고르세요.

**예제:** 「알바생의 정체」 12컷의 이미지 프롬프트는 예제 패키지 › 컷별 프롬프트에 모두 있어요.

### STEP 6 체크리스트

- [ ] 공식대로 첫 컷 이미지 만들기
- [ ] 나머지 컷 이미지 완성하기
- [ ] 모든 컷을 나란히 놓고 얼굴·의상·조명 비교하기
- [ ] 혼자 튀는 컷 다시 만들기

그림 · STEP 07 · 2~3시간

## STEP 07 · 이미지를 영상으로 움직이기

**끝나면:** 컷마다 3~10초짜리 영상 클립이 생겨요.

### 어떤 도구를 쓸까

| 도구                                         | 잘하는 것                                                                                                                                                                   | 알아 둘 점                                                                                                                |
|----------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| **Kling 4.0** (Kling AI)                     | 한 번에 최대 30초. 키프레임 10장, 참고 자료 15개. 한국어를 포함한 여러 언어의 립싱크 지원을 발표했어요.                                                                     | 무료는 하루 크레딧, 워터마크, 비상업. 초기 체험판은 720p였어요.                                                           |
| **Google Flow** (Veo 3.1, Gemini Omni Flash) | 사실적인 화질과 주변 소리. Veo 3.1 Lite는 4·6·8초 모두 10크레딧(720p, 1080p 업스케일 가능)이라 **8초로 만들면 1초당 비용이 가장 낮아요**. AI Pro 구독이면 이미지는 0크레딧. | 비구독자는 하루 50크레딧. 한국어 대사는 고르지 않아 TTS로 따로 넣는 게 안전해요. 얼굴이 실존 인물과 닮으면 생성이 막혀요. |
| **Hailuo** (MiniMax H3)                      | 감정 연기, 인물 레퍼런스 최대 9장, 5~15초.                                                                                                                                  | 2026년 7월 출시라 사용 후기가 아직 적어요.                                                                                |
| **Dreamina** (Seedance 2.0)                  | 참고 자료를 활용한 멀티샷, 최대 15초.                                                                                                                                       | 실제 사람 얼굴이 담긴 이미지는 쓸 수 없어요. 지역별로 순차 제공 중이에요.                                                 |

### Google Flow로 따라 하기 (AI Pro 구독이라면 추천)

1.  labs.google/flow에서 프로젝트를 열고, 이미지 모델 나노바나나 Pro · 비율 9:16으로 키프레임을 만들어요. (AI Pro는 0크레딧)
2.  ‘프레임으로 동영상 만들기(Frames to Video)’를 고르고, 키프레임을 시작 프레임으로 넣어요.
3.  모델 Veo 3.1 Lite · 8초 · 한 번에 1개로 설정해요. (10크레딧)
4.  영상 프롬프트를 넣어요. 대사가 있으면 STEP 8의 ‘C안’처럼 목소리와 입 모양까지 한 번에 만들어요.
5.  마음에 드는 결과만 1080p로 업스케일하고, ‘컷01.mp4’처럼 번호로 저장해요.

### Kling으로 따라 하기

1.  Kling AI에 로그인해 오늘 받은 크레딧을 확인해요.
2.  영상 만들기에서 ‘이미지로 영상 만들기(Image to Video)’를 골라요.
3.  03_장면 폴더의 ‘컷01.png’를 올리고 비율이 9:16인지 확인해요.
4.  모델과 길이를 골라요. 첫 테스트는 5초로, 무료라면 크레딧이 적게 드는 모델로 해요.
5.  컷의 영상 프롬프트를 붙여 넣어요. 대사를 넣을지는 STEP 8의 A안·B안을 보고 정해요.
6.  생성한 뒤 결과를 비교해 가장 자연스러운 것을 04_영상 폴더에 ‘컷01_v1.mp4’로 저장해요.

메뉴 이름은 업데이트에 따라 조금씩 달라질 수 있어요.

### 모션 프롬프트 공식

One continuous shot, no cuts + \[카메라 움직임\] + \[인물 동작 하나\] + \[표정 변화\] + \[그 뒤엔 정지\] + (대사) + No text

**예: 컷 3 영상 프롬프트** · Kling · 이미지로 영상 만들기

``` text
One continuous shot, no cuts, no scene change, same framing throughout. Slow push-in. She looks startled for a moment, blinks, regains her composure and gives a small polite nod. Her hands stay still at her sides. Calm café ambience. No text, no subtitles.
```

- 한 컷에는 동작 하나만
- slowly, subtle 같은 말로 움직임을 작게
- 처음에는 5초로 만들고 편집에서 자르기
- 카메라와 인물을 동시에 크게 움직이지 않기
- 맨 앞에 One continuous shot, no cuts: 남는 시간에 AI가 장면을 바꾸거나 새 동작을 지어내는 걸 막아요
- 끝에 No text, no subtitles: 화면 구석에 엉뚱한 글자가 생기는 걸 막아요

**실제 테스트에서 배운 것:** 8초 클립에서 쓸 만한 건 보통 3~5초예요. 앞뒤에서 손이 하나 더 생기거나, 장면이 바뀌거나, 글자가 나타나는 일이 많아요. 실패라고 생각하지 말고 가장 좋은 3~5초만 잘라 쓰는 게 기본이에요.

### 8초를 통째로 쓰는 방법

길이가 꼭 60초일 필요는 없어요. **12컷 × 8초(약 1분 36초)**로 구성하면 클립을 자르지 않고 그대로 이어 붙일 수 있어요. 대신 AI가 남는 시간을 엉뚱하게 채우지 않도록 8초를 두 박자로 나눠 지시하세요.

**8초 두 박자 모션 프롬프트** · Veo 3.1 Lite · 8초

``` text
One continuous 8-second shot, no cuts, same framing throughout. Seconds 0-4: [동작 하나]. Seconds 4-8: [표정 변화나 반응], then holds still. [대사]. No text, no subtitles.
```

대사도 8초면 30자 안팎까지 넣을 수 있어요. 내 작품 기획서의 길이를 ‘96초’로 고르면 대본 프롬프트가 이 구성으로 바뀌어요.

### 크레딧 아끼는 법

- 이미지 단계에서 충분히 고르고, 영상은 확정된 컷만 만들기
- Flow라면 Veo 3.1 Lite를 8초로: 길이와 상관없이 10크레딧이라 1초당 비용이 가장 낮고, 720p라 그대로 본편에 써요. 사용법만 익힐 땐 Omni Flash 360p 4초(5크레딧)도 좋아요
- 확정 컷만 1080p로 업스케일하기
- 무료 크레딧은 이월되지 않으니 매일 조금씩 쓰기
- 한 번에 여러 개를 생성하는 옵션은 꺼 두기

내 방식별 영상 도구

- **무료** · Kling 무료 일일 크레딧(크레딧이 적게 드는 모델) + Google Flow 비구독자 하루 50크레딧. 워터마크가 붙고 상업적으로 쓸 수 없어요.
- **가성비** · Kling Standard 660크레딧으로 확정 컷을 만들고, 시안은 Flow(AI Plus 크레딧)로 만들어요.
- **본격** · Kling Pro 3,000크레딧으로 Kling 4.0을 넉넉히, Flow에서 Veo 3.1 Quality와 Gemini Omni Flash까지 써요.

**다음 단계:** 익숙해지면 Kling 4.0의 다중 키프레임(최대 10장)으로 여러 컷을 한 번에 최대 30초까지 이어 만들 수 있어요. 첫 편은 컷별로 만드는 쪽이 실패가 적어요.

### STEP 7 체크리스트

- [ ] 첫 컷으로 테스트하며 설정 익히기
- [ ] 모든 컷 영상 만들기 (컷당 1~3회)
- [ ] 컷별로 가장 좋은 클립을 04_영상 폴더에 저장하기
- [ ] 얼굴이 변하거나 손이 깨진 컷 다시 만들기

## PART 3 · 소리

STEP 8~9 · 목소리와 음악으로 감정을 완성해요

소리 · STEP 08 · 약 60분

## STEP 08 · 목소리 입히기

**끝나면:** 모든 대사가 인물마다 일관된 목소리로 들어가요.

### 두 가지 방법

|          | A안: 영상과 함께 대사 생성                                                                     | B안: AI 음성(TTS)으로 따로                                              |
|----------|------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| **방법** | 모션 프롬프트 끝에 She says in Korean: "대사"를 넣어, 영상을 만들 때 목소리까지 같이 생성해요. | Typecast·ElevenLabs·클로바더빙에서 대사 파일을 만들어 편집할 때 붙여요. |
| **장점** | 입 모양이 자동으로 맞고 가장 간단해요.                                                         | 인물 목소리가 끝까지 같아요. 감정과 속도를 세밀하게 조절해요.           |
| **단점** | 컷마다 목소리가 조금씩 달라질 수 있어요. 한국어 발음은 도구마다 차이가 있어요.                 | 입 모양을 따로 맞춰야 해요 (립싱크 기능이나 입이 안 보이는 컷).         |
| **추천** | 첫 편, 무료·가성비                                                                             | 시리즈, 본격 연재                                                       |

먼저 A안으로 해 보고, 목소리가 거슬리는 인물만 B안으로 바꾸는 게 가장 효율적이에요. 같은 인물의 목소리 묘사(예: deep, arrogant male voice in his late 40s)를 모든 컷에 똑같이 넣으면 A안도 꽤 일정해져요.

### C안: Flow(Veo)에서 목소리와 입 모양을 한 번에

Veo는 영상을 만들면서 목소리, 입 모양, 효과음까지 함께 만들어요. 따로 녹음하거나 립싱크할 필요가 없어서 가장 간단해요. 대신 컷마다 목소리를 새로 만들기 때문에, **인물별 목소리 묘사를 고정**해서 매번 똑같이 넣어야 해요.

| 규칙                  | 프롬프트에 쓰는 말                                                                        |
|-----------------------|-------------------------------------------------------------------------------------------|
| 인물별 목소리 고정    | in a calm, clear, low-pitched Korean female voice in her late 20s, restrained and precise |
| 누가, 언제 말하는지   | Seconds 4-8: she speaks with clear lip movement, ... saying in Korean: "대사"             |
| 말하기 전엔 입을 닫게 | lips closed                                                                               |
| 두 명이 나올 때       | Only he speaks. / Only she speaks.                                                        |
| 화면 밖 목소리        | Her lips stay closed. Off-screen, \[목소리 묘사\], says in Korean: "대사"                 |
| 음악은 편집에서       | Audio: \[효과음\], her voice, no background music. No text, no subtitles.                 |

**C안 영상 프롬프트 공식** · Flow · Veo 3.1 Lite · 8초

``` text
One continuous 8-second shot, no cuts, same framing throughout. Seconds 0-4: [동작], lips closed. Seconds 4-8: [표정 변화] and [he/she] speaks with clear lip movement, in [인물 목소리 묘사], saying in Korean: "[대사]" Only [he/she] speaks. Audio: [효과음], [his/her] voice, no background music. No text, no subtitles.
```

- **발음이 뭉개지면** 한두 번 더 뽑고, 그래도 안 되면 대사를 한 문장으로 줄이세요.
- **입 모양이 안 맞으면** 대사 앞에 facing the camera를 넣어 얼굴이 정면을 보게 하세요.
- **컷마다 목소리가 조금씩 달라요.** 완전히 같게 하려면 그 인물만 B안(TTS)으로 바꾸세요.

### Typecast로 대사 만들기 (B안)

1.  typecast.ai에서 새 프로젝트를 만들어요.
2.  인물에 맞는 목소리(캐릭터)를 골라요.
3.  대사를 한 줄씩 붙여 넣고 감정과 속도를 정해요.
4.  미리 들어 보고, 어색한 곳은 쉼표나 말줄임표로 호흡을 바꿔요.
5.  05_음성 폴더에 ‘컷03_서윤.wav’처럼 컷 번호로 내려받아요.

### 발음이 자연스러워지는 팁

- 숫자와 영어는 한글로 풀어 쓰기 (10분 → 십 분, CEO → 대표)
- 쉼표와 말줄임표로 호흡 넣기
- 긴 문장은 두 개로 끊기
- 같은 인물은 끝까지 같은 목소리, 같은 설정

### 입 모양 맞추기

- 영상 도구의 립싱크 기능(Kling 등)에 영상과 음성 파일을 함께 넣기
- 입이 잘 안 보이는 컷(옆모습, 뒷모습, 듣는 사람의 반응)에 대사 깔기
- 대사 길이를 컷 길이에 맞추기

내 방식별 음성 도구

- **무료** · A안(Kling 영상 속 대사) 위주로 하고, Typecast 무료 범위에서 몇 줄만 보충해요.
- **가성비** · A안을 기본으로, 목소리가 거슬리는 인물만 Typecast로 바꿔요.
- **본격** · AI Pro라면 C안(Flow에서 목소리·입 모양 한 번에)부터 해 보고, 목소리를 완전히 통일해야 하는 인물만 B안(Typecast·ElevenLabs 유료)으로 바꿔요.

### STEP 8 체크리스트

- [ ] A안·B안·C안(Flow 한 번에) 중 정하기
- [ ] 인물별 목소리 정하기
- [ ] 대사 파일 만들기 (컷 번호로 저장)
- [ ] 입 모양을 맞추거나 컷 배치 조정하기

소리 · STEP 09 · 약 40분

## STEP 09 · 음악과 효과음

**끝나면:** 배경음악 1곡과 효과음 5개 이상이 준비돼요.

| 구하는 곳                 | 특징                                        | 쓸 때 주의                                                                                           |
|---------------------------|---------------------------------------------|------------------------------------------------------------------------------------------------------|
| **YouTube 오디오 보관함** | YouTube 스튜디오 안에 있는 무료 음악·효과음 | 수익화 영상에도 쓸 수 있어요. 일부 곡은 출처 표기가 필요해요.                                        |
| **Suno**                  | 원하는 분위기를 글로 써서 음악 생성         | 무료 플랜 곡은 개인·비상업용이에요. 상업적으로 쓰려면 Pro(월 \$10부터) 구독 중에 만든 곡이어야 해요. |
| **CapCut 음악·효과음**    | 편집하면서 바로 넣기                        | 상업적 이용 가능 표시가 있는 것만 쓰세요.                                                            |

**Suno 프롬프트 (예제용)** · Suno · Instrumental 켜기

``` text
Instrumental only. Tense K-drama underscore: pizzicato strings, low cello pulses and a soft ticking clock, slowly building suspense, a sudden stop, then a powerful reveal theme with taiko drums and rising strings, cinematic, cold and confident ending.
```

### 예제에 필요한 효과음

- 도자기 컵 ‘쾅’
- 손가락으로 카운터 ‘톡톡’
- 카페 웅성거림
- 출입문 종소리 ‘딸랑’
- 구두 발소리
- 반전 임팩트 ‘두둥’

### 소리 크기 규칙

- 대사, 효과음, 음악 순서로 크게
- 대사가 나오는 동안은 음악을 한 단계 더 낮추기
- 반전 직전 1초 정적이 ‘두둥’보다 셀 때가 있어요
- 이어폰과 스마트폰 스피커 둘 다로 들어 보기

내 방식별 음악 도구

- **무료** · YouTube 오디오 보관함 음악 + CapCut 기본 효과음
- **가성비** · 위와 같아요. Suno 무료로 분위기를 연습해 볼 수 있지만, 공개 영상에는 오디오 보관함 음악을 쓰세요.
- **본격** · Suno Pro로 작품 전용 테마곡을 만들어 시리즈 내내 써요.

### STEP 9 체크리스트

- [ ] 배경음악 고르기 (라이선스 확인)
- [ ] 효과음 5개 이상 모으기
- [ ] 06_사운드 폴더에 저장하기

## PART 4 · 완성·공개

STEP 10~12 · 편집하고, 올리고, 키워요

완성·공개 · STEP 10 · 약 2시간

## STEP 10 · 편집하고 자막 넣기

**끝나면:** 1080×1920 크기의 60초 완성본이 생겨요.

### CapCut으로 따라 하기

1.  새 프로젝트를 만들고 04_영상의 클립을 컷 순서대로 불러와요. 비율은 9:16.
2.  클립마다 앞뒤를 다듬어요. AI 영상은 시작 0.2~0.5초와 끝부분이 어색할 때가 많아요.
3.  B안이라면 대사 파일을 해당 컷 아래에 놓아요. A안이면 영상 속 대사를 그대로 써요.
4.  배경음악을 깔고, 대사가 나오는 구간은 볼륨을 낮춰요.
5.  효과음을 타임라인처럼 배치해요. (쾅, 웅성, 딸랑, 두둥)
6.  자막을 넣어요. 자동 자막이 유료로 막혀 있으면 Vrew를 쓰세요.
7.  첫 3초 위쪽에 훅 문구를, 마지막 컷에 ‘2화에서 계속’을 넣어요.
8.  필터 하나를 전체 클립에 약하게 걸어 색감을 맞춰요.
9.  1080×1920, 30fps로 내보내요. AI 클립이 24fps라면 24fps도 괜찮아요.

### 자막 스타일

- 굵은 고딕, 흰 글자에 검은 테두리나 반투명 상자
- 한 줄 14자 안팎, 최대 두 줄
- 화면 가운데에서 아래 1/3 사이
- 맨 아래 20%와 오른쪽 끝은 앱의 버튼과 제목이 가려요
- 훅 문구는 위쪽에, 첫 3초 동안

**Vrew 자막:** 완성본을 Vrew로 불러와 언어를 한국어로 정하고 자동 자막을 만든 뒤, 오타를 고치고 스타일을 정해 내보내면 돼요.

### 내보내기 전 최종 점검

- 소리를 꺼도 이야기가 이해되나요?
- 첫 1초에 손가락이 멈출 만한가요?
- 길이가 60초 안팎인가요?
- 자막 오타와 타이밍이 맞나요?
- 얼굴이 튀는 컷은 없나요?
- 대사가 음악에 묻히지 않나요?

내 방식별 편집 도구

- **무료** · CapCut 기본 편집 + Vrew 무료 범위 자동 자막
- **가성비** · 위와 같아요. 자막 작업이 많아지면 Vrew 유료를 검토하세요.
- **본격** · CapCut 유료(자동 자막, AI 보정) 또는 Vrew 유료

### STEP 10 체크리스트

- [ ] 클립 배치하고 다듬기
- [ ] 대사·음악·효과음 배치하기
- [ ] 자막과 훅 문구 넣기
- [ ] 1080×1920으로 내보내기

완성·공개 · STEP 11 · 약 30분

## STEP 11 · 제목·커버·AI 표시

**끝나면:** 업로드에 필요한 제목, 설명, 해시태그, 커버, AI 표시가 준비돼요.

### 제목 공식 5가지

| 공식        | 예시                               |
|-------------|------------------------------------|
| 정체 공개형 | 카페 알바생의 정체                 |
| 결과 궁금형 | 알바생에게 갑질한 부장의 최후      |
| 조건형      | 사장 나오라고 소리쳤더니 벌어진 일 |
| 대사 인용형 | “대표님, 이사회 십 분 전입니다”    |
| 시리즈형    | \[알바생의 정체 1화\] 진상 손님    |

**설명란 템플릿** · YouTube · Instagram · TikTok

``` text
진상 손님에게 갑질을 당한 카페 알바생, 그녀의 진짜 정체는?
2화는 [요일]에 공개돼요.
이 영상은 AI 도구로 제작한 창작 드라마이며 등장인물과 단체는 모두 허구입니다.
#AI드라마 #숏드라마 #사이다 #반전 #shorts
```

### 커버(썸네일)

쇼츠는 영상 속 한 장면을 커버로 골라요. 표정이 가장 센 컷이 좋아요. 예제라면 10번, 얼어붙은 부장의 얼굴이에요. 릴스는 커버 이미지를 따로 올릴 수 있고, 프로필 격자에서는 위아래가 잘려 보이니 얼굴을 가운데에 두세요.

### AI로 만든 영상이라고 표시하기

- **YouTube:** 업로드 화면 ‘세부정보’의 ‘변경되거나 합성된 콘텐츠’ 항목에서 ‘예’를 골라요. 실제처럼 보이는 인물이나 장면이면 꼭 표시해야 해요.
- **Instagram:** 게시 전 ‘고급 설정’에서 AI 레이블을 켜요. 앱 버전에 따라 이름이 조금 달라요.
- **TikTok:** 게시 화면의 추가 옵션에서 ‘AI 생성 콘텐츠’를 켜요.
- **설명란:** 마지막 줄에 AI로 만든 창작물이라고 적어요.

**걱정 마세요:** AI 표시를 했다고 해서 수익 창출이 막히지는 않아요. 문제가 되는 건 표시를 하지 않아 시청자를 속이는 경우예요.

**제목·설명·해시태그 프롬프트** · ChatGPT · Gemini · Claude

``` text
아래 숏드라마 대본으로 업로드 정보를 만들어 줘.
1) 유튜브 쇼츠 제목 5개: 30자 이내, 궁금증을 남기되 내용과 다른 낚시는 금지
2) 설명란 3줄: 마지막 줄은 "이 영상은 AI 도구로 제작한 창작 드라마이며 등장인물과 단체는 모두 허구입니다."
3) 해시태그 5개: #AI드라마 #숏드라마 포함
4) 고정 댓글 1개: 다음 화를 기다리게 만드는 질문

[대본]
(여기에 대본을 붙여 넣으세요)
```

### STEP 11 체크리스트

- [ ] 제목 후보 5개 중 하나 고르기
- [ ] 설명란과 해시태그 쓰기
- [ ] 커버로 쓸 장면 고르기
- [ ] 플랫폼별 AI 표시 설정 확인하기

완성·공개 · STEP 12 · 30분 + 꾸준히

## STEP 12 · 올리고, 숫자 보고, 시리즈로 키우기

**끝나면:** 첫 작품이 공개되고, 48시간 데이터로 2화 계획이 생겨요.

### 업로드 순서

1.  **YouTube 쇼츠:** YouTube 앱의 ‘+’에서 동영상을 올려요. 세로 영상이 3분 이하면 쇼츠로 분류돼요.
2.  **릴스·틱톡:** 같은 원본 파일로 올려요. 다른 앱의 워터마크가 찍힌 파일은 쓰지 마세요.
3.  **고정 댓글:** 다음 화 질문을 남겨요. 예: “2화에서 부장님은 어떻게 될까요? 댓글로 예상해 주세요!”

### 48시간 뒤에 볼 숫자 3개

| 숫자                          | 어디서 보나                              | 낮으면 이렇게                                                         |
|-------------------------------|------------------------------------------|-----------------------------------------------------------------------|
| **‘시청함 vs 스와이프’ 비율** | YouTube 스튜디오 › 분석 › 쇼츠 피드 지표 | 첫 1초를 바꾸세요. 가장 센 장면을 맨 앞으로 옮기고 훅 문구를 더 짧게. |
| **시청 지속 그래프**          | 콘텐츠별 분석 › 시청 지속시간            | 그래프가 뚝 떨어지는 지점의 컷을 줄이거나 빼세요.                     |
| **댓글·공유·구독**            | 참여도                                   | 마지막 한 줄과 고정 댓글 질문을 바꿔 보세요.                          |

### 시리즈로 키우기

- 캐릭터 고정 문장과 레퍼런스를 계속 재사용하기
- 제목에 \[작품명 N화\]를 붙이고 재생목록 만들기
- 주 2~3편, 같은 요일 같은 시간에 올리기
- 편마다 새로운 갈등을 넣기. 틀만 바꾼 대량 복제는 YouTube가 ‘진정성 없는 콘텐츠’로 보고 수익 창출을 막아요.
- 최소 10편은 올려 보고 판단하기

### STEP 12 체크리스트

- [ ] 첫 작품 업로드하기
- [ ] 48시간 뒤 숫자 3개 기록하기
- [ ] 고칠 점 하나 정하기
- [ ] 2화 로그라인 쓰기

실습 · 첫 편은 이대로 따라 만들기

## 예제 패키지 「알바생의 정체」

60초, 12컷, 인물 3명, 장소 1곳. 첫 편은 이 패키지를 그대로 따라 만들어 보세요. 모든 프롬프트는 복사해서 바로 쓸 수 있어요. 등장하는 인물과 회사는 모두 지어낸 것이에요.

- **로그라인**: 카페 알바생 서윤이 진상 손님에게 갑질을 당하는데, 사실 그녀는 그 손님의 회사를 인수하는 그룹의 대표였다.
- **장르**: 신분 반전 · 사이다
- **인물**: 한서윤(26, 알바생이자 그룹 대표) · 오정훈 부장(48, 대한물산) · 강민재 비서(32)
- **장소**: 서울 오피스 빌딩 1층 카페, 낮

### 예제 · 대본

| 컷  | 시간      | 샷                 | 화면                                                                     | 대사                                                                     | 소리                         |
|-----|-----------|--------------------|--------------------------------------------------------------------------|--------------------------------------------------------------------------|------------------------------|
| 1   | 0:00–0:03 | 익스트림 클로즈업  | 카운터에 커피잔이 쾅 내려놓이며 커피가 튄다.                             | 오 부장(화면 밖): “이걸 커피라고 준 거야?!”                              | 쾅 · 훅 문구 등장            |
| 2   | 0:03–0:08 | 미디엄 (서윤 시점) | 오 부장이 카운터 너머로 몸을 숙이며 삿대질한다.                          | 오 부장: “연하게 달라고 했잖아! 귀가 없어?”                              | 긴장 음악 시작               |
| 3   | 0:08–0:12 | 클로즈업           | 서윤이 잠깐 놀라지만 침착하게 고개를 숙인다.                             | 서윤: “죄송합니다. 다시 만들어 드릴게요.”                                | —                            |
| 4   | 0:12–0:17 | 바스트샷           | 오 부장이 비웃으며 카운터 위 명함을 손가락으로 두드린다.                 | 오 부장: “됐고, 사장 나오라 그래!”                                       | 톡톡                         |
| 5   | 0:17–0:21 | 와이드             | 카페 손님들이 고개를 돌려 쳐다보며 수군거린다.                           | (없음)                                                                   | 웅성웅성                     |
| 6   | 0:21–0:26 | 클로즈업           | 서윤이 명함을 내려다보다 천천히 고개를 들며 옅게 웃는다.                 | 서윤: “대한물산… 오정훈 부장님?”                                         | —                            |
| 7   | 0:26–0:30 | 미디엄             | 오 부장이 팔짱을 끼고 턱을 치켜든다.                                     | 오 부장: “그래! 알바 주제에… 당장 사장 불러!”                            | 긴장 음악 최고조             |
| 8   | 0:30–0:35 | 풀샷               | 유리문이 열리고 검은 정장의 강 비서가 빠르게 걸어 들어온다.              | (없음)                                                                   | 음악 끊김 · 딸랑 · 구두 소리 |
| 9   | 0:35–0:40 | 미디엄 투샷        | 강 비서가 서윤 앞에서 정중히 고개를 숙인다.                              | 강 비서: “대표님, 이사회 십 분 전입니다.”                                | 반전 테마 시작               |
| 10  | 0:40–0:45 | 클로즈업           | 오 부장의 얼굴이 얼어붙고 입이 벌어진다.                                 | 오 부장: “대… 대표님?”                                                   | 두둥                         |
| 11  | 0:45–0:53 | 바스트샷           | 서윤이 앞치마를 벗어 내려놓고, 오 부장을 똑바로 보며 차갑게 웃는다.      | 서윤: “오늘 저희가 인수하는 회사… 대한물산이죠? 곧 또 뵙겠네요, 부장님.” | —                            |
| 12  | 0:53–1:00 | 와이드             | 얼어붙은 오 부장 뒤로 서윤과 강 비서가 카페를 나간다. 화면이 어두워진다. | (없음)                                                                   | 딸랑 · 엔딩 · “2화에서 계속” |

**2화 예고:** 인수 계약식 날, 회의실 상석에 앉은 사람은…

대사 길이를 컷 길이에 맞춰 두었어요. 1초에 4~5글자 기준이에요.

### 예제 · 캐릭터·장소

아래 다섯 문장이 이 작품의 ‘고정 문장’이에요. 인물 문장은 외모(IDENTITY)와 의상을 합친 거예요. 컷별 프롬프트에는 이 문장들이 이미 들어가 있어요.

**고정 문장 · 한서윤** · 주인공

``` text
Seoyun, 26, the visual of a top-tier Korean film actress: small oval face with a softly defined jaw, clear luminous skin with natural pores, almond-shaped dark brown eyes with subtle inner double eyelids and slightly lifted outer corners, a high slim nose with a rounded tip, naturally full coral lips, a small beauty mark under her right eye, a glossy straight black bob just above the shoulders, slender build, wearing white button-up shirt with rolled sleeves, beige linen barista apron with a small name tag, black slacks, white sneakers, small silver stud earrings
```

**고정 문장 · 오정훈 부장** · 상대역

``` text
Mr. Oh, 48, the visual of a seasoned Korean character actor: round face with full cheeks, thick dark eyebrows, small hooded eyes, a small mole on his left cheek, a broad nose, short side-parted black hair graying at the temples, thin gold-rimmed glasses, slightly heavy build, wearing charcoal gray suit, navy tie, gold wristwatch, black leather shoes
```

**고정 문장 · 강민재 비서** · 조연

``` text
Kang, 32, the sleek visual of a top-tier Korean actor: long narrow face with a sharp jawline, calm monolid eyes, a straight high nose, thin lips, a small scar above his right eyebrow, neatly slicked-back black hair, slim tall build, wearing black suit, white shirt, black tie, black leather shoes, holding a black leather folder
```

**고정 문장 · 장소**

``` text
a modern minimalist café in a Seoul office building, light oak counter, black espresso machine, large windows, warm pendant lights
```

**고정 문장 · 스타일** · 모든 이미지 끝에

``` text
cinematic Korean drama still, photorealistic, soft warm window light, shallow depth of field, vertical 9:16, no text, no watermark
```

### 13칸 캐릭터 시트 (인물마다 1장)

나노바나나 Pro, 16:9 가로로 한 사람씩 만들어요. 장면 이미지를 만들 때 이 시트를 첨부해요.

**한서윤 캐릭터 시트** · 주인공 · 나노바나나 Pro · 16:9

``` text
Photorealistic character reference sheet of ONE fictional original Korean woman who does not resemble any real person. Landscape 16:9, clean light-gray studio background, 13 panels separated by thin white lines, nothing overlapping or cropped.

IDENTITY: Seoyun, 26, the visual of a top-tier Korean film actress: small oval face with a softly defined jaw, clear luminous skin with natural pores, almond-shaped dark brown eyes with subtle inner double eyelids and slightly lifted outer corners, a high slim nose with a rounded tip, naturally full coral lips, a small beauty mark under her right eye, a glossy straight black bob just above the shoulders, slender build.

WARDROBE (same in every full-body panel): white button-up shirt with rolled sleeves, beige linen barista apron with a small name tag, black slacks, white sneakers, small silver stud earrings.

LAYOUT:
Left: 1 large chest-up front portrait.
Center top row: head-and-shoulders front, 45-degree three-quarter, 90-degree side profile.
Center bottom row: calm, startled, cold confident smile.
Center right: full body front, side, back.
Right column: close-ups of eyes, nose, lips, hair.

CONSISTENCY: exactly the same person in all 13 panels; same bone structure, eye shape, eyelids, nose, lips, distinguishing marks, hairline, haircut, skin tone, age and proportions. Expressions change only through natural muscle movement.

QUALITY: ultra-photorealistic live-action portrait photography, even soft studio lighting, realistic skin microtexture, individual hair strands, natural eye reflections, realistic fabric. Attractive but believable, natural eye size, natural proportions.

AVOID: identity drift, extra people, distorted hands, plastic skin, text, watermark.
```

**오정훈 부장 캐릭터 시트** · 상대역 · 나노바나나 Pro · 16:9

``` text
Photorealistic character reference sheet of ONE fictional original Korean man who does not resemble any real person. Landscape 16:9, clean light-gray studio background, 13 panels separated by thin white lines, nothing overlapping or cropped.

IDENTITY: Mr. Oh, 48, the visual of a seasoned Korean character actor: round face with full cheeks, thick dark eyebrows, small hooded eyes, a small mole on his left cheek, a broad nose, short side-parted black hair graying at the temples, thin gold-rimmed glasses, slightly heavy build.

WARDROBE (same in every full-body panel): charcoal gray suit, navy tie, gold wristwatch, black leather shoes.

LAYOUT:
Left: 1 large chest-up front portrait.
Center top row: head-and-shoulders front, 45-degree three-quarter, 90-degree side profile.
Center bottom row: arrogant smirk, shouting in anger, frozen in shock.
Center right: full body front, side, back.
Right column: close-ups of eyes, nose, lips, hair.

CONSISTENCY: exactly the same person in all 13 panels; same bone structure, eye shape, eyelids, nose, lips, distinguishing marks, hairline, haircut, skin tone, age and proportions. Expressions change only through natural muscle movement.

QUALITY: ultra-photorealistic live-action portrait photography, even soft studio lighting, realistic skin microtexture, individual hair strands, natural eye reflections, realistic fabric. Attractive but believable, natural eye size, natural proportions.

AVOID: identity drift, extra people, distorted hands, plastic skin, text, watermark.
```

**강민재 비서 캐릭터 시트** · 조연 · 나노바나나 Pro · 16:9

``` text
Photorealistic character reference sheet of ONE fictional original Korean man who does not resemble any real person. Landscape 16:9, clean light-gray studio background, 13 panels separated by thin white lines, nothing overlapping or cropped.

IDENTITY: Kang, 32, the sleek visual of a top-tier Korean actor: long narrow face with a sharp jawline, calm monolid eyes, a straight high nose, thin lips, a small scar above his right eyebrow, neatly slicked-back black hair, slim tall build.

WARDROBE (same in every full-body panel): black suit, white shirt, black tie, black leather shoes, holding a black leather folder.

LAYOUT:
Left: 1 large chest-up front portrait.
Center top row: head-and-shoulders front, 45-degree three-quarter, 90-degree side profile.
Center bottom row: neutral, polite, serious.
Center right: full body front, side, back.
Right column: close-ups of eyes, nose, lips, hair.

CONSISTENCY: exactly the same person in all 13 panels; same bone structure, eye shape, eyelids, nose, lips, distinguishing marks, hairline, haircut, skin tone, age and proportions. Expressions change only through natural muscle movement.

QUALITY: ultra-photorealistic live-action portrait photography, even soft studio lighting, realistic skin microtexture, individual hair strands, natural eye reflections, realistic fabric. Attractive but believable, natural eye size, natural proportions.

AVOID: identity drift, extra people, distorted hands, plastic skin, text, watermark.
```

**얼굴 지문:** 서윤은 눈 밑 점과 올라간 눈꼬리, 오 부장은 볼의 점과 둥근 얼굴, 강 비서는 눈썹 위 흉터와 무쌍이에요. 세 사람이 닮지 않고, 실존 인물로 오인되어 생성이 막히는 일도 줄어요.

**장소 레퍼런스** · Gemini · 사람 없이

``` text
Empty establishing shot of a modern minimalist café in a Seoul office building, light oak counter, black espresso machine, large windows, warm pendant lights, small round tables, morning light, no people, photorealistic, vertical 9:16, no text, no watermark
```

### 예제 · 컷별 프롬프트

컷마다 이미지 프롬프트(STEP 6)와 영상 프롬프트(STEP 7)가 짝으로 있어요. 영상 프롬프트 속 한국어 대사는 A안용이에요. B안이라면 따옴표 대사 부분을 지우고 쓰세요.

#### 컷 01 · 0:00–0:03 · 익스트림 클로즈업

카운터에 커피잔이 쾅 내려놓이며 커피가 튄다.

오 부장(화면 밖): “이걸 커피라고 준 거야?!”

**이미지 프롬프트** · Gemini · 오 부장 레퍼런스 첨부

``` text
Extreme close-up of a white ceramic coffee cup being slammed onto the counter of a modern minimalist café in a Seoul office building, light oak counter, black espresso machine, large windows, warm pendant lights, coffee splashing out, a man's hand in a charcoal gray suit sleeve with a gold wristwatch, frozen motion. cinematic Korean drama still, photorealistic, soft warm window light, shallow depth of field, vertical 9:16, no text, no watermark
```

**영상 프롬프트** · Kling · 5초 생성 → 3초 사용

``` text
One continuous shot, no cuts, same framing throughout. Static camera. The hand slams the cup down and coffee splashes in slow motion across the counter. A sharp ceramic slam, then a man shouts off-screen in Korean, angry: "이걸 커피라고 준 거야?!" No text, no subtitles.
```

소리: 도자기 ‘쾅’ · 훅 문구 “알바생에게 갑질한 손님의 최후”

#### 컷 02 · 0:03–0:08 · 미디엄 (서윤 시점)

오 부장이 카운터 너머로 몸을 숙이며 삿대질한다.

오 부장: “연하게 달라고 했잖아! 귀가 없어?”

**이미지 프롬프트** · Gemini · 오 부장 레퍼런스 첨부

``` text
Point-of-view shot from behind the café counter: Mr. Oh, 48, the visual of a seasoned Korean character actor: round face with full cheeks, thick dark eyebrows, small hooded eyes, a small mole on his left cheek, a broad nose, short side-parted black hair graying at the temples, thin gold-rimmed glasses, slightly heavy build, wearing charcoal gray suit, navy tie, gold wristwatch, black leather shoes, leaning over the counter and pointing his finger at the camera, shouting with an angry red face. Background: a modern minimalist café in a Seoul office building, light oak counter, black espresso machine, large windows, warm pendant lights. cinematic Korean drama still, photorealistic, soft warm window light, shallow depth of field, vertical 9:16, no text, no watermark
```

**영상 프롬프트** · Kling · 5초

``` text
One continuous shot, no cuts, same framing throughout. Handheld camera with a slight shake. The man leans closer, jabbing his finger toward the camera while he shouts. Customers in the background stay blurred. He shouts in Korean, loud and arrogant: "연하게 달라고 했잖아! 귀가 없어?" No text, no subtitles.
```

소리: 긴장 음악 시작 (작게)

#### 컷 03 · 0:08–0:12 · 클로즈업

서윤이 잠깐 놀라지만 침착하게 고개를 숙인다.

서윤: “죄송합니다. 다시 만들어 드릴게요.”

**이미지 프롬프트** · Gemini · 서윤 레퍼런스 첨부

``` text
Close-up of Seoyun, 26, the visual of a top-tier Korean film actress: small oval face with a softly defined jaw, clear luminous skin with natural pores, almond-shaped dark brown eyes with subtle inner double eyelids and slightly lifted outer corners, a high slim nose with a rounded tip, naturally full coral lips, a small beauty mark under her right eye, a glossy straight black bob just above the shoulders, slender build, wearing white button-up shirt with rolled sleeves, beige linen barista apron with a small name tag, black slacks, white sneakers, small silver stud earrings, standing behind the café counter, calm but slightly startled expression, about to bow her head politely. Background softly blurred: a modern minimalist café in a Seoul office building, light oak counter, black espresso machine, large windows, warm pendant lights. cinematic Korean drama still, photorealistic, soft warm window light, shallow depth of field, vertical 9:16, no text, no watermark
```

**영상 프롬프트** · Kling · 5초 생성 → 4초 사용

``` text
One continuous shot, no cuts, same framing throughout. Slow push-in. She blinks once, keeps her composure and bows her head slightly. She says in Korean, polite and calm: "죄송합니다. 다시 만들어 드릴게요." No text, no subtitles.
```

소리: —

#### 컷 04 · 0:12–0:17 · 바스트샷

오 부장이 비웃으며 카운터 위 명함을 손가락으로 두드린다.

오 부장: “됐고, 사장 나오라 그래!”

**이미지 프롬프트** · Gemini · 오 부장 레퍼런스 첨부

``` text
Medium close-up of Mr. Oh, 48, the visual of a seasoned Korean character actor: round face with full cheeks, thick dark eyebrows, small hooded eyes, a small mole on his left cheek, a broad nose, short side-parted black hair graying at the temples, thin gold-rimmed glasses, slightly heavy build, wearing charcoal gray suit, navy tie, gold wristwatch, black leather shoes, smirking arrogantly, his index finger resting on a white business card lying on the counter. Background: a modern minimalist café in a Seoul office building, light oak counter, black espresso machine, large windows, warm pendant lights. cinematic Korean drama still, photorealistic, soft warm window light, shallow depth of field, vertical 9:16, no text, no watermark
```

**영상 프롬프트** · Kling · 5초

``` text
One continuous shot, no cuts, same framing throughout. Static camera. He smirks, taps the business card twice with his index finger, then leans back. He says in Korean, mocking: "됐고, 사장 나오라 그래!" No text, no subtitles.
```

소리: 손가락 ‘톡톡’

#### 컷 05 · 0:17–0:21 · 와이드

카페 손님들이 고개를 돌려 쳐다보며 수군거린다.

**이미지 프롬프트** · Gemini · 장소 레퍼런스 첨부

``` text
Wide shot of the interior of a modern minimalist café in a Seoul office building, light oak counter, black espresso machine, large windows, warm pendant lights: several customers at small round tables turn their heads toward the counter and whisper to each other; a man in a charcoal gray suit stands at the counter in the middle ground, seen from behind. cinematic Korean drama still, photorealistic, soft warm window light, shallow depth of field, vertical 9:16, no text, no watermark
```

**영상 프롬프트** · Kling · 5초 생성 → 4초 사용

``` text
One continuous shot, no cuts, same framing throughout. Slow pan from left to right across the café. Customers turn their heads toward the counter and whisper to each other. Ambient sound of a murmuring crowd and soft café noise. No text, no subtitles.
```

소리: 카페 웅성거림

#### 컷 06 · 0:21–0:26 · 클로즈업

서윤이 명함을 내려다보다 천천히 고개를 들며 옅게 웃는다.

서윤: “대한물산… 오정훈 부장님?”

**이미지 프롬프트** · Gemini · 서윤 레퍼런스 첨부

``` text
Close-up of Seoyun, 26, the visual of a top-tier Korean film actress: small oval face with a softly defined jaw, clear luminous skin with natural pores, almond-shaped dark brown eyes with subtle inner double eyelids and slightly lifted outer corners, a high slim nose with a rounded tip, naturally full coral lips, a small beauty mark under her right eye, a glossy straight black bob just above the shoulders, slender build, wearing white button-up shirt with rolled sleeves, beige linen barista apron with a small name tag, black slacks, white sneakers, small silver stud earrings, looking down at a white business card on the counter, face calm and unreadable. Background softly blurred: a modern minimalist café in a Seoul office building, light oak counter, black espresso machine, large windows, warm pendant lights. cinematic Korean drama still, photorealistic, soft warm window light, shallow depth of field, vertical 9:16, no text, no watermark
```

**영상 프롬프트** · Kling · 5초

``` text
One continuous shot, no cuts, same framing throughout. Static close-up. She studies the card, then slowly raises her eyes with a faint, knowing smile. She says quietly in Korean: "대한물산... 오정훈 부장님?" No text, no subtitles.
```

소리: —

#### 컷 07 · 0:26–0:30 · 미디엄

오 부장이 팔짱을 끼고 턱을 치켜든다.

오 부장: “그래! 알바 주제에… 당장 사장 불러!”

**이미지 프롬프트** · Gemini · 오 부장 레퍼런스 첨부

``` text
Medium shot of Mr. Oh, 48, the visual of a seasoned Korean character actor: round face with full cheeks, thick dark eyebrows, small hooded eyes, a small mole on his left cheek, a broad nose, short side-parted black hair graying at the temples, thin gold-rimmed glasses, slightly heavy build, wearing charcoal gray suit, navy tie, gold wristwatch, black leather shoes, arms crossed, chin raised, condescending look, standing at the café counter. Background: a modern minimalist café in a Seoul office building, light oak counter, black espresso machine, large windows, warm pendant lights. cinematic Korean drama still, photorealistic, soft warm window light, shallow depth of field, vertical 9:16, no text, no watermark
```

**영상 프롬프트** · Kling · 5초 생성 → 4초 사용

``` text
One continuous shot, no cuts, same framing throughout. Static camera. He scoffs, tightens his crossed arms and raises his chin. He says in Korean, condescending: "그래! 알바 주제에... 당장 사장 불러!" No text, no subtitles.
```

소리: 긴장 음악 최고조

#### 컷 08 · 0:30–0:35 · 풀샷

유리문이 열리고 검은 정장의 강 비서가 빠르게 걸어 들어온다.

**이미지 프롬프트** · Gemini · 강 비서 레퍼런스 첨부

``` text
Full shot of the glass entrance door of a modern minimalist café in a Seoul office building, light oak counter, black espresso machine, large windows, warm pendant lights swinging open, Kang, 32, the sleek visual of a top-tier Korean actor: long narrow face with a sharp jawline, calm monolid eyes, a straight high nose, thin lips, a small scar above his right eyebrow, neatly slicked-back black hair, slim tall build, wearing black suit, white shirt, black tie, black leather shoes, holding a black leather folder, striding in briskly, bright daylight behind him. cinematic Korean drama still, photorealistic, soft warm window light, shallow depth of field, vertical 9:16, no text, no watermark
```

**영상 프롬프트** · Kling · 5초

``` text
One continuous shot, no cuts, same framing throughout. The camera slowly tracks backward as the man in the black suit walks briskly toward it. A door bell chimes and his footsteps echo on the floor. No text, no subtitles.
```

소리: 음악 끊김 · 문 종소리 ‘딸랑’ · 구두 발소리

#### 컷 09 · 0:35–0:40 · 미디엄 투샷

강 비서가 서윤 앞에서 정중히 고개를 숙인다.

강 비서: “대표님, 이사회 십 분 전입니다.”

**이미지 프롬프트** · Gemini · 강 비서 + 서윤 (둘 다 첨부) 레퍼런스 첨부

``` text
Medium two-shot inside a modern minimalist café in a Seoul office building, light oak counter, black espresso machine, large windows, warm pendant lights: Kang, 32, the sleek visual of a top-tier Korean actor: long narrow face with a sharp jawline, calm monolid eyes, a straight high nose, thin lips, a small scar above his right eyebrow, neatly slicked-back black hair, slim tall build, wearing black suit, white shirt, black tie, black leather shoes, holding a black leather folder, stands in front of the counter, bowing politely toward Seoyun, 26, the visual of a top-tier Korean film actress: small oval face with a softly defined jaw, clear luminous skin with natural pores, almond-shaped dark brown eyes with subtle inner double eyelids and slightly lifted outer corners, a high slim nose with a rounded tip, naturally full coral lips, a small beauty mark under her right eye, a glossy straight black bob just above the shoulders, slender build, wearing white button-up shirt with rolled sleeves, beige linen barista apron with a small name tag, black slacks, white sneakers, small silver stud earrings, who stands behind the counter. cinematic Korean drama still, photorealistic, soft warm window light, shallow depth of field, vertical 9:16, no text, no watermark
```

**영상 프롬프트** · Kling · 5초

``` text
One continuous shot, no cuts, same framing throughout. Static camera. The man in the black suit stops in front of the counter and bows politely to the woman. He says in Korean, calm and respectful: "대표님, 이사회 십 분 전입니다." No text, no subtitles.
```

소리: 반전 테마 시작

#### 컷 10 · 0:40–0:45 · 클로즈업

오 부장의 얼굴이 얼어붙고 입이 벌어진다.

오 부장: “대… 대표님?”

**이미지 프롬프트** · Gemini · 오 부장 레퍼런스 첨부

``` text
Close-up of Mr. Oh, 48, the visual of a seasoned Korean character actor: round face with full cheeks, thick dark eyebrows, small hooded eyes, a small mole on his left cheek, a broad nose, short side-parted black hair graying at the temples, thin gold-rimmed glasses, slightly heavy build, wearing charcoal gray suit, navy tie, gold wristwatch, black leather shoes, face frozen in shock, mouth slightly open, eyes wide behind his glasses. Background softly blurred: a modern minimalist café in a Seoul office building, light oak counter, black espresso machine, large windows, warm pendant lights. cinematic Korean drama still, photorealistic, soft warm window light, shallow depth of field, vertical 9:16, no text, no watermark
```

**영상 프롬프트** · Kling · 5초

``` text
One continuous shot, no cuts, same framing throughout. Fast push-in on his face. His expression freezes in shock and his mouth falls open. He stammers in Korean: "대... 대표님?" A deep dramatic impact sound. No text, no subtitles.
```

소리: 임팩트 ‘두둥’

#### 컷 11 · 0:45–0:53 · 바스트샷

서윤이 앞치마를 벗어 내려놓고, 오 부장을 똑바로 보며 차갑게 웃는다.

서윤: “오늘 저희가 인수하는 회사… 대한물산이죠? 곧 또 뵙겠네요, 부장님.”

**이미지 프롬프트** · Gemini · 서윤 레퍼런스 첨부

``` text
Medium close-up of Seoyun, 26, the visual of a top-tier Korean film actress: small oval face with a softly defined jaw, clear luminous skin with natural pores, almond-shaped dark brown eyes with subtle inner double eyelids and slightly lifted outer corners, a high slim nose with a rounded tip, naturally full coral lips, a small beauty mark under her right eye, a glossy straight black bob just above the shoulders, slender build, wearing white button-up shirt with rolled sleeves, beige linen barista apron with a small name tag, black slacks, white sneakers, small silver stud earrings, untying her beige apron behind the counter, looking straight into the camera with a cold, confident smile. Background: a modern minimalist café in a Seoul office building, light oak counter, black espresso machine, large windows, warm pendant lights. cinematic Korean drama still, photorealistic, soft warm window light, shallow depth of field, vertical 9:16, no text, no watermark
```

**영상 프롬프트** · Kling · 10초 생성 → 8초 사용

``` text
One continuous shot, no cuts, same framing throughout. Slow push-in. She takes off the apron, places it on the counter and looks straight at the camera with a cold, confident smile. She says in Korean, calm and cold: "오늘 저희가 인수하는 회사... 대한물산이죠? 곧 또 뵙겠네요, 부장님." No text, no subtitles.
```

소리: —

메모: 손 동작이 깨지면 앞치마를 이미 벗은 이미지로 시작하고, 미소와 대사만 넣으세요.

#### 컷 12 · 0:53–1:00 · 와이드

얼어붙은 오 부장 뒤로 서윤과 강 비서가 카페를 나간다. 화면이 어두워진다.

**이미지 프롬프트** · Gemini · 오 부장 + 서윤 + 강 비서 레퍼런스 첨부

``` text
Wide shot from behind the man in the charcoal gray suit: his charcoal gray suit shoulders and graying hair blurred in the foreground; in the background Seoyun, a 26-year-old Korean woman with a glossy straight black bob, white button-up shirt with rolled sleeves, no apron, and Kang, 32, the sleek visual of a top-tier Korean actor: long narrow face with a sharp jawline, calm monolid eyes, a straight high nose, thin lips, a small scar above his right eyebrow, neatly slicked-back black hair, slim tall build, wearing black suit, white shirt, black tie, black leather shoes, holding a black leather folder, walk out through the glass door of a modern minimalist café in a Seoul office building, light oak counter, black espresso machine, large windows, warm pendant lights into bright daylight. cinematic Korean drama still, photorealistic, soft warm window light, shallow depth of field, vertical 9:16, no text, no watermark
```

**영상 프롬프트** · Kling · 10초 생성 → 7초 사용

``` text
One continuous shot, no cuts, same framing throughout. Static camera with a slow rack focus from the frozen man in the foreground to the two people leaving through the glass door. The door bell chimes. Slow fade to black at the end. No text, no subtitles.
```

소리: 문 종소리 ‘딸랑’ · 엔딩 음악 · “2화에서 계속”

메모: 서윤의 고정 문장에서 앞치마만 뺐어요.

### 예제 · 목소리·사운드·편집

### 인물별 목소리

| 인물            | 목소리 방향                                                            | ElevenLabs 보이스 디자인 문장                                                              |
|-----------------|------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| **한서윤**      | 20대 중반 여성. 낮고 또렷하게, 감정은 절제. 11번 컷만 차갑고 단호하게. | A calm, composed Korean woman in her mid-20s with a low, clear voice and quiet confidence. |
| **오정훈 부장** | 40대 후반 남성. 굵고 큰 소리, 거만하게. 10번 컷은 말을 더듬어요.       | An arrogant Korean man in his late 40s with a deep, loud, condescending voice.             |
| **강민재 비서** | 30대 초반 남성. 낮고 정중하게, 감정 없이.                              | A composed Korean male secretary in his early 30s with a crisp, low, very polite voice.    |

Typecast에서는 위 방향에 맞는 목소리를 고르고 감정(차분, 화남, 단호 등)과 속도를 조절하세요. A안이라면 이 목소리 묘사를 영상 프롬프트의 대사 앞에 넣어도 돼요.

### 음악·효과음 큐시트

| 시간 | 음악                   | 효과음                         |
|------|------------------------|--------------------------------|
| 0:00 | (없음)                 | 도자기 컵 ‘쾅’                 |
| 0:03 | 긴장 음악 시작 (작게)  | —                              |
| 0:13 | —                      | 손가락 ‘톡톡’                  |
| 0:17 | —                      | 카페 웅성거림 (4초)            |
| 0:26 | 긴장 음악 최고조       | —                              |
| 0:30 | 음악 뚝 끊기 (정적)    | 문 종소리 ‘딸랑’ + 구두 발소리 |
| 0:35 | 반전 테마 시작         | —                              |
| 0:41 | —                      | 임팩트 ‘두둥’                  |
| 0:53 | 엔딩 → 서서히 작아지기 | —                              |
| 0:57 | —                      | 문 종소리 ‘딸랑’               |

### 편집 순서

1.  컷 1~12를 순서대로 놓고, 위 대본 표의 시간에 맞춰 길이를 잘라요.
2.  대사(A안이면 영상 속 소리, B안이면 음성 파일)를 맞춰요.
3.  큐시트대로 음악과 효과음을 놓아요. 30초의 정적이 이 작품의 하이라이트예요.
4.  자막을 넣고, 0~3초 위쪽에 “알바생에게 갑질한 손님의 최후”를 넣어요.
5.  마지막 2초에 “2화에서 계속”을 넣고 화면을 어둡게 해요.
6.  1080×1920으로 내보내 ‘알바생의정체_1화.mp4’로 저장해요.

제목 예시는 STEP 11에 있어요. 커버는 10번 컷의 얼어붙은 표정을 추천해요.

실습 · 두 번째 작품부터

## 내 작품 기획서

칸을 채우면 아래 프롬프트들이 내 작품에 맞게 바로 바뀌어요. 적은 내용은 자동으로 저장돼요. Claude 앱에서 이 페이지를 열었다면 ‘AI 코치로’ 버튼을 눌러 여기서 바로 대본과 샷리스트를 만들 수도 있어요.

이 기획서는 칸을 채우면 대본·캐릭터 시트·샷리스트·제목 프롬프트가 자동으로 만들어지는 입력 화면이라, 글 버전에서는 빠졌어요. index.html이나 Claude 아티팩트 페이지에서 쓰세요. 프롬프트 원본은 STEP 3, 4, 5, 11에 있어요.

실습 · 하루 1~2시간

## 2주 완성 플랜

첫 주는 예제로 손에 익히고, 둘째 주는 내 이야기로 만들어요. 하루를 마칠 때마다 체크하세요.

### 1주차 · 예제 「알바생의 정체」 완성

- [ ] **D1** 제작 방식 고르기, 계정 만들기, 폴더 만들기 (시작 1~2 · 1시간)
- [ ] **D2** AI 숏드라마 10편 보고 벤치마킹 노트 쓰기 (STEP 1 · 1시간)
- [ ] **D3** 예제 대본 읽기, 인물 3명 캐릭터 시트 만들기 (STEP 3~5 · 2시간)
- [ ] **D4** 장면 이미지 12장 만들기 (STEP 6 · 2시간)
- [ ] **D5** 컷 1~6 영상 만들기 (STEP 7 · 1.5시간)
- [ ] **D6** 컷 7~12 영상 만들기, 목소리 정리 (STEP 7~8 · 2시간)
- [ ] **D7** 음악·편집·업로드. 첫 작품 완성! (STEP 9~12 · 2시간)

### 2주차 · 내 이야기로 2편 만들기

- [ ] **D8** 1편 48시간 숫자 보기, 내 작품 기획서 쓰기 (STEP 12 · STEP 2 · 1시간)
- [ ] **D9** 대본 받고 두 번 이상 다듬기 (STEP 3 · 1시간)
- [ ] **D10** 샷리스트 만들기, 캐릭터 고정하기 (STEP 4~5 · 2시간)
- [ ] **D11** 장면 이미지 만들기 (STEP 6 · 2시간)
- [ ] **D12** 영상 만들기 (STEP 7 · 2시간)
- [ ] **D13** 목소리·음악·편집 (STEP 8~10 · 2시간)
- [ ] **D14** 제목·AI 표시·업로드, 3화 로그라인 쓰기 (STEP 11~12 · 1시간)

도움말

## 막힐 때 보는 해결 모음

#### 컷마다 주인공 얼굴이 달라져요

1.  정면 클로즈업 레퍼런스를 매번 첨부하세요.
2.  캐릭터 고정 문장을 글자 그대로 복사해 넣으세요.
3.  글로 바로 영상을 만들지 말고, 이미지에서 얼굴을 확정한 뒤 그 이미지를 움직이세요.
4.  Kling의 참고 자료(인물 등록) 기능에 레퍼런스를 넣어 보세요.
5.  그래도 튀는 컷은 그 컷만 다시 만드세요.

#### 손가락이나 물건이 이상하게 나와요

손 동작을 한 컷에 하나로 줄이고, 손이 화면 밖에 있도록 구도를 바꿔 보세요. 컵이나 명함 같은 물건은 키프레임 이미지에 미리 그려 두면 덜 깨져요. 이미지 프롬프트에 hands resting naturally를 넣는 것도 도움이 돼요.

#### 인물이 녹아내리거나 이상하게 움직여요

동작을 하나만 남기고 slowly, subtle을 넣어 움직임을 작게 하세요. 5초로 짧게 만들고, 카메라와 인물을 동시에 크게 움직이지 마세요.

#### 화면에 이상한 글자나 자막이 생겨요

이미지 프롬프트 끝에 no text, no subtitles, no watermark를 넣으세요. 자막은 편집 단계에서 직접 넣는 거예요. 이미 생긴 글자는 편집에서 확대로 잘라 내거나 흐리게 가리세요.

#### 한국어 대사 발음이 어색해요

숫자와 영어를 한글로 풀어 쓰고(10분 → 십 분), 쉼표와 말줄임표로 호흡을 넣고, 긴 문장은 두 개로 나누세요. 그래도 어색하면 그 컷만 B안(Typecast 같은 AI 음성)으로 바꾸세요.

#### 입 모양이 대사와 맞지 않아요

대사를 영상 생성 때 함께 넣거나(A안), 영상 도구의 립싱크 기능을 쓰세요. 입이 잘 보이지 않는 옆모습, 뒷모습, 듣는 사람의 반응 컷에 대사를 깔아도 자연스러워요.

#### 같은 인물인데 컷마다 목소리가 달라요

A안은 컷마다 목소리가 조금씩 바뀔 수 있어요. 인물의 목소리 묘사를 모든 컷에 똑같이 넣거나, 그 인물만 B안의 한 목소리로 통일하세요.

#### 크레딧이 금방 떨어져요

이미지 단계에서 충분히 고르고, 영상은 확정된 컷만 만드세요. 처음엔 5초, 시안은 가벼운 모델로 만들고, 무료 크레딧은 매일 받아 쓰세요. 무료 크레딧은 다음 날로 이월되지 않아요.

#### 영상이 가로로 나오거나 위아래가 잘려요

키프레임 이미지, 영상 생성 설정, 편집 프로젝트를 모두 9:16으로 맞추세요. 세 곳 중 하나라도 다르면 잘리거나 검은 띠가 생겨요.

#### 무료 플랜 워터마크를 지워도 되나요?

지우는 도구로 없애면 서비스 약관 위반이 될 수 있어요. 공개할 영상은 유료 플랜에서 다시 만들거나, 연습용이라면 워터마크를 그대로 두세요.

#### Flow에서 “유명인 관련 정책 위반” 오류로 계속 실패해요

시작 이미지의 얼굴이 실존 인물과 닮았다고 판단되면 같은 이미지로는 계속 막혀요. 실패한 생성의 크레딧은 환불돼요. 고정 문장에 fictional과 둥근 얼굴, 짙은 눈썹, 볼의 점 같은 독특한 특징을 넣어 얼굴 이미지를 새로 만들고, 이름이나 Korean drama 같은 단서는 빼세요. 그래도 막히면 손이나 뒷모습으로 감정을 보여 주는 컷으로 바꾸세요.

#### 8초 영상 뒷부분에 손이 하나 더 생기거나, 장면이 바뀌거나, 글자가 나타나요

AI가 지시받은 동작을 끝낸 뒤 남는 시간을 스스로 채우면서 생기는 일이에요. 영상 프롬프트 맨 앞에 One continuous shot, no cuts, same framing throughout., 끝에 No text, no subtitles.를 넣고, 동작 뒤에 “그 뒤엔 정지(then stays still)”를 붙이세요. 그래도 생기면 가장 좋은 3~5초만 잘라 쓰면 돼요. 오른쪽 아래 작은 ‘Veo’ 표시는 구글의 AI 생성 표시라 지우지 마세요.

#### 연예인을 닮게 만들어도 되나요?

안 돼요. 실존 인물의 얼굴이나 목소리를 쓰면 초상권과 퍼블리시티권을 침해할 수 있고, 딥페이크로 처벌받을 수도 있어요. 가상의 얼굴을 만들어 쓰세요.

#### 영어 프롬프트가 어려워요

한국어로 쓴 뒤 AI 챗봇에 “영어 이미지 프롬프트로 바꿔 줘”라고 하면 돼요. Gemini 이미지 생성은 한국어 요청도 잘 알아들어요. 이 페이지의 프롬프트 공식을 복사해 빈칸만 바꿔 써도 충분해요.

#### 올렸는데 조회수가 안 나와요

첫 1초를 바꿔 보세요. 가장 센 장면을 맨 앞에 두고, 제목에 궁금증을 남기세요. 한 편으로 판단하지 말고 같은 캐릭터로 최소 10편을 올리면서 48시간 숫자를 보고 한 가지씩 고치세요.

도움말 · 올리기 전에 꼭

## 꼭 지킬 규칙: 저작권·AI 표시·수익화

### 1. 실존 인물은 쓰지 않아요

연예인이나 지인의 얼굴·목소리를 합성하지 마세요. 초상권과 퍼블리시티권 침해가 될 수 있고 딥페이크 처벌 대상이 될 수 있어요. 목소리 복제는 본인 목소리로만 하세요.

### 2. 남의 작품·브랜드는 빼요

기존 드라마·만화 캐릭터, 실제 회사 로고, 유명한 음악은 넣지 마세요. 디즈니가 ByteDance의 Seedance 2.0에 자사 캐릭터 문제로 반발한 일처럼, AI 결과물이라도 저작권 문제는 그대로예요.

### 3. AI로 만들었다고 밝혀요

YouTube의 ‘변경되거나 합성된 콘텐츠’, Instagram의 AI 레이블, TikTok의 AI 생성 콘텐츠 표시를 켜고 설명란에도 적으세요. 2026년 1월 22일 시행된 AI 기본법의 표시 의무는 주로 AI 서비스 제공자에게 있고, 도구를 쓰는 개인 창작자에게는 과도한 의무를 지우지 않는 방향으로 안내되고 있어요. 그래도 실제처럼 보이는 영상은 표시하는 습관이 가장 안전해요.

### 4. 무료 플랜 결과물은 수익화에 쓰지 않아요

Kling 무료, Suno 무료처럼 상업적 이용을 막는 플랜이 많아요. 수익을 낼 채널이라면 유료 플랜에서 만든 결과물을 쓰고, 서비스마다 약관을 확인하세요.

### 5. YouTube 수익화 기준을 알아 둬요

AI 사용 자체는 괜찮아요. 하지만 2026년 7월 YouTube가 명확히 한 기준에 따르면 틀만 바꾼 대량 반복 영상, 불쾌하거나 충격적인 영상, 건강·금융 같은 민감 주제를 AI 인물이 말하는 영상은 수익을 낼 수 없어요. 편마다 새 이야기와 내 편집을 담으세요.

### 6. 내가 기여한 부분을 남겨 둬요

문화체육관광부와 한국저작권위원회의 「생성형 AI 활용 저작물의 저작권 등록 안내서」(2025년 6월)에 따르면 AI가 만든 결과물 자체는 보호받기 어렵고, 사람이 창작적으로 기여한 부분(대본, 선택과 배열, 편집)이 보호 대상이에요. 기획서, 대본, 프롬프트와 작업 기록을 저장해 두세요.

### 7. 자극에는 선이 있어요

폭력, 혐오, 선정적인 장면과 특정 집단을 깎아내리는 내용은 넣지 마세요. 막장 드라마도 선을 넘으면 노출이 제한되고 수익을 낼 수 없어요.

도움말 · 강의에서 자주 나오는 말

## A부터 Z까지 용어 사전

- **A · 화면비 Aspect Ratio**: 숏폼은 9:16 세로. 이미지, 영상, 편집 모두 같은 비율로 맞춰요.
- **B · 인서트 컷 B-roll**: 장소나 분위기를 보여 주는 보조 컷. 대사 사이에 숨 쉴 틈을 줘요.
- **C · 클리프행어 Cliffhanger**: 가장 궁금한 순간에 끊어서 다음 화를 보게 만드는 끝맺음.
- **D · 다가가기 Dolly In · Push-in**: 카메라가 인물에게 다가가며 긴장을 높이는 움직임.
- **E · 익스트림 클로즈업 ECU**: 눈, 입술, 손끝처럼 한 부분만 아주 크게 보여 주는 샷.
- **F · 첫 프레임 First Frame**: 이미지로 영상을 만들 때의 시작 그림. 쇼츠 피드에서 가장 먼저 보이는 화면이기도 해요.
- **G · 생성 크레딧 Generation Credit**: 이미지나 영상을 한 번 만들 때 쓰는 포인트. 모델과 길이에 따라 드는 양이 달라요.
- **H · 훅 Hook**: 첫 1~3초에 스크롤을 멈추게 하는 장면이나 대사.
- **I · 이미지→영상 Image-to-Video · I2V**: 정지 이미지를 움직이는 클립으로 바꾸는 방식. 얼굴을 지키기에 유리해요.
- **J · J컷 J-cut**: 다음 장면의 소리가 화면보다 먼저 들리게 붙이는 편집.
- **K · 키프레임 Keyframe**: 컷의 핵심 장면 그림. Kling 4.0은 한 영상에 최대 10장을 넣을 수 있어요.
- **L · 립싱크 Lip Sync**: 입 모양을 대사에 맞추는 것.
- **M · 모션 프롬프트 Motion Prompt**: 카메라와 인물의 움직임을 지시하는 문장.
- **N · 네거티브 프롬프트 Negative Prompt**: 나오지 말아야 할 것. 예: no text, no watermark.
- **O · 오버 더 숄더 OTS**: 한 사람의 어깨 너머로 상대를 보는 대화 샷.
- **P · 프롬프트 Prompt**: AI에게 주는 지시문. 공식대로 쓰면 결과가 안정돼요.
- **Q · 품질 모드 Quality Mode**: 가벼운(Lite), 빠른(Fast), 고품질(Quality) 중 고르는 설정. 시안은 가볍게 만들어요.
- **R · 레퍼런스 이미지 Reference Image**: 얼굴, 의상, 장소를 고정하려고 함께 넣는 참고 그림.
- **S · 샷리스트 Shot List**: 컷 번호, 크기, 움직임, 대사, 길이를 정리한 표.
- **T · 음성 합성 TTS · Text-to-Speech**: 글을 목소리로 바꾸는 기술. Typecast, ElevenLabs, 클로바더빙 등.
- **U · 업스케일 Upscale**: 낮은 해상도의 영상을 높은 해상도로 키우는 작업.
- **V · 보이스오버 Voice-over**: 화면 밖에서 들리는 목소리나 내레이션.
- **W · 워터마크 Watermark**: 무료 플랜의 로고, 또는 AI로 만들었다는 표시.
- **X · 크로스페이드 X-fade · Crossfade**: 두 소리나 장면을 겹치며 자연스럽게 바꾸는 전환.
- **Y · 유튜브 쇼츠 YouTube Shorts**: 최대 3분의 세로 영상. AI 숏드라마의 기본 무대예요.
- **Z · 줌 Zoom**: 렌즈로 화면을 확대하거나 축소하는 것. 급줌은 반전 순간의 단골 연출이에요.

기준일 2026년 10월 23일

## 출처와 확인 방법

도구, 가격, 정책 정보는 2026년 10월 23일에 확인했어요. AI 도구는 몇 주 단위로 바뀌니 결제하거나 수익화를 시작하기 전에는 공식 페이지를 다시 확인하세요.

- Kling 4.0 전면 공개: [Let’s Data Science](https://letsdatascience.com/news/kling-ai-opens-kling-40-to-all-users-d9dc6422) · 초기 사용기: [MindStudio](https://www.mindstudio.ai/blog/kling-4-0-first-look/)
- Kling 요금제: [Aiarty (2026년 8월 확인)](https://www.aiarty.com/ai-video-generator/kling-ai-pricing.htm) · [Wireflow (2026년 10월)](https://www.wireflow.ai/blog/kling-4-0-pricing)
- Sora 종료: [Engadget](https://engadget.com/ai/openai-is-shutting-down-its-sora-video-generation-app-211023358.html) · [CyberInsider](https://cyberinsider.com/openai-pulls-the-plug-on-sora-ai-video-app-15-months-after-launch/)
- Google Flow 무료 크레딧: [Google Flow 고객센터](https://support.google.com/flow/answer/16526234)
- Gemini Omni Flash: [Shacknews](https://www.shacknews.com/article/149206/google-gemini-omni-multimodal-gen-ai) · [Gemini API 문서](https://ai.google.dev/gemini-api/docs/models/gemini-omni-flash)
- Google AI Plus 국내 출시: [Google 코리아 블로그](https://blog.google/intl/ko-kr/products/google-ai-plus-plans-kr/) · 나노바나나: [Gemini 이미지 생성 안내](https://gemini.google/kr/overview/image-generation/?hl=ko)
- Seedance 2.0: [TechCrunch](https://techcrunch.com/2026/03/26/bytedances-new-ai-video-generation-model-dreamina-seedance-2.0-comes-to-capcut/) · Hailuo H3: [gradually.ai](https://www.gradually.ai/en/ai-video-model-comparison/minimax-h3-vs-hailuo-2-3/)
- YouTube AI 콘텐츠 수익화 기준: [TechCrunch (2026년 7월)](https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/)
- AI 기본법 시행과 표시 의무: [국민일보](https://www.kmib.co.kr/article/view.asp?arcid=1768984300) · [크리에이터 대상 해설](https://ctee.kr/blog/86572)
- 생성형 AI 저작권: [관련 보도 (2026년 4월)](https://v.daum.net/v/20260421144511956)
- 중국 AI 숏드라마 통계: [엑스포츠뉴스](https://www.xportsnews.com/article/2196220) · [위픽 레터](https://letter.wepick.kr/post/26334)
- 국내 동향: [비글루 AI 제작 툴 (유니콘팩토리)](https://www.unicornfactory.co.kr/article/2026071016322471217) · [스타뉴스](https://www.starnewskorea.com/broadcast-drama/2026/09/08/2026082114011033639)
- 음성·음악·편집: [Typecast 비교 글 (제조사 작성)](https://typecast.ai/kr/learn/natural-korean-ai-voice-2026/) · [Suno 상업적 이용](https://dynamoi.com/learn/guides/suno-commercial-rights-explained) · [CapCut 요금 변경 (Newsweek)](https://newsweek.com/app-used-millions-nearly-doubles-subscription-price-overnight-11535999)

AI 숏드라마 제작 교실 · 2026년 10월 23일 판. 예제 「알바생의 정체」의 인물과 회사는 모두 지어낸 것이에요.
