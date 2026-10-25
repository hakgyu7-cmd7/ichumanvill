# 롱폼 → 숏폼 자동 추출기

YouTube 링크(또는 로컬 영상)를 넣으면 숏폼으로 쓸 만한 구간을 AI가 골라서 **9:16 세로 영상 + 자막**으로 뽑아줍니다.

```
yt-dlp 다운로드 → Whisper 받아쓰기 → Claude가 하이라이트 선정 → 얼굴 기준 세로 크롭 → ffmpeg로 자막 입혀 렌더링
```

## 설치

1. **ffmpeg** 설치
   - Windows: `winget install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Ubuntu: `sudo apt install ffmpeg`
2. Python 3.10 이상에서 다음 명령 실행:
   ```bash
   pip install -r requirements.txt
   ```
3. Claude API 키 설정 ([console.anthropic.com](https://console.anthropic.com)에서 발급)
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."      # Windows PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."
   ```
4. 한글 자막 폰트: 나눔고딕이 기본값입니다. 없다면 설치하거나 `--font "맑은 고딕"`처럼 지정하세요.

## 사용법

```bash
# 기본: 숏폼 5개, 20~59초
python shorts.py "https://www.youtube.com/watch?v=XXXX"

# 3개만, 30~45초, 한국어, 웃긴 장면 위주로
python shorts.py "https://youtu.be/XXXX" -n 3 --min 30 --max 45 --lang ko --prompt "웃긴 장면 위주로"

# 로컬 파일
python shorts.py 내영상.mp4

# 렌더링 없이 어떤 구간이 뽑히는지만 확인
python shorts.py "https://youtu.be/XXXX" --dry-run
```

결과는 `output/` 폴더에 생깁니다.

| 파일 | 내용 |
|---|---|
| `short_01_제목.mp4` … | 1080×1920 세로 숏폼 (바이럴 점수 높은 순) |
| `clips.json` | 구간별 시작·끝 시각, 제목, 훅, 선정 이유, 점수, 해시태그 |
| `transcript.json` | 받아쓰기 캐시 (같은 영상을 다시 돌리면 받아쓰기를 건너뜀) |

## 주요 옵션

| 옵션 | 설명 | 기본값 |
|---|---|---|
| `-n, --clips` | 뽑을 숏폼 개수 | 5 |
| `--min / --max` | 클립 길이(초) | 20 / 59 |
| `--lang` | 음성 언어 (`ko`, `en` …) | 자동 감지 |
| `--whisper-model` | `tiny` `base` `small` `medium` `large-v3` (클수록 정확하지만 느림) | `small` |
| `--prompt` | 구간 선정 추가 지시 | 없음 |
| `--font` | 자막 폰트 | `NanumGothic` |
| `--words-per-line` | 자막 한 줄 단어 수 | 3 |
| `--no-subs` | 자막 없이 출력 | |
| `--no-face` | 얼굴 추적 없이 가운데 크롭 | |
| `--dry-run` | 구간 선정까지만 실행 | |
| `--model` | 구간 선정용 Claude 모델 | `claude-opus-5-5` |
| `-o, --out` | 출력 폴더 | `output` |

## 팁

- **속도**: NVIDIA GPU가 있으면 Whisper가 자동으로 GPU를 씁니다. CPU만 있으면 1시간 영상에 `small` 모델 기준 수십 분 걸릴 수 있어요. 급하면 `--whisper-model base`를 쓰세요.
- **비용**: 1시간 영상 자막은 대략 15~20k 토큰이라 Claude 호출 한 번에 몇 센트 수준입니다.
- **크롭**: 클립마다 가장 큰 얼굴의 평균 위치로 화면을 고정해서 자릅니다. 두 사람이 번갈아 말하는 대담 영상은 한 명이 잘릴 수 있으니 `--no-face`도 비교해보세요.
- **저작권**: 본인 영상이나 사용 허락을 받은 영상에만 쓰세요.
