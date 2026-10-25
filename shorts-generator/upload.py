#!/usr/bin/env python3
"""shorts.py가 만든 숏폼을 YouTube에 업로드한다.

처음 실행하면 브라우저가 열리고 Google 계정으로 로그인/허용하면 token.json이 저장되어
다음부터는 자동으로 업로드된다. (client_secret.json 준비 방법은 README 참고)

사용 예:
  python upload.py output/                         # output/clips.json의 클립을 비공개로 업로드
  python upload.py output/ --privacy public
  python upload.py output/ --schedule 2026-11-01T18:00 --interval 24   # 하루 1개씩 예약 공개
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
HERE = Path(__file__).resolve().parent


def get_service(client_secret: Path, token: Path):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_file(str(token), SCOPES) if token.exists() else None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid:
        if not client_secret.exists():
            sys.exit(f"{client_secret} 파일이 없습니다. README의 'YouTube 업로드 설정'을 따라 만들어주세요.")
        flow = InstalledAppFlow.from_client_secrets_file(str(client_secret), SCOPES)
        creds = flow.run_local_server(port=0)
    token.write_text(creds.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=creds)


def build_body(clip: dict, privacy: str, publish_at: datetime | None, footer: str | None) -> dict:
    tags = [t.lstrip("#") for t in clip.get("hashtags", [])]
    title = clip["title"]
    if "#shorts" not in title.lower():
        title = f"{title} #Shorts"
    description = " ".join(f"#{t}" for t in tags + ["Shorts"])
    if footer:
        description = f"{footer}\n\n{description}"

    status = {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}
    if publish_at:  # 예약 공개는 private 상태로 올리고 publishAt을 지정해야 함
        status["privacyStatus"] = "private"
        status["publishAt"] = publish_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:30],
            "categoryId": "22",  # People & Blogs
        },
        "status": status,
    }


def upload_clips(out_dir: Path, privacy: str = "private", schedule: str | None = None,
                 interval_hours: float = 24, footer: str | None = None,
                 client_secret: Path = HERE / "client_secret.json", token: Path = HERE / "token.json") -> None:
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    clips_file = out_dir / "clips.json"
    clips = json.loads(clips_file.read_text(encoding="utf-8"))
    pending = [c for c in clips if c.get("file") and not c.get("youtube_id")]
    if not pending:
        print("업로드할 새 클립이 없습니다.")
        return

    youtube = get_service(client_secret, token)
    first = datetime.fromisoformat(schedule).astimezone() if schedule else None

    print(f"[업로드] {len(pending)}개 → YouTube ({'예약 공개' if first else privacy})")
    for i, clip in enumerate(pending):
        publish_at = first + timedelta(hours=interval_hours * i) if first else None
        body = build_body(clip, privacy, publish_at, footer)
        media = MediaFileUpload(str(out_dir / clip["file"]), mimetype="video/mp4", resumable=True, chunksize=8 * 1024 * 1024)
        try:
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
            response = None
            while response is None:
                progress, response = request.next_chunk()
                if progress:
                    print(f"      {clip['file']} {progress.progress() * 100:.0f}%", end="\r")
        except HttpError as e:
            if e.resp.status == 403 and b"quota" in e.content:
                print("\n      ⚠ 오늘 API 할당량을 다 썼습니다. 내일 같은 명령을 다시 실행하면 남은 것부터 이어서 올립니다.")
                break
            raise

        clip["youtube_id"] = response["id"]
        if publish_at:
            clip["publish_at"] = publish_at.isoformat()
        clips_file.write_text(json.dumps(clips, ensure_ascii=False, indent=2), encoding="utf-8")
        when = f" (공개 예정 {publish_at:%m/%d %H:%M})" if publish_at else ""
        print(f"      ✓ https://youtube.com/shorts/{response['id']}{when}")


def main() -> None:
    p = argparse.ArgumentParser(description="숏폼 클립 YouTube 업로드")
    p.add_argument("out_dir", type=Path, help="shorts.py 출력 폴더 (clips.json이 있는 곳)")
    add_upload_args(p)
    args = p.parse_args()
    upload_clips(args.out_dir, args.privacy, args.schedule, args.interval, args.footer)


def add_upload_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private",
                   help="공개 범위 (기본: private — 확인 후 Studio에서 공개 권장)")
    p.add_argument("--schedule", default=None,
                   help="첫 클립 예약 공개 시각, 내 컴퓨터 시간 기준 (예: 2026-11-01T18:00)")
    p.add_argument("--interval", type=float, default=24, help="예약 공개 간격(시간) (기본: 24)")
    p.add_argument("--footer", default=None, help="설명란에 넣을 문구 (예: '풀영상 👉 https://youtu.be/...')")


if __name__ == "__main__":
    main()
