# assets/ - 폰트 폴더

합성 단계(타이틀/자막)에 쓰는 한글 폰트를 여기에 넣습니다.

| 파일 | 용도 |
|---|---|
| `Pretendard-Black.ttf` (또는 `.otf`) | 상단 노란 타이틀 |
| `Pretendard-Bold.ttf` (또는 `.otf`) | 하단 자막 |

- Pretendard 는 https://github.com/orioncactus/pretendard 릴리스에서 받을 수 있습니다 (OFL 라이선스).
- 폰트가 없으면 자동으로 이 폴더의 다른 폰트 → 시스템 한글 폰트(맑은 고딕 / Apple SD Gothic Neo / 나눔 / Noto CJK)로 대체되며, 합성 로그에 알림이 표시됩니다.
- 폰트 파일은 `.gitignore` 대상입니다(저장소에 올라가지 않음).
