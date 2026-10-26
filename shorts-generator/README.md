# 롱폼 → 숏폼 자동 추출 + 업로드

내 풀영상을 넣으면 숏폼으로 쓸 만한 구간을 AI가 골라 **9:16 세로 영상 + 자막**으로 만들고, 원하면 **YouTube에 자동 업로드(예약 공개 포함)** 까지 합니다.

```
내 영상 → Whisper 받아쓰기 → Claude가 하이라이트 선정 → 얼굴 기준 세로 크롭 → 자막 렌더링 → YouTube 업로드
```

## 1. 설치

1. **ffmpeg** 설치
   - Windows: `winget install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Ubuntu: `sudo apt install ffmpeg`
2. **Python 3.11~3.13** 에서 설치 (3.14 이상은 받아쓰기 패키지 `av` 등의 설치 파일이 아직 없어 빌드 에러가 납니다):
   ```bash
   py install 3.12                     # Windows: 3.12 설치 (또는 python.org에서 설치)
   py -3.12 -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt      # macOS/Linux: .venv/bin/python -m pip ...
   ```
   이후 실행도 `.venv\Scripts\python.exe shorts.py ...`처럼 같은 Python으로 합니다.
   Windows 11에서 **"응용 프로그램 제어 정책에서 이 파일을 차단했습니다"** 가 나오면 스마트 앱 컨트롤이 DLL을 막는 것입니다.
   Windows 보안 → 앱 및 브라우저 컨트롤 → 스마트 앱 컨트롤을 끄거나 WSL(Ubuntu)에서 실행하세요.
3. Claude API 키 설정 ([console.anthropic.com](https://console.anthropic.com)에서 발급)
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."      # Windows PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."
   ```
4. 한글 자막 폰트: 기본값은 나눔고딕입니다. 없으면 설치하거나 `--font "맑은 고딕"`처럼 지정하세요.

## 2. 사용법

```bash
# 추출만 (결과 확인용)
python shorts.py 내영상.mp4

# 추출 + 비공개로 업로드 (Studio에서 확인 후 공개)
python shorts.py 내영상.mp4 --upload

# 추출 + 내일 저녁 6시부터 하루 1개씩 예약 공개
python shorts.py 내영상.mp4 --upload --schedule 2026-11-01T18:00 --interval 24 \
  --footer "풀영상 👉 https://youtu.be/내풀영상ID"

# 폴더 감시 모드: inbox 폴더에 영상을 넣기만 하면 추출 → 업로드까지 자동
python shorts.py --watch inbox --upload --schedule 2026-11-01T18:00
```

**감시 모드**는 `inbox/`에 영상이 들어오면 복사가 끝나길 기다렸다가 처리하고, 끝난 원본은 `inbox/done/`으로 옮깁니다. 실패한 파일은 이름 끝에 `.failed`를 붙여 둡니다. 컴퓨터를 켜두고 실행해 두면 됩니다.

**업로드만 따로** 하고 싶을 때 (추출 결과를 먼저 보고 마음에 안 드는 클립은 `clips.json`에서 지운 뒤 올리기):
```bash
python shorts.py 내영상.mp4            # 1) 추출
python upload.py output/내영상 --privacy public   # 2) 확인 후 업로드
```
이미 올린 클립은 `clips.json`에 `youtube_id`가 기록되어 다시 올라가지 않습니다.

### 결과물 (`output/영상이름/`)

| 파일 | 내용 |
|---|---|
| `short_01_제목.mp4` … | 1080×1920 세로 숏폼 (바이럴 점수 높은 순) |
| `clips.json` | 구간별 시각, 제목, 선정 이유, 점수, 해시태그, 업로드된 영상 ID |
| `transcript.json` | 받아쓰기 캐시 (같은 영상을 다시 돌리면 받아쓰기를 건너뜀) |

업로드 시 제목에는 `#Shorts`, 설명란에는 해시태그와 `--footer` 문구가 자동으로 들어갑니다.

## 3. YouTube 업로드 설정 (처음 한 번)

1. [Google Cloud Console](https://console.cloud.google.com/)에서 새 프로젝트를 만듭니다.
2. **API 및 서비스 → 라이브러리**에서 **YouTube Data API v3**를 검색해 **사용**을 누릅니다.
3. **OAuth 동의 화면**: 사용자 유형 **외부** → 앱 이름과 이메일 입력 → **테스트 사용자**에 내 Google 계정을 추가합니다.
4. **사용자 인증 정보 → 사용자 인증 정보 만들기 → OAuth 클라이언트 ID → 데스크톱 앱**을 만들고 JSON을 다운로드합니다.
5. 받은 파일 이름을 `client_secret.json`으로 바꿔 `shorts.py`와 같은 폴더에 둡니다.
6. 처음 `--upload`를 실행하면 브라우저가 열립니다. 채널 계정으로 로그인하고 허용하면 `token.json`이 저장되어, 다음부터는 묻지 않고 업로드합니다.

> `client_secret.json`과 `token.json`은 내 채널 업로드 권한이므로 다른 사람에게 공유하거나 GitHub에 올리지 마세요 (`.gitignore`에 포함되어 있음).

### ⚠ 꼭 알아야 할 YouTube API 제한

- **새 API 프로젝트는 업로드 영상이 '비공개'로 잠깁니다.** Google 정책상 심사(audit)를 받지 않은 프로젝트로 올린 영상은 비공개로 고정되어, 공개나 예약 공개가 적용되지 않습니다. 해결 방법은 둘 중 하나입니다.
  - 무료인 [YouTube API 서비스 심사](https://support.google.com/youtube/contact/yt_api_form)를 신청합니다. 내 채널에만 쓰는 용도라고 적으면 됩니다.
  - 심사 전에는 `--privacy private`로 올리고 YouTube Studio에서 직접 공개하거나 예약합니다. 이렇게 해도 추출·제목·해시태그·업로드는 자동이라 손이 많이 줄어듭니다.
- **하루 업로드 개수 제한**: 기본 할당량은 하루 10,000 유닛이고 업로드 한 번에 1,600 유닛이 들어서 **하루 약 6개**까지 올릴 수 있습니다. 넘으면 멈추는데, 다음 날 같은 명령을 다시 실행하면 남은 것부터 이어서 올립니다.
- **로그인 7일 만료**: OAuth 동의 화면이 '테스트' 상태면 `token.json`이 7일마다 만료됩니다. 동의 화면에서 **앱 게시(프로덕션으로 푸시)** 를 누르면 계속 유지됩니다. 로그인할 때 '확인되지 않은 앱' 경고가 뜨지만, 내 앱이니 **고급 → 이동**을 누르면 됩니다.

## 4. 옵션 전체

| 옵션 | 설명 | 기본값 |
|---|---|---|
| `-n, --clips` | 뽑을 숏폼 개수 | 5 |
| `--min / --max` | 클립 길이(초) | 20 / 59 |
| `--lang` | 음성 언어 (`ko`, `en` …) | 자동 감지 |
| `--device` | 받아쓰기 장치 `auto` `cpu` `cuda` (GPU가 안 되면 자동으로 CPU) | `auto` |
| `--whisper-model` | `tiny` `base` `small` `medium` `large-v3` (클수록 정확하지만 느림) | `small` |
| `--prompt` | 구간 선정 추가 지시 (예: `"꿀팁 위주로"`) | 없음 |
| `--preset` | 채널 유형별 구간 선정 기준. `story`: 옛날이야기·민담 낭독 (반전·궁금한 장면, 결말은 숨김) | 없음 |
| `--font` | 자막 폰트 이름 (시스템에 설치된 것) | `NanumGothic` |
| `--font-file` | 자막 글꼴 파일 (.ttf/.otf). 설치하지 않아도 됨. 예: `fonts\BMJUA_ttf.ttf` (배달의민족 주아체) | 없음 |
| `--sub-color` | 자막 글자 색 (RGB) | `FFE400` 노란색 |
| `--font-size` | 자막 글자 크기 | 140 |
| `--no-cta` | 끝부분 '전체 이야기 보러 가기' 문구와 움직이는 화살표 끄기 | (켜짐) |
| `--cta-x` / `--cta-y` | 화살표 끝이 가리킬 위치 (1080×1920 기준). Shorts의 '관련 동영상' 링크 자리에 맞춰 조정 | 150 / 1560 |
| `--cta-text` / `--cta-seconds` | 화살표 위 문구 / 끝에서 몇 초 동안 보일지 | 전체 이야기 보러 가기 / 6 |
| `--sub-pos` | 자막 위치: `center` 화면 정중앙 / `bottom` 아래쪽 (Shorts 아래쪽은 제목·버튼에 가려짐) | `center` |
| `--sub-y` | `bottom`일 때 자막 높이 (화면 아래에서 px, 1920 기준, 클수록 위로) | face 560 / fit 620 |
| `--words-per-line` | 자막 한 번에 표시할 단어 수 | 2 |
| `--no-subs` | 자막 없이 출력 | |
| `--layout` | `face`: 장면마다 인물 따라 크롭 / `fit`: 원본 전체 + 흐린 배경 + 상단 제목 / `center`: 가운데 크롭 | `face` |
| `--no-title` | `fit`에서 상단 제목 숨기기 | |
| `--reuse-clips` | 이전에 고른 구간 그대로 다시 렌더링 (설정만 바꿔 다시 뽑을 때) | |
| `--dry-run` | 구간 선정까지만 (렌더링·업로드 안 함) | |
| `--upload` | 추출 후 YouTube 업로드 | |
| `--privacy` | `private` / `unlisted` / `public` | `private` |
| `--schedule` | 첫 클립 예약 공개 시각 (내 컴퓨터 시간 기준) | 없음 |
| `--interval` | 예약 공개 간격(시간) | 24 |
| `--footer` | 설명란 문구 (풀영상 링크 등) | 없음 |
| `--watch DIR` | 폴더 감시 모드 | |
| `--poll` | 감시 간격(초) | 30 |
| `-o, --out` | 출력 폴더 | `output` |
| `--model` | 구간 선정용 Claude 모델 | `claude-opus-5-5` |

## 팁

- **속도**: NVIDIA GPU가 있으면 Whisper가 자동으로 GPU를 씁니다. CPU만 있으면 1시간 영상에 `small` 모델 기준 수십 분 걸릴 수 있습니다.
- **비용**: 1시간 영상 자막은 대략 15~20k 토큰이라 Claude 호출 한 번에 몇 센트 수준입니다. YouTube API는 무료입니다.
- **크롭**: 장면(컷)이 바뀔 때마다 가장 큰 얼굴을 찾아 그 위치로 자릅니다 (YuNet 얼굴 인식, 첫 실행 시 자동 다운로드). 두 사람이 한 화면에 나오거나 그림·애니메이션이라 얼굴을 못 찾으면 `--layout fit`이 낫습니다.
- **처음엔 `--privacy private`로** 몇 번 돌려보고, 고르는 구간이 마음에 들면 예약 공개로 넘어가는 걸 추천합니다.
- YouTube URL에서 바로 받고 싶다면 `pip install yt-dlp` 후 파일 대신 URL을 넣으면 됩니다.
