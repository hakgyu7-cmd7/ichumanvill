# 시니어 수면 옛날이야기 채널 운영 도구

Claude Code에서 쓰는 스킬 5개와, 숏폼 추출기(`shorts-generator/`)로 이루어져 있습니다.

## 처음 한 번: 채널 프로필 채우기
`youtube/channel.md`를 열어 `[ ]` 칸을 채웁니다. 모든 스킬이 이 파일을 기준으로 대본, 제목, 답글을 씁니다.
직접 채우기 어려우면 Claude에게 "channel.md 채우는 거 도와줘"라고 하면 질문하면서 같이 채워줍니다.

## 스킬 사용법
이 저장소를 연 Claude Code에서 아래처럼 말하거나 `/스킬이름`을 입력합니다.

| 하고 싶은 일 | 이렇게 말하기 | 스킬 |
|---|---|---|
| 대본 쓰기 | "장터에서 쫓겨난 과부 이야기로 40분짜리 대본 써줘" | `/sleep-script` |
| 제목·썸네일 | "이 대본으로 제목이랑 썸네일 문구 지어줘" | `/sleep-package` |
| 시청 지속 분석 | "이 유지율 CSV 분석해줘 (영상 길이 3:02:15)" + 파일 | `/sleep-retention` |
| 경쟁 채널 분석·소재 추천 | "이 채널들에서 터진 영상 찾고 다음 소재 추천해줘" + 채널 주소 | `/sleep-outliers` |
| 댓글 답글 | "이 댓글들 답글 써줘" + 댓글 붙여넣기 | `/sleep-comment` |

### 한 편을 만드는 흐름
1. `/sleep-outliers` → 요즘 잘 되는 소재 확인, 소재 고르기
2. `/sleep-script` → 대본과 그림 장면 목록
3. AI 음성과 그림으로 영상 제작 (직접)
4. `/sleep-package` → 제목, 썸네일 문구, 설명란
5. 업로드 후 `shorts_upload.bat`에 롱폼 영상을 끌어다 놓기 → 숏폼 5개 자동 추출·업로드
6. 일주일 뒤 `/sleep-retention`과 `/sleep-comment`로 반응 확인 → 다음 영상에 반영

## 도구만 따로 쓰기 (Python)
```bash
python .claude/skills/sleep-package/title_ko.py --title "제목" --thumb "썸네일 문구"
python .claude/skills/sleep-retention/retention_sleep.py retention.csv --duration 3:02:15
python .claude/skills/sleep-outliers/outliers.py collect channels.txt -o data.json
python .claude/skills/sleep-outliers/outliers.py rank data.json
```
`outliers.py collect`는 yt-dlp가 필요합니다 (`pip install yt-dlp`). YouTube가 클라우드 서버를 막는 경우가 많아 **내 PC에서** 실행하세요.

## 참고
- 스킬은 `Jakeschincariol/youtube-agent-skill`(MIT)의 구성을 참고해, 한국어 수면 채널에 맞게 새로 썼습니다. 원본의 점수 도구는 영어 전용이라 한국어에서 맞지 않습니다.
- 스킬은 글을 써줄 뿐 업로드하지 않습니다. 업로드는 숏폼 추출기의 `--upload`만 합니다.
