/* 자동 생성 파일: python prompt_engine.py sync-config  (config.json / samples / data 를 수정한 뒤 실행) */
window.PIPELINE_CONFIG = {
 "version": "3.0",
 "spec": {
  "total_seconds": 45,
  "scenes": 6,
  "scene_seconds": 7.5,
  "cut_seconds": 2.5,
  "cuts_per_scene": 3,
  "speed": 1.2,
  "crop_scale": 1.06,
  "safe_zone_pct": 70,
  "margin_pct": 15
 },
 "default_category": "general",
 "suffix": {
  "zero_text": "--no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16",
  "safe_margin": "subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up",
  "zero_text_core": "--no text, letters, words, typography, subtitles, font, signage, watermark",
  "adult": "all characters are clearly adult"
 },
 "cut_connectors": [
  "Start from Frame 1.",
  "Instant hard cut to the Frame 2 view.",
  "Snappy whip-pan transition to a brand-new third angle."
 ],
 "omni": {
  "header": "A continuous 7.5-second vertical 9:16 clip with snappy transitions every 2.5 seconds, consistent visual style",
  "header_zero": ", pure visual storytelling without any letters or text",
  "polish_base": "no morphing artifacts between cuts",
  "polish_safe": "subject stays centered in the safe zone",
  "polish_zero": "no text, letters or typography"
 },
 "time_labels": [
  "[0.0s - 2.5s]",
  "[2.5s - 5.0s]",
  "[5.0s - 7.5s]"
 ],
 "blueprint_keys": [
  [
   "hook",
   "훅"
  ],
  [
   "problem",
   "문제 심화"
  ],
  [
   "mechanism",
   "원인·메커니즘"
  ],
  [
   "climax",
   "클라이맥스"
  ],
  [
   "punchline",
   "반전 펀치라인"
  ],
  [
   "action",
   "행동 유도"
  ]
 ],
 "scene_roles": [
  {
   "id": 1,
   "time": "0.0~7.5s",
   "role": "충격적 훅 (Hook)",
   "cuts": "[0-2.5s] 미디엄 줌 → [2.5-5s] 로우앵글 → [5-7.5s] 휩팬"
  },
  {
   "id": 2,
   "time": "7.5~15.0s",
   "role": "문제 심화 / 기존 대안 실패",
   "cuts": "[0-2.5s] 탑다운 POV → [2.5-5s] 하드 컷 → [5-7.5s] 미디엄 트래킹"
  },
  {
   "id": 3,
   "time": "15.0~22.5s",
   "role": "원인 해부 / 솔루션 등장",
   "cuts": "[0-2.5s] 매크로 클로즈업(여백 확보) → [2.5-5s] 앵글 틸트 → [5-7.5s] 스냅 줌"
  },
  {
   "id": 4,
   "time": "22.5~30.0s",
   "role": "기능 검증 / 핵심 카타르시스",
   "cuts": "[0-2.5s] 고속 슬로모 → [2.5-5s] 충격 진동 컷 → [5-7.5s] 진짜 풀백"
  },
  {
   "id": 5,
   "time": "30.0~37.5s",
   "role": "반전 펀치라인 / 극적 대비",
   "cuts": "[0-2.5s] 더치 앵글 → [2.5-5s] 시선 급반전 → [5-7.5s] 와이드 쇼크"
  },
  {
   "id": 6,
   "time": "37.5~45.0s",
   "role": "결론 / 행동 유도 (CTA)",
   "cuts": "[0-2.5s] 제4의 벽 응시 → [2.5-5s] 포인트 컷 → [5-7.5s] 블랙아웃"
  }
 ],
 "camera_library": [
  "초반 컷: Medium Close-up(안전 마진 확보) / Dutch Angle + Rapid push-in zoom, Macro focal switch",
  "중반 컷: Low-angle Tilt / Top-down POV + Sudden hard cut, Snappy whip-pan, Dynamic shake",
  "후반 컷: Tracking Medium Shot / Dutch Tilt + Fast tracking pull-back, Sharp snap-zoom to freeze"
 ],
 "styles": {
  "diorama": {
   "number": 7,
   "name": "고정밀 피규어 & 디오라마",
   "name_en": "Detailed Figure & Diorama",
   "default": true,
   "desc": "레진 피규어 질감, 틸트시프트 접사, 미니어처 디오라마 스케일",
   "anchor": "Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography",
   "video_feel": "Miniature stop-motion feel, precise macro depth of field, subtle plastic reflections, flawless scale consistency",
   "recommended": "B급 병맛, 쇼핑/아이템 쇼츠, 가상 시뮬레이션",
   "icon": "🧸"
  },
  "cinematic": {
   "number": 1,
   "name": "시네마틱 실사 영화",
   "name_en": "Cinematic Live-Action",
   "desc": "35mm 렌즈, 자연광, 실사 영화·다큐 질감",
   "anchor": "Hyper-realistic cinematic film photography, 35mm lens, natural dynamic lighting, realistic skin and material textures, medium pulled-back framing",
   "video_feel": "Cinematic live-action movie aesthetic, natural camera motion blur, 24fps filmic shutter, consistent cinematic lighting across cuts",
   "recommended": "재난 시뮬레이션, 역사 비화, 생활 꿀팁",
   "icon": "🎬"
  },
  "claymation": {
   "number": 2,
   "name": "스톱모션 클레이메이션",
   "name_en": "Handmade Claymation",
   "desc": "수제 점토 질감, 지문 자국, 스톱모션 프레임",
   "anchor": "Handmade stop-motion claymation, detailed plasticine clay texture, fingerprint marks, miniature studio softbox lighting",
   "video_feel": "Authentic stop-motion frame jitter, tactile clay texture dynamics, fluid miniature animation",
   "recommended": "B급 병맛, 쇼핑 꿀템, 일상 공감",
   "icon": "🧱"
  },
  "hyperreal_3d": {
   "number": 3,
   "name": "하이퍼리얼 3D CGI",
   "name_en": "Hyper-Realistic 3D CGI",
   "desc": "언리얼 엔진 5 렌더, 레이트레이싱 반사광",
   "anchor": "Ultra-detailed 3D CGI render, Unreal Engine 5 look, Octane Render, ray-tracing, crisp reflections, clean studio rim light",
   "video_feel": "Flawless smooth 3D camera pan, photorealistic physics, clean reflection tracking",
   "recommended": "공학/기술, IT 쇼핑, 과학 시뮬레이션",
   "icon": "🧊"
  },
  "vintage_1930": {
   "number": 4,
   "name": "1930s 빈티지 흑백 필름",
   "name_en": "Vintage Monochrome",
   "desc": "모노크롬, 필름 그레인, 아카이브 다큐 질감",
   "anchor": "1930s authentic historical black-and-white film, monochrome, dramatic chiaroscuro harsh shadows, fine film grain",
   "video_feel": "Subtle vintage projector flicker, authentic archival documentary motion, high-contrast shadows",
   "recommended": "역사 비화, 미해결 미스터리",
   "icon": "🎞️"
  },
  "macro_medical": {
   "number": 5,
   "name": "과학 메디컬 매크로",
   "name_en": "Microscopic Scientific",
   "desc": "전자현미경 느낌, 투시 단면, 생체 발광",
   "anchor": "Microscopic macro scientific photography, scanning electron microscope aesthetic, translucent bioluminescence, sharp focal depth",
   "video_feel": "Smooth microscopic focus-pull, floating particle dynamics, fluid biological motion",
   "recommended": "인체/뇌과학, 피부/뷰티 쇼핑, 기괴한 생태계",
   "icon": "🔬"
  },
  "minimal_ad": {
   "number": 6,
   "name": "미니멀 상업 광고",
   "name_en": "Clean Minimalist Ad",
   "desc": "파스텔 대리석, 소프트 스튜디오 조명, 플랫레이",
   "anchor": "Sleek minimalist commercial, clean pastel marble backdrop, bright aesthetic studio daylight, elegant flat-lay",
   "video_feel": "Smooth high-end commercial tracking shot, ultra-clean reflections, crisp elegant motion",
   "recommended": "인테리어/살림 꿀템, 여성 뷰티, 패션 쇼핑",
   "icon": "🪞"
  }
 },
 "categories": {
  "general": {
   "num": 0,
   "name": "자유 주제 (레퍼런스 구조 재구성)",
   "name_en": "Free Topic / Reference Remake",
   "hook": "시선을 1초 만에 붙잡는 충격/의문/반전 선언 (레퍼런스의 훅 문법 우선)",
   "problem": "상황과 문제를 구체적으로 심화해 궁금증을 키움",
   "mechanism": "핵심 원리·원인·전개를 한 단계씩 보여줌 (레퍼런스의 전개 리듬 우선)",
   "climax": "가장 강렬한 장면 또는 결정적 순간 (절정)",
   "punchline": "예상을 뒤집는 반전 또는 서늘한 한마디",
   "action": "마무리 한 줄 + 댓글/공유를 부르는 질문",
   "flow": "[레퍼런스 훅 구조] → [문제 심화] → [원리/전개] → [절정] → [반전 펀치라인]",
   "psychology": "레퍼런스가 떡상한 이유(후킹·시청 유지·반전)를 그대로 계승",
   "sourcing": "떡상 영상(V/S 10배 이상), 레딧, 위키/다큐 등 무엇이든",
   "styles": [
    "diorama",
    "cinematic",
    "hyperreal_3d"
   ]
  },
  "shopping": {
   "num": 8,
   "name": "소비 심리 저격 쇼핑 (꿀템)",
   "name_en": "Lifehack Products",
   "shopping": true,
   "hook": "기존 사용법의 충격적 낭비/불편/분노 지적",
   "problem": "기존 방식 또는 저가 제품의 치명적 결함 증명",
   "mechanism": "핵심 혁신 아이템 등장 및 스펙 조명",
   "climax": "극적인 비포&애프터 및 카타르시스 기능 검증",
   "punchline": "동급 대비 가격 파괴 및 가성비 체감",
   "action": "재고 경고 및 쇼핑 태그·고정 댓글 유도",
   "flow": "[충격 결함/불편] → [기존 대안 실패] → [아이템 등장·기능 시각화] → [실사용 체감] → [가격/구매 팁]",
   "psychology": "\"돈 낭비 막아줌\" + \"나만 몰랐던 꿀템\" (손실 회피 심리)",
   "sourcing": "알리/아마존 신제품 랭킹, 크라우드펀딩 사이트, 쿠팡 베스트, 틱톡 크리에이티브 센터",
   "styles": [
    "diorama",
    "minimal_ad",
    "hyperreal_3d"
   ]
  },
  "history": {
   "num": 1,
   "name": "역발상 역사 & 인물 비화",
   "name_en": "Historical Reversals",
   "hook": "교과서 상식을 정면으로 부수는 인물/사건 충격 훅",
   "problem": "역사 기록 이면에 숨겨진 충격적인 진실",
   "mechanism": "사건을 파국 또는 반전으로 이끈 결정적 계기",
   "climax": "믿기 힘든 역사적 아이러니 폭로",
   "punchline": "현재의 우리에게 던지는 서늘한 풍자",
   "action": "시청자의 판단을 묻는 질문 댓글 유도",
   "flow": "[위인의 숨겨진 악행/비참한 진실] → [교과서 왜곡 지적] → [결정적 사건 전말] → [허를 찌르는 교훈]",
   "psychology": "권위 파괴, 도덕적 충격, 댓글 논쟁 유도",
   "sourcing": "야사, 위키백과 미스터리, 해외 역사 다큐",
   "styles": [
    "vintage_1930",
    "cinematic"
   ]
  },
  "disaster": {
   "num": 3,
   "name": "'만약에' 극한 재난 시뮬레이션",
   "name_en": "What-If Extreme",
   "hook": "일상적 물리 법칙의 즉각적 붕괴 선언",
   "problem": "초 단위로 이어지는 연쇄 물리 파괴",
   "mechanism": "수치와 시뮬레이션으로 보는 파국 메커니즘",
   "climax": "시각적으로 압도적인 거대 재앙의 정점",
   "punchline": "생존자 0명에 수렴하는 충격적 2차 반전",
   "action": "당신이라면 어디로 도망칠 것인가 댓글 질문",
   "flow": "[\"내일 당장 지구 자전이 멈춘다면?\"] → [1초 뒤 충격] → [생태계 붕괴 단계] → [인류 생존 가능성]",
   "psychology": "극단적 호기심, CG/모션 시각 충격",
   "sourcing": "가상 시나리오, 물리 계산 논문, 재난 시뮬",
   "styles": [
    "cinematic",
    "diorama"
   ]
  },
  "bgrade": {
   "num": 7,
   "name": "현대인 공감 B급 병맛 시트콤",
   "name_en": "Relatable Absurdism",
   "hook": "기괴하거나 지나치게 진지한 엉뚱한 의문 제시",
   "problem": "말도 안 되는 억지 논리를 극도로 진지하게 전개",
   "mechanism": "점점 꼬여가는 뇌내 회로와 갈등",
   "climax": "상상을 초월하는 황당한 파국",
   "punchline": "현실과 타협하는 킹받는 결말",
   "action": "도파민 폭발 댓글 유도 질문",
   "flow": "[\"월요일 아침 출근 3초 전 뇌내 상황\"] → [장기들의 파업 및 비상회의] → [카페인 투입 후 발작] → [결국 퇴사 상상으로 종료]",
   "psychology": "극도의 공감, 친구 태그, 킹받는 중독성",
   "sourcing": "직장인/일상 커뮤니티 밈, SNS 릴스 챌린지",
   "styles": [
    "diorama",
    "claymation"
   ]
  },
  "body_brain": {
   "num": 11,
   "name": "인체 공학 & 뇌과학 해부",
   "name_en": "Body & Brain Anatomy",
   "hook": "매일 겪는 신체 증상에 대한 충격적 반전 질문",
   "problem": "세포/신경/호르몬 단위의 미세 메커니즘 해부",
   "mechanism": "진화론적으로 뇌가 그렇게 설계된 진짜 이유",
   "climax": "신체 내부에서 일어나는 폭발적 연쇄 반응",
   "punchline": "인간 신체의 경이로운 생존 비밀",
   "action": "즉각적인 신체 바이오해킹 행동 팁 제공",
   "flow": "[일상적 신체 증상 훅] → [현미경 메커니즘 해부] → [진화론적·신경학적 원인] → [행동 지침]",
   "psychology": "\"내 몸에 이런 일이?\" (경외감과 자기 관련성)",
   "sourcing": "의학 논문 초록, 뇌과학 유튜브, 해외 헬스 매체",
   "styles": [
    "macro_medical",
    "hyperreal_3d"
   ]
  },
  "architecture": {
   "num": 12,
   "name": "건축 & 공간 역학 미스터리",
   "name_en": "Architecture & Structure",
   "hook": "불가능해 보이는 구조물/공간의 붕괴 미스터리 조명",
   "problem": "외력과 하중이 부딪히는 물리적 모순 시각화",
   "mechanism": "설계자가 숨겨둔 트러스/댐퍼/재료 역학적 비책",
   "climax": "극한의 하중을 버텨내는 공학적 카타르시스",
   "punchline": "공간 설계의 숨겨진 심리학적 의도",
   "action": "공간의 비밀에 대한 질문 댓글 유도",
   "flow": "[미스터리한 공간/구조 훅] → [설계적 결함 vs 의도] → [물리/하중 메커니즘] → [숨겨진 비밀 공개]",
   "psychology": "\"이 건물/다리가 왜 안 무너질까?\" (지적 호기심)",
   "sourcing": "건축 다큐, 공학 유튜브, 토목 사례집",
   "styles": [
    "hyperreal_3d",
    "diorama"
   ]
  },
  "deepsea_space": {
   "num": 2,
   "name": "극한 심해 / 우주 미스터리",
   "name_en": "Cosmic & Deep Sea",
   "hook": "익숙한 공포(암흑/수압)를 정면으로 던지는 첫 장면",
   "problem": "실제 발견된 기괴한 생물/천체의 정체",
   "mechanism": "극한 환경이 만들어낸 과학적 불가사의 원리",
   "climax": "인간의 무력함을 강조하는 스케일 비교",
   "punchline": "아직도 밝혀지지 않은 서늘한 사실",
   "action": "어디까지 가봤을지 상상을 묻는 댓글 유도",
   "flow": "[익숙한 공포(암흑/수압)] → [실제 발견된 기괴한 생물/천체] → [과학적 불가사의] → [인간의 무력함 강조]",
   "psychology": "코스믹 호러, 시각적 압도감, 경외감",
   "sourcing": "NASA/NOAA 공개 데이터, 천문학 프리프린트",
   "styles": [
    "cinematic",
    "hyperreal_3d"
   ]
  },
  "psychology": {
   "num": 4,
   "name": "인간 심리 & 행동경제학 치트키",
   "name_en": "Dark Psychology & Bias",
   "hook": "\"상대방이 거짓말할 때 0.1초 반응\" 같은 즉각 써먹는 훅",
   "problem": "심리학 실험을 재현하는 일상 장면",
   "mechanism": "무의식을 조종하는 인지 편향의 원리",
   "climax": "실험 결과가 드러나는 소름 돋는 순간",
   "punchline": "나도 모르게 당하고 있었다는 자각",
   "action": "즉각 실전에 적용할 한 줄 행동 팁과 공유 유도",
   "flow": "[\"상대방이 거짓말할 때 0.1초 반응\"] → [심리학 실험 재현] → [무의식 조종 원리] → [즉각 실전 적용법]",
   "psychology": "자기 투영, 저장 및 공유율(Share) 극대화",
   "sourcing": "심리학 학술지, FBI 심문 기술, 마케팅 서적",
   "styles": [
    "diorama",
    "minimal_ad"
   ]
  },
  "bizarre_nature": {
   "num": 5,
   "name": "기괴한 생태계 / 잔혹 동화",
   "name_en": "Bizarre Nature",
   "hook": "\"이 곤충은 뇌를 조종당합니다\" 같은 기이한 선언",
   "problem": "기생충·침입 과정의 단계적 묘사",
   "mechanism": "숙주의 기이한 행동이 만들어지는 원리",
   "climax": "자연의 잔혹한 룰이 완성되는 절정",
   "punchline": "인간 사회와 겹쳐 보이는 서늘한 비유",
   "action": "이 중 가장 소름 돋는 생물 투표 댓글 유도",
   "flow": "[\"이 곤충은 뇌를 조종당합니다\"] → [기생충 침투 과정] → [숙주의 기이한 행동] → [자연의 잔혹한 룰]",
   "psychology": "도파민 자극, 기괴함(Uncanny), 끝까지 시청",
   "sourcing": "네이처/사이언스 생태 논문, 내셔널지오그래픽",
   "styles": [
    "macro_medical",
    "cinematic"
   ]
  },
  "extreme_jobs": {
   "num": 6,
   "name": "기상천외한 극한 직업 & 산업",
   "name_en": "Extreme Engineering & Jobs",
   "hook": "\"연봉 3억인데 아무도 안 하는 일\" 같은 호기심 훅",
   "problem": "작업 환경의 치명적 위험",
   "mechanism": "특수 장비 작동 원리와 작업 방식",
   "climax": "아슬아슬한 작업이 완성되는 만족스러운 순간",
   "punchline": "버티는 사람들의 숨은 조건",
   "action": "당신이라면 하겠는가 질문 댓글 유도",
   "flow": "[\"연봉 3억인데 아무도 안 하는 일\"] → [작업 환경의 치명적 위험] → [특수 장비 작동 원리] → [버티는 자들의 조건]",
   "psychology": "만족감(Satisfying), 직업적 호기심",
   "sourcing": "해외 르포, 중장비/특수 산업 커뮤니티",
   "styles": [
    "cinematic",
    "hyperreal_3d"
   ]
  },
  "mystery": {
   "num": 9,
   "name": "미해결 사건 & 미스터리 기행",
   "name_en": "Unsolved Paradox",
   "hook": "\"사진 1장 남기고 증발한 탐험대\" 같은 사건 선언",
   "problem": "현장에서 발견된 기이한 단서",
   "mechanism": "3가지 음모론/가설의 대립",
   "climax": "가장 유력한 가설이 소름 돋게 맞아떨어지는 지점",
   "punchline": "끝내 열리지 않은 결말",
   "action": "당신의 가설을 묻는 댓글 토론 유도",
   "flow": "[\"사진 1장 남기고 증발한 탐험대\"] → [현장에서 발견된 기이한 단서] → [3가지 음모론 대립] → [소름 돋는 열린 결말]",
   "psychology": "추리 본능 자극, 댓글 토론 과열",
   "sourcing": "레딧(UnresolvedMysteries), 세계 기네스북",
   "styles": [
    "vintage_1930",
    "cinematic"
   ]
  },
  "near_future": {
   "num": 10,
   "name": "미래 기술 & 사이버펑크 유출",
   "name_en": "Near-Future Tech",
   "hook": "\"2030년 인간의 뇌에 칩이 심어지면?\" 같은 미래 선언",
   "problem": "기술이 작동하는 인터페이스 시각화",
   "mechanism": "예상되는 부작용과 통제 불가 시나리오",
   "climax": "기술이 일상을 잠식하는 압도적 장면",
   "punchline": "찬반 딜레마로 끝나는 서늘한 질문",
   "action": "당신은 찬성 vs 반대 선택 댓글 유도",
   "flow": "[\"2030년 인간의 뇌에 칩이 심어지면?\"] → [기술 작동 인터페이스] → [예상되는 부작용과 통제] → [찬반 딜레마]",
   "psychology": "미래 공포(Technophobia), 기술적 신비감",
   "sourcing": "신기술 특허 문서, 테크 컨퍼런스 발표",
   "styles": [
    "hyperreal_3d",
    "cinematic"
   ]
  }
 },
 "formats": {
  "satisfying_sim": {
   "name": "시각적 만족 카타르시스",
   "name_en": "Ultra-Satisfying Simulation",
   "keywords": "3D Kinetic, Micro-mechanics, Fluid Dynamics",
   "guide": "나레이션은 팩트만 단문으로 치고, 화면은 2~3초마다 물성(금속→유리→점토)이 파괴되거나 정밀 결합하는 비주얼로 배치한다."
  },
  "moral_dilemma": {
   "name": "딜레마 밸런스 게임",
   "name_en": "Moral Dilemmas / Choose Your Fate",
   "keywords": "Interactive Choice, Extreme Morality",
   "guide": "\"당신이라면 A(100억) vs B(수명 20년 연장) 중 무엇을 택하시겠습니까?\" 같은 극단적 선택지를 2~3초 컷으로 대비시키고 마지막은 댓글 투표로 닫는다."
  },
  "timelapse_evolution": {
   "name": "타임랩스 역사/진화",
   "name_en": "Evolution in 30 Seconds",
   "keywords": "1,000 Years Timelapse, Scale of Universe",
   "guide": "100년 전 → 50년 전 → 현재 → 100년 후를 2초 간격 줌아웃과 컷 전환으로 압축한다."
  },
  "unusual_top5": {
   "name": "비공식 통계 / 순위 랭킹",
   "name_en": "Unusual Top 5",
   "keywords": "Shocking Global Stats, Secret Ranks",
   "guide": "전 세계에서 가장 이상한 법, 가장 위험한 도로 등 5위부터 2초 만에 보여주고 1위는 마지막 3초에 공개한다."
  }
 },
 "languages": {
  "ko": {
   "name": "한국어",
   "unit": "chars",
   "min": 320,
   "max": 350,
   "scene_min": 50,
   "scene_max": 58,
   "desc": "한국어 (자연스러운 숏폼 구어체, 1.2배속 발화)",
   "length_rule": "공백 포함 총 320~350자 엄수 (초당 약 7.5자), 씬당 50~58자.",
   "cta": "제품 정보는 하단 쇼핑 태그와 고정 댓글 확인!",
   "cta_markers": [
    "쇼핑 태그",
    "고정 댓글"
   ],
   "count_note": "공백 포함 "
  },
  "en": {
   "name": "English",
   "unit": "words",
   "min": 90,
   "max": 100,
   "scene_min": 14,
   "scene_max": 17,
   "desc": "English (punchy, viral TikTok tone, 1.2x speech)",
   "length_rule": "총 90~100 words (씬당 14~17 words)",
   "cta": "Check the shopping tag below and the pinned comment for product info!",
   "cta_markers": [
    "shopping tag",
    "pinned comment"
   ],
   "count_note": ""
  },
  "ja": {
   "name": "日本語",
   "unit": "chars",
   "min": 300,
   "max": 330,
   "scene_min": 48,
   "scene_max": 56,
   "desc": "日本語 (テンポの良いショート動画口調, 現地化された自然な表現)",
   "length_rule": "공백 제외 총 300~330문자 (씬당 48~56문자)",
   "cta": "商品情報は下のショッピングタグと固定コメントをチェック！",
   "cta_markers": [
    "ショッピングタグ",
    "固定コメント"
   ],
   "count_note": "공백 제외 "
  },
  "zh": {
   "name": "中文",
   "unit": "chars",
   "min": 280,
   "max": 310,
   "scene_min": 44,
   "scene_max": 52,
   "desc": "中文 (快节奏短视频风格, 台湾/全球华语习惯用语)",
   "length_rule": "공백 제외 총 280~310자 (씬당 44~52자)",
   "cta": "商品資訊請看下方購物標籤與置頂留言！",
   "cta_markers": [
    "購物標籤",
    "置頂留言"
   ],
   "count_note": "공백 제외 "
  }
 },
 "models": {
  "default": {
   "name": "Claude Sonnet 5.5",
   "use": "메인 45초 대본 & Omni 1.2 프롬프트 생성 (속도·추론 밸런스, 화풍/글자수 제약 준수)"
  },
  "crossover": {
   "name": "Claude Opus 5.5",
   "use": "합성(크로스오버) 카테고리·고난도 전환 설계, 병맛 펀치라인 정밀 설계"
  },
  "metadata": {
   "name": "Claude Haiku 5.5",
   "use": "다국어(영/일/중) 초월 번역 & 플랫폼별 메타데이터 일괄 추출"
  }
 },
 "platforms": {
  "youtube": {
   "name": "YouTube Shorts",
   "rule": "제목: 후킹 강한 60자 이내 / 설명란: 요약 3~5줄 + 해시태그(#shorts 포함) / 고정댓글: 시청자 반응 유도 질문{{shopping_pin}}"
  },
  "instagram": {
   "name": "Instagram Reels",
   "rule": "제목(첫 줄 후킹 캡션) / 본문: 공감 유도 및 친구 태그 요청 + 해시태그 8~10개 / 고정댓글{{shopping_pin}}"
  },
  "tiktok": {
   "name": "TikTok",
   "rule": "숏 캡션(이모지 포함) + 바이럴 해시태그(#fyp #viral 포함) / 고정댓글{{shopping_pin}}"
  }
 },
 "layout": {
  "width": 1080,
  "height": 1920,
  "top_bar": 240,
  "bottom_bar": 400,
  "bar_color": "000000",
  "title_font": "",
  "title_size": 66,
  "title_color": "FFE500",
  "title_outline": 2,
  "title_outline_color": "000000",
  "title_y": 0,
  "title_chars_per_line": 15,
  "sub_font": "",
  "sub_size": 52,
  "sub_color": "FFFFFF",
  "sub_outline": 0,
  "sub_outline_color": "000000",
  "sub_box": true,
  "sub_box_color": "000000",
  "sub_box_alpha": 0.65,
  "sub_box_border": 14,
  "sub_gap": 8,
  "sub_bottom": 0,
  "sub_bottom_gap": 20,
  "sub_chars_per_line": 18
 },
 "master_template": [
  "# [시스템 지침] 쇼츠 알고리즘 분석가 & 고성능 비주얼 디렉터",
  "당신은 유튜브 쇼츠의 '시청 지속 시간(AVD)'과 '클릭률(CTR)'을 극대화하는 전문가입니다.",
  "{{task_line}}",
  "",
  "## 1. 오디오 및 러닝타임 제약 (엄수)",
  "- 발화 전제: 1.2배속 고속 발화 + 숨소리/무음(Silence) 완전 제거. 총 러닝타임 정확히 45초(43~46초).",
  "- 씬 분할: 정확히 6개 씬(Scene 01~06), 씬당 정확히 7.5초.",
  "- 대본 분량: {{length_rule}}",
  "- 각 씬의 대사는 2.5초 호흡 단위 3개 비트(beats)로 쪼갭니다 (0.0~2.5s / 2.5~5.0s / 5.0~7.5s). 한 비트는 자막 1~2줄에 들어가는 한 호흡 분량으로 씁니다.",
  "- 발화 언어: {{lang_desc}}",
  "",
  "## 2. [CRITICAL] Zero-Text(무문자) 원칙",
  "- 이미지(T2I)·영상(I2V) 프롬프트 어디에도 글자, 단어, 숫자 텍스트, 자막, 간판, 책/폰 화면 속 글, 브랜드 로고를 묘사하지 않습니다. 프롬프트는 영문으로만 쓰고 한글/일문/중문 문자를 넣지 않습니다.",
  "- 문자로 전달할 정보는 '상징적 오브젝트', '빛과 색의 변화', '인물의 표정', '아이콘'으로 시각화합니다.",
  "  · 나쁜 예: Screen showing text 'MAGNITUDE 9.0'",
  "  · 좋은 예: Screen flashing an intense pulsing red hazard icon and glowing warning light, clean UI without text",
  "- '--no text, letters, words...' 같은 네거티브 접미사는 시스템이 자동으로 붙이므로 직접 쓰지 않습니다.",
  "",
  "## 3. [CRITICAL] 워터마크 크롭 대비 화각 후퇴 안전 마진",
  "- 구글 플로우 우측 하단 워터마크를 {{crop_scale}}배 확대 크롭으로 밀어내므로, 극단적 익스트림 클로즈업(Extreme/Tight Close-up)을 쓰지 않습니다.",
  "- 주요 피사체는 화면 중앙 {{safe_pct}}% 구역 안에, 가장자리(특히 우측 하단)에는 {{margin_pct}}% 이상 여백을 둡니다. 'Medium close-up with generous negative space'처럼 한 단계 후퇴한 화각을 씁니다.",
  "- 손/머리/제품 일부가 화면 끝에 걸치는 구도는 피합니다.",
  "",
  "## 3-2. [CRITICAL] Google Flow(Veo) 콘텐츠 정책 안전 (생성 차단 방지)",
  "- 모든 인물·피규어·캐릭터는 명백한 성인으로 설정하고, 외형(appearance)에 반드시 연령을 명시하세요(예: a 30-year-old adult). 성인 신체 비율과 성인 의상을 씁니다.",
  "- child, kid, boy, girl, teen, student, baby 등 미성년으로 읽힐 수 있는 단어와 young, little, cute, childlike, baby-faced 같은 유아적 표현, 귀여움/순수함 강조는 쓰지 않습니다. (장난감/피규어/인형 캐릭터도 같은 규칙입니다.)",
  "- 노골적 노출·선정적 묘사, 유혈·잔혹 묘사, 실존 인물·유명인의 얼굴/이름은 쓰지 않습니다.",
  "",
  "## 4. 비주얼 규격 (방법 B: 씬당 7.5초 단일 클립 내 2.5초 간격 화각 전환)",
  "- 씬마다 frame1(0s 시작 기준 이미지), frame2(2.5s 전환 기준 이미지), cuts 3개(각 2.5초 구간의 카메라 무빙/동작)를 출력합니다.",
  "- frame1/frame2/cuts의 prompt에는 '피사체·구도·행동·조명'만 영문으로 씁니다. 화풍 앵커, 안전 마진 문구, 네거티브 접미사, 'Start from Frame 1' 같은 연결 문구는 시스템이 자동 합성하므로 쓰지 않습니다.",
  "- 한 씬 안에서 컷마다 화각(Scale)과 시점(Angle)이 반드시 달라야 하며, cuts[1]은 frame2의 구도와, cuts[0]은 frame1의 구도와 맞아야 합니다.",
  "- 씬별 추천 컷 리듬:",
  "{{cut_plan}}",
  "- 카메라 키워드 라이브러리:",
  "{{camera_lib}}",
  "",
  "## 5. 화풍 일관성 & 기준 이미지(등장인물·사물)",
  "- 선택된 화풍: {{style_name}}. 화풍 앵커는 시스템이 모든 프레임 프롬프트 앞에 자동 삽입합니다. 분위기가 반전되어도(예: B급 병맛) 만화/애니메이션 등 다른 화풍 키워드를 쓰지 말고, 같은 화풍 안에서 표정 연기와 상황 연출로만 표현합니다.",
  "{{asset_rule}}",
  "",
  "## 6. 스토리 아키텍처 (총 45초 / 6씬)",
  "{{structure}}",
  "{{format_block}}",
  "{{cta_block}}",
  "",
  "## 7. 입력 기획 데이터",
  "- 타깃 소재 / 상품명: {{topic}}",
  "- 카테고리 구성: {{category_line}}",
  "- 벤치마킹 소스: {{source_line}}",
  "{{source_block}}",
  "",
  "## 8. 출력 포맷 (아래 JSON 하나만 ```json 코드블록으로 출력. 설명 문장 금지)",
  "{{schema}}"
 ],
 "schema_template": [
  "```json",
  "{",
  "  \"analysis\": {\"hook_technique\": \"원본(또는 카테고리 뼈대)의 후킹 기법\", \"retention_psychology\": \"시청자 유지 심리 기법\", \"skeleton\": \"차용할 핵심 리듬(구조)\"},",
  "  \"plan\": {\"titles\": [\"후킹 제목 후보 1\", \"후보 2\", \"후보 3\"], \"description\": \"유튜브 설명란\", \"hashtags\": [\"#해시태그\"]},",
  "  \"top_title\": \"상단 노란 타이틀 배너 문구 (15자 내외, 후킹)\",",
  "  \"assets\": [",
  "    {\"id\": \"hero\", \"type\": \"character\", \"name\": \"주인공(한국어 이름)\", \"label\": \"the deadpan PVC man figure\", \"appearance\": \"영문 외형 고정 키워드 (성별·연령·체형·의상·색·재질·특징. 배경/동작/화각 제외)\", \"keywords\": \"남자, 주인공, 그\"},",
  "    {\"id\": \"pot\", \"type\": \"object\", \"name\": \"냄비\", \"label\": \"the silver pot\", \"appearance\": \"...\", \"keywords\": \"냄비, 솥\"}",
  "  ],",
  "  \"scenes\": [",
  "    {",
  "      \"id\": 1,",
  "      \"beats\": [\"[0.0~2.5s] 대사\", \"[2.5~5.0s] 대사\", \"[5.0~7.5s] 대사\"],",
  "      \"refs\": [\"hero\", \"pot\"],",
  "      \"frame1\": \"영문: 0s 시작 기준 이미지 묘사 (피사체·구도·조명만)\",",
  "      \"frame2\": \"영문: 2.5s 전환 기준 이미지 묘사 (frame1과 다른 화각)\",",
  "      \"cuts\": [",
  "        {\"type\": \"Medium Close-up\", \"prompt\": \"영문: 0.0~2.5s 카메라 무빙/동작\"},",
  "        {\"type\": \"Low-angle Tilt\", \"prompt\": \"영문: 2.5~5.0s 카메라 무빙/동작\"},",
  "        {\"type\": \"Tracking Medium Shot\", \"prompt\": \"영문: 5.0~7.5s 카메라 무빙/동작\"}",
  "      ]",
  "    }",
  "  ]",
  "}",
  "```",
  "- scenes는 정확히 6개(id 1~6), 각 씬의 beats는 정확히 3개입니다. beats 문자열 앞의 [시간] 표기는 생략해도 됩니다.",
  "- assets 는 2개 이상의 씬에 등장하거나 스토리 핵심인 인물·사물·장소만 정의하고, 각 씬의 refs 에는 그 씬에 등장하는 asset id 를 넣습니다(없으면 빈 배열). frame1/frame2/cuts 에서는 asset 의 외형을 다시 설명하지 말고 label 로만 지칭합니다.",
  "- 대사(beats)는 {{lang_name}}로, 나머지 모든 prompt/type/label/appearance는 영문으로만 작성합니다."
 ],
 "metadata_template": [
  "# [메타데이터 생성 지침] 숏폼 다국어 로컬라이징 & 플랫폼 최적화",
  "아래 [확정 대본]을 바탕으로 요청한 언어와 플랫폼별 메타데이터를 생성하세요.",
  "- 직역하지 말고, 해당 문화권의 밈과 뉘앙스에 맞는 초월 번역(Transcreation)으로 작성합니다.",
  "- 카테고리: {{category_line}} / 소재: {{topic}}",
  "- 대상 언어: {{languages}}",
  "- 플랫폼별 규칙:",
  "{{platform_rules}}",
  "{{shopping_note}}",
  "",
  "## 확정 대본 (한국어 기준)",
  "{{script}}",
  "",
  "## 출력 포맷 (JSON 하나만 ```json 코드블록으로, 설명 금지)",
  "```json",
  "{ \"ko\": { \"youtube\": {\"title\": \"\", \"caption\": \"\", \"pinned\": \"\"}, \"instagram\": {\"title\": \"\", \"caption\": \"\", \"pinned\": \"\"}, \"tiktok\": {\"title\": \"\", \"caption\": \"\", \"pinned\": \"\"} }, \"en\": { ... 동일 구조 ... } }",
  "```",
  "- 요청한 언어 키만 포함합니다. caption에는 해시태그를 포함하고, 줄바꿈은 \\n으로 씁니다."
 ],
 "reference": {
  "ar_main": "9:16",
  "ar_sheet": "16:9",
  "types": {
   "character": {
    "name": "인물",
    "main": "full-body character reference image, standing in a neutral relaxed pose facing the camera, centered, plain seamless neutral studio background, even soft lighting, every costume and body detail clearly visible, generous empty margin around the subject",
    "sheet": "character turnaround reference sheet showing the same character in three views (front view, three-quarter view, side view) standing in a neutral pose side by side, plain seamless neutral background, identical proportions, costume and colors in every view"
   },
   "object": {
    "name": "사물",
    "main": "single hero object reference image, centered, shown from a clear three-quarter front angle, plain seamless neutral studio background, even soft lighting, every material, shape and color detail clearly visible, generous empty margin around the object",
    "sheet": "object turnaround reference sheet showing the same object in three views (front view, three-quarter view, side view) side by side, plain seamless neutral background, identical shape, material and colors in every view"
   },
   "place": {
    "name": "장소",
    "main": "wide establishing reference image of the location, empty of people, eye-level view, even soft lighting, all architectural and prop details clearly visible, centered composition with generous margins",
    "sheet": "location reference sheet showing the same place from three angles (wide front view, left corner view, right corner view), empty of people, even soft lighting, identical layout, materials and colors in every view"
   }
  }
 },
 "asset_template": [
  "# [기준 이미지 분석 지침] 등장인물·사물 일관성 확보",
  "아래 [6씬 대본과 장면 묘사]를 분석해, 영상 전체에서 반복 등장하거나 스토리 핵심인 인물·사물·장소를 찾아 '기준 이미지'용 asset 으로 정의하세요.",
  "- 2개 이상의 씬에 등장하거나 핵심 소품인 대상만 포함합니다(한 번 스치는 배경 물건은 제외).",
  "- 선택된 화풍: {{style_name}} (화풍 키워드는 appearance 에 쓰지 않습니다. 시스템이 화풍 앵커를 자동 삽입합니다.)",
  "- id: 영문 소문자·숫자·_ / type: character | object | place / name: 한국어 이름 / label: 영문 짧은 호칭(예: the plastic cook figure)",
  "- appearance: 영문 외형 고정 키워드(성별·연령·체형·의상·색·재질·크기·특징 등을 구체적으로, 40단어 이내). 배경·동작·화각은 제외하고, 한글/글자/간판/로고 묘사는 금지합니다.",
  "- 인물(character)의 appearance 에는 반드시 성인 연령을 명시하세요(예: a 30-year-old adult). 피규어/인형 캐릭터도 동일하며, child/kid/boy/girl/young/cute 등 어려 보이는 표현은 금지입니다.",
  "- keywords: 한국어 대본이나 묘사에서 이 대상을 가리키는 단어들을 쉼표로 나열합니다.",
  "{{existing_assets}}",
  "",
  "## 6씬 대본과 장면 묘사",
  "{{scenes_text}}",
  "",
  "## 출력 포맷 (JSON 하나만 ```json 코드블록으로, 설명 문장 금지)",
  "```json",
  "{",
  "  \"assets\": [",
  "    {\"id\": \"hero\", \"type\": \"character\", \"name\": \"주인공\", \"label\": \"the deadpan PVC man figure\", \"appearance\": \"...\", \"keywords\": \"남자, 주인공, 그\"}",
  "  ],",
  "  \"scene_refs\": {\"1\": [\"hero\"], \"2\": [\"hero\"], \"3\": [], \"4\": [], \"5\": [], \"6\": []}",
  "}",
  "```",
  "- scene_refs 의 키는 1~6, 값은 그 씬에 등장하는 asset id 배열입니다."
 ],
 "recurring_stop_words": [
  "shot",
  "view",
  "angle",
  "close",
  "closeup",
  "camera",
  "zoom",
  "push",
  "pull",
  "whip",
  "pan",
  "hard",
  "cut",
  "slow",
  "slowly",
  "fast",
  "tracking",
  "track",
  "back",
  "with",
  "from",
  "into",
  "that",
  "this",
  "their",
  "there",
  "while",
  "toward",
  "towards",
  "across",
  "through",
  "under",
  "over",
  "onto",
  "upon",
  "about",
  "after",
  "before",
  "between",
  "around",
  "inside",
  "outside",
  "above",
  "below",
  "behind",
  "frame",
  "scene",
  "clip",
  "focus",
  "freeze",
  "snap",
  "rapid",
  "smooth",
  "sudden",
  "instant",
  "dynamic",
  "micro",
  "shake",
  "light",
  "lighting",
  "soft",
  "wide",
  "medium",
  "centered",
  "negative",
  "space",
  "margin",
  "area",
  "safe",
  "pulled",
  "framing",
  "extreme",
  "tilt",
  "dutch",
  "level",
  "side",
  "profile",
  "down",
  "upward",
  "downward",
  "single",
  "very",
  "each",
  "other",
  "same",
  "tiny",
  "small",
  "large",
  "huge",
  "massive",
  "miniature",
  "studio",
  "macro",
  "detailed",
  "hyper",
  "collectible",
  "premium",
  "resin",
  "statue",
  "texture",
  "visible",
  "seams",
  "matte",
  "paint",
  "finish",
  "diorama",
  "shift",
  "photography",
  "hands",
  "hand",
  "face",
  "head",
  "eyes",
  "lens",
  "whole",
  "entire",
  "both",
  "being",
  "then",
  "than",
  "them",
  "they",
  "those",
  "these",
  "just",
  "like",
  "more",
  "most",
  "some",
  "such",
  "only",
  "also",
  "even",
  "still",
  "where",
  "which",
  "what",
  "when",
  "against",
  "along",
  "among",
  "beside",
  "beyond",
  "during",
  "except",
  "until",
  "within",
  "without",
  "again",
  "almost",
  "already",
  "always",
  "ever",
  "never",
  "once",
  "twice",
  "quickly",
  "gently",
  "softly",
  "slightly",
  "sharply",
  "suddenly",
  "directly",
  "smoothly",
  "moving",
  "revealing",
  "showing",
  "holding",
  "standing",
  "sitting",
  "looking",
  "turning",
  "rising",
  "falling",
  "dripping",
  "flowing",
  "glowing",
  "gleaming",
  "shimmering",
  "snappy",
  "clean",
  "dirty",
  "greasy",
  "bright",
  "warm",
  "dark",
  "heavy",
  "sharp",
  "tight"
 ],
 "timing": {
  "tolerance": 0.05,
  "scene_tolerance": 0.08
 },
 "policy": {
  "minor_terms": [
   "child",
   "children",
   "kid",
   "kids",
   "boy",
   "boys",
   "girl",
   "girls",
   "teen",
   "teens",
   "teenager",
   "teenagers",
   "teenage",
   "minor",
   "minors",
   "baby",
   "babies",
   "toddler",
   "toddlers",
   "infant",
   "infants",
   "newborn",
   "schoolboy",
   "schoolgirl",
   "student",
   "students",
   "elementary",
   "kindergarten",
   "preschool",
   "juvenile",
   "underage",
   "little girl",
   "little boy",
   "young girl",
   "young boy",
   "loli",
   "shota"
  ],
  "ambiguous_terms": [
   "young",
   "youthful",
   "childlike",
   "childish",
   "baby-faced",
   "innocent",
   "cute",
   "adorable"
  ],
  "sexual_terms": [
   "nude",
   "naked",
   "nudity",
   "topless",
   "sexy",
   "erotic",
   "lingerie",
   "bikini",
   "underwear",
   "seductive",
   "cleavage"
  ],
  "adult_regex": "\\badult\\b|\\b(?:2\\d|[3-6]\\d)[- ]year[- ]old\\b|\\bmiddle[- ]aged\\b|\\bsenior\\b|\\belderly\\b"
 },
 "policy_fix_template": [
  "# [정책 안전 재작성] Google Flow(Veo) 콘텐츠 정책 차단 대응",
  "아래 Scene {{scene_no}} 의 프롬프트가 Google 의 콘텐츠 정책(미성년자 관련 등)에 걸려 생성이 차단되었습니다. 의미와 카메라 컷 구조는 유지하되, 정책에 걸릴 수 있는 요소를 제거해 영문 프롬프트를 다시 써 주세요.",
  "- 모든 등장인물/피규어/캐릭터는 명백한 성인(예: a 30-year-old adult)으로 표현하고, 성인 신체 비율과 성인 의상을 쓰세요.",
  "- 아이·어린이·청소년·학생·아기·소년·소녀, young/little/cute/childlike/baby-faced 등 미성년으로 읽힐 수 있는 표현과 유아적 비율, 귀여움/순수함 강조를 모두 제거하세요.",
  "- 노골적 노출·선정, 유혈·잔혹 묘사, 실존 인물/유명인을 제거하세요.",
  "- 화풍 키워드·안전 마진 문구·--no 접미사는 시스템이 자동 추가하므로 쓰지 않습니다. 글자/간판/텍스트 묘사 금지, 영문만 사용합니다.",
  "{{flagged}}",
  "",
  "## 현재 Scene {{scene_no}}",
  "등장 대상(기준 이미지): {{assets}}",
  "{{scene_text}}",
  "",
  "## 출력 (JSON 하나만 ```json 코드블록으로, 설명 금지)",
  "```json",
  "{\"frame1\": \"...\", \"frame2\": \"...\", \"cuts\": [{\"type\": \"...\", \"prompt\": \"...\"}, {\"type\": \"...\", \"prompt\": \"...\"}, {\"type\": \"...\", \"prompt\": \"...\"}],",
  " \"assets\": [{\"id\": \"asset id\", \"appearance\": \"연령/표현을 고친 영문 외형\"}]}",
  "```",
  "- assets 는 이 씬에 연결된 등장 대상 중 외형(appearance)의 연령/표현을 고쳐야 하는 것만 포함합니다(없으면 빈 배열)."
 ]
};
window.PIPELINE_SEED = {
 "_note": "오프라인/수집 실패 시 쓰는 '샘플' 목록입니다. 실제 트렌드가 아니라 아이디어 예시이므로 대시보드에서 [샘플] 배지로 표시됩니다. 자유롭게 수정하세요.",
 "items": [
  {
   "platform": "쿠팡",
   "title": "차량용 초강력 무선 에어건 13만RPM",
   "keyword": "차량용 에어건",
   "cat": "shopping"
  },
  {
   "platform": "쿠팡",
   "title": "모공 피지 흡입 초음파 워터 삭피기",
   "keyword": "초음파 삭피기",
   "cat": "shopping"
  },
  {
   "platform": "쿠팡",
   "title": "접이식 캠핑 회전 릴렉스 의자",
   "keyword": "캠핑 의자",
   "cat": "shopping"
  },
  {
   "platform": "쿠팡",
   "title": "에어프라이어 분할 실리콘 디바이더 팟",
   "keyword": "실리콘 팟",
   "cat": "shopping"
  },
  {
   "platform": "쿠팡",
   "title": "다용도 실리콘 틈새 배수구 마개",
   "keyword": "배수구 마개",
   "cat": "shopping"
  },
  {
   "platform": "틱톡",
   "title": "자가 발전 LED 실리콘 야간 러닝 밴드",
   "keyword": "야간 러닝 밴드",
   "cat": "shopping"
  },
  {
   "platform": "틱톡",
   "title": "원터치 자동 진공 밀폐 음식 보관용기",
   "keyword": "자동 진공 보관기",
   "cat": "shopping"
  },
  {
   "platform": "틱톡",
   "title": "마그네틱 다각도 접이식 스마트폰 거치대",
   "keyword": "자석 폰 거치대",
   "cat": "shopping"
  },
  {
   "platform": "틱톡",
   "title": "휴대용 미니 열풍 열선 비닐 밀봉기",
   "keyword": "비닐 밀봉기",
   "cat": "shopping"
  },
  {
   "platform": "토픽",
   "title": "지구 자전이 딱 1초 멈춘다면?",
   "keyword": "지구 자전 정지",
   "cat": "disaster"
  },
  {
   "platform": "토픽",
   "title": "1939년 히틀러가 노벨 평화상 후보였던 이유",
   "keyword": "히틀러 노벨 평화상",
   "cat": "history"
  },
  {
   "platform": "토픽",
   "title": "고대 로마 검투사의 땀과 때를 긁어 팔던 스트리길",
   "keyword": "스트리길",
   "cat": "history"
  },
  {
   "platform": "토픽",
   "title": "규모 9.0 지진 직후 3분 생존 행동",
   "keyword": "대지진 생존",
   "cat": "disaster"
  },
  {
   "platform": "토픽",
   "title": "모기 소리에 잠 못 드는 사람을 위한 궁극의 방어 시스템",
   "keyword": "모기 퇴치",
   "cat": "bgrade"
  },
  {
   "platform": "토픽",
   "title": "월요일 아침 출근 3초 전 뇌내 상황",
   "keyword": "월요병",
   "cat": "bgrade"
  },
  {
   "platform": "토픽",
   "title": "이 곤충은 뇌를 조종당합니다",
   "keyword": "좀비 곤충",
   "cat": "bizarre_nature"
  },
  {
   "platform": "토픽",
   "title": "연봉 3억인데 아무도 안 하는 일",
   "keyword": "극한 직업",
   "cat": "extreme_jobs"
  },
  {
   "platform": "토픽",
   "title": "상대방이 거짓말할 때 나오는 0.1초 반응",
   "keyword": "거짓말 심리",
   "cat": "psychology"
  }
 ],
 "reddit_subs": {
  "history": [
   "todayilearned",
   "history"
  ],
  "disaster": [
   "Damnthatsinteresting",
   "interestingasfuck"
  ],
  "mystery": [
   "UnresolvedMysteries"
  ],
  "bizarre_nature": [
   "natureismetal",
   "Damnthatsinteresting"
  ],
  "deepsea_space": [
   "space",
   "deepsea"
  ],
  "body_brain": [
   "askscience",
   "todayilearned"
  ],
  "extreme_jobs": [
   "Damnthatsinteresting",
   "oddlysatisfying"
  ],
  "near_future": [
   "Futurology",
   "technology"
  ],
  "psychology": [
   "psychology",
   "todayilearned"
  ],
  "architecture": [
   "engineeringporn",
   "architecture"
  ],
  "shopping": [
   "gadgets",
   "mildlyinteresting"
  ],
  "bgrade": [
   "mildlyinteresting",
   "Showerthoughts"
  ],
  "general": [
   "Damnthatsinteresting",
   "todayilearned",
   "interestingasfuck"
  ]
 },
 "manual_links": [
  {
   "name": "TikTok Creative Center - Top Products",
   "url": "https://ads.tiktok.com/business/creativecenter/pc/en",
   "tip": "Inspiration > Top Products / Trending Videos, 국가 United States, 기간 Last 7 days 로 필터 (한국에 아직 안 넘어온 해외 꿀템 소스)"
  },
  {
   "name": "쿠팡 베스트",
   "url": "https://www.coupang.com/np/best100",
   "tip": "카테고리별 실시간 베스트. 봇 차단이 잦으니 직접 보고 상품명을 [직접 추가]에 붙여넣는 방식이 가장 안정적"
  },
  {
   "name": "YouTube 시크릿 검색",
   "url": "https://www.youtube.com/results?search_query=kitchen+gadget&sp=EgQIAxAB",
   "tip": "필터: 업로드 날짜 이번 달 / 구분 동영상(쇼츠 포함) / 정렬 조회수. 구독자 10만 이하인데 조회수 100만+ 영상만 URL 복사"
  },
  {
   "name": "Reddit r/Damnthatsinteresting",
   "url": "https://www.reddit.com/r/Damnthatsinteresting/top/?t=week",
   "tip": "역사/재난/미스터리 텍스트·스토리 팩트 소재 발굴"
  }
 ]
};
window.PIPELINE_SAMPLES = {
 "airfryer_shopping": {
  "version": 3,
  "meta": {
   "topic": "에어프라이어 실리콘 원형 디바이더 팟 (쿠팡 트렌드 꿀템)",
   "top_title": "아직도 종이호일 태우세요?",
   "category": "shopping",
   "category2": "",
   "format": "",
   "style": "diorama",
   "language": "ko",
   "source_url": "",
   "source_script": ""
  },
  "options": {
   "zero_text": true,
   "safe_margin": true,
   "adult_safe": true,
   "camera_warn": true
  },
  "timing": {
   "chars_per_sec": 0
  },
  "assets": [
   {
    "id": "pot",
    "type": "object",
    "name": "실리콘 팟",
    "label": "the sage-green silicone pot",
    "appearance": "a pastel sage-green platinum silicone round air fryer divider pot with radial wave grooves on the bottom and a central divider wall",
    "keywords": "팟, 실리콘, 디바이더, 이거",
    "done": false
   },
   {
    "id": "cook",
    "type": "character",
    "name": "요리하는 주인공",
    "label": "the PVC home cook figure",
    "appearance": "a 30-year-old adult PVC figure of a home cook with short brown hair and a cream apron",
    "keywords": "손목, 설거지, 나, 사람",
    "done": false
   },
   {
    "id": "fryer",
    "type": "object",
    "name": "에어프라이어",
    "label": "the black air fryer",
    "appearance": "a compact round black basket-style air fryer with a silver handle",
    "keywords": "에어프라이어, 기계, 바스켓",
    "done": false
   }
  ],
  "analysis": {
   "hook_technique": "",
   "retention_psychology": "",
   "skeleton": ""
  },
  "plan": {
   "titles": [
    "아직도 에어프라이어 청소 30분씩 하세요? 인생 꿀템 발견!",
    "종이호일 태우던 사람들이 갈아탄 이유",
    "설거지 3초 컷 에어프라이어 팟"
   ],
   "description": "종이호일 매번 태우고 기름때 벗기느라 스트레스 받으셨던 분들 주목! 내열 실리콘 팟 하나로 설거지 3초 컷.",
   "hashtags": [
    "#에어프라이어",
    "#주방꿀템",
    "#살림꿀팁",
    "#쿠팡추천템",
    "#shorts"
   ]
  },
  "scenes": [
   {
    "id": 1,
    "beats": [
     "아직도 에어프라이어에 종이호일 깔고",
     "타서 눌어붙은 기름때 닦느라",
     "손목 다 나가고 계신가요?"
    ],
    "frame1": "medium shot of a dirty greasy air fryer basket with burnt paper foil smoking slightly, dim moody kitchen lighting",
    "frame2": "low-angle shot of the frustrated PVC cook waving both hands in despair beside the messy air fryer",
    "refs": [
     "cook",
     "fryer"
    ],
    "cuts": [
     {
      "type": "Medium Close-up",
      "prompt": "Rapid push-in zoom toward the smoking burnt foil and sticky residue"
     },
     {
      "type": "Low-angle Dutch Tilt",
      "prompt": "Snap cut to the cook looking up at the greasy basket, micro-camera shake"
     },
     {
      "type": "Whip-pan Pull-back",
      "prompt": "Snappy whip-pan pull-back revealing the whole smoky messy countertop"
     }
    ]
   },
   {
    "id": 2,
    "beats": [
     "기름때는 안 지워지고 코팅은 다 벗겨져서",
     "비싼 기계 통째로 버릴 뻔한 적",
     "다들 한 번쯤 있으시죠?"
    ],
    "frame1": "top-down view of peeled non-stick coating flakes and a harsh metallic sponge scrubbing the basket surface",
    "frame2": "45-degree view of a worn-out cooking basket covered in scratch marks under harsh kitchen side lighting",
    "refs": [
     "cook",
     "fryer"
    ],
    "cuts": [
     {
      "type": "Top-down POV",
      "prompt": "Fast tracking over the flaking coating as the metal sponge scrapes across it"
     },
     {
      "type": "45-degree Over-the-shoulder",
      "prompt": "Hard cut to the scratched basket with dust particles floating in the harsh side light"
     },
     {
      "type": "Slow Pull-back",
      "prompt": "Slow zoom-out revealing the cluttered messy kitchen counter with grease stains"
     }
    ]
   },
   {
    "id": 3,
    "beats": [
     "이제 이거 하나만 넣으세요!",
     "내열 250도 플래티넘 실리콘 팟",
     "에어프라이어 전용 분할 디바이더예요."
    ],
    "frame1": "front hero shot of the pastel sage-green silicone pot dropping gracefully into the center of the clean air fryer basket, studio spotlight",
    "frame2": "medium close-up of the grooved wave bottom ridges of the silicone pot with wide negative space around it",
    "refs": [
     "pot"
    ],
    "cuts": [
     {
      "type": "Front Center Hero",
      "prompt": "Smooth push-in as the pot lands softly in the middle of the frame with a gentle bounce"
     },
     {
      "type": "Orbiting View",
      "prompt": "Hard cut to a circular camera orbit around the pot showcasing its grooved bottom ridges"
     },
     {
      "type": "Macro Texture Pull-back",
      "prompt": "Snap focus on the flexible soft silicone bending smoothly without deformation, then fast pull-back"
     }
    ]
   },
   {
    "id": 4,
    "beats": [
     "가운데 칸막이로 고기와 감자튀김을",
     "냄새 섞임 없이 동시에 조리하고",
     "기름은 웨이브 바닥으로 쏙 빠집니다."
    ],
    "frame1": "high-angle shot showing the center divider separating sizzling crispy pork belly on one side and golden french fries on the other",
    "frame2": "medium close-up of hot golden oil draining cleanly down the radial wave grooves away from the food",
    "refs": [
     "pot",
     "fryer"
    ],
    "cuts": [
     {
      "type": "Split-focus Top Angle",
      "prompt": "Slow tracking glide across both sides of the divider as the food sizzles"
     },
     {
      "type": "Slow-motion Liquid Cut",
      "prompt": "Hard cut to slow-motion golden oil draining down the wave grooves with fluid ripples"
     },
     {
      "type": "Eye-level Sizzle",
      "prompt": "Snappy whip-pan to an eye-level shot of delicate steam rising from the golden cooked meal"
     }
    ]
   },
   {
    "id": 5,
    "beats": [
     "다 먹고 뒤집어서 물로 깨끗이 헹구면",
     "기름이 미끄러지듯 떨어져서",
     "설거지 3초 컷으로 끝납니다."
    ],
    "frame1": "medium shot of the PVC cook flipping the flexible silicone pot inside-out with an effortless snap, pristine clean surface",
    "frame2": "medium close-up of a crystal clear water stream splashing over the non-stick surface while oil slides off",
    "refs": [
     "pot",
     "cook"
    ],
    "cuts": [
     {
      "type": "Dynamic Action Angle",
      "prompt": "Fast tracking as the hands flip the pot inside-out with a springy snap"
     },
     {
      "type": "High-speed Water Splash",
      "prompt": "Hard cut to a high-speed water stream splashing across the surface, oil sliding off in one second"
     },
     {
      "type": "Sparkle Clean Hero",
      "prompt": "Snappy whip-pan to the sparkling clean pot drying on a wooden miniature rack with a gleam effect"
     }
    ]
   },
   {
    "id": 6,
    "beats": [
     "오늘만 반값 특가 진행 중이니",
     "놓치면 재고 소진이에요.",
     "제품 정보는 하단 쇼핑 태그와 고정 댓글 확인!"
    ],
    "frame1": "wide beauty shot of neatly stacked sage green, cream and blush pink silicone pots on a modern clean kitchen island, empty space in the lower area",
    "frame2": "medium shot of a miniature wooden pointing arrow indicating downward toward the lower safe area",
    "refs": [
     "pot"
    ],
    "cuts": [
     {
      "type": "Commercial Hero Display",
      "prompt": "Smooth push-in on the stacked colorful pots with a shimmering clean kitchen background"
     },
     {
      "type": "Pointer Gesture Cut",
      "prompt": "Hard cut to the wooden arrow bouncing and pointing downward with a playful motion"
     },
     {
      "type": "Final Lockup",
      "prompt": "Snappy whip-pan pull-back to a centered wide beauty shot of the whole product set, then hard blackout"
     }
    ]
   }
  ],
  "render": {
   "crop_scale": 1.06,
   "fit": "cover",
   "top_bar": 240,
   "bottom_bar": 400,
   "bar_color": "000000",
   "title_font": "",
   "title_size": 66,
   "title_color": "FFE500",
   "title_outline": 2,
   "title_outline_color": "000000",
   "title_y": 0,
   "title_chars_per_line": 15,
   "sub_font": "",
   "sub_size": 52,
   "sub_color": "FFFFFF",
   "sub_outline": 0,
   "sub_outline_color": "000000",
   "sub_box": true,
   "sub_box_color": "000000",
   "sub_box_alpha": 0.65,
   "sub_box_border": 14,
   "sub_gap": 8,
   "sub_bottom": 0,
   "sub_bottom_gap": 20,
   "sub_chars_per_line": 18
  },
  "metadata": {
   "ko": {
    "youtube": {
     "title": "아직도 에어프라이어 청소 30분씩 하세요? 인생 꿀템 발견!",
     "caption": "종이호일 매번 태우고 기름때 벗기느라 스트레스 받으셨던 분들 주목! 내열 실리콘 팟 하나로 설거지 3초 컷 끝냈습니다.\n\n#에어프라이어 #주방꿀템 #살림꿀팁 #쿠팡추천템 #생활용품 #shorts",
     "pinned": "🔥 영상 속 분할 실리콘 팟 구매 링크는 [하단 쇼핑 태그] 및 아래 첫 댓글 공식 링크에서 단독 할인 중입니다! 👇"
    },
    "instagram": {
     "title": "살림 9단만 안다는 에어프라이어 청소 종결템 🍳",
     "caption": "종이호일의 위험함과 기름때 지옥에서 벗어나세요! 뒤집어서 물만 뿌리면 설거지 완료 ✨\n\n📌 프로필 링크에서 '에어프라이어 팟' 검색!\n#살림스타그램 #주방스타그램 #자취꿀템 #살림팁 #리뷰스타그램",
     "pinned": "🛍️ 구매 정보: 프로필 상단 링크트리 클릭 후 '1번 실리콘 팟' 확인해 주세요!"
    },
    "tiktok": {
     "title": "이거 쓰고 삶의 질 수직상승함 ㅋㅋㅋ 3초 세척 실화냐?",
     "caption": "기름때 안 닦여서 고생했던 과거 안녕.. 🖐️ 분할 조리까지 쌉가능 #주방꿀템 #자취생필수템 #추천 #fyp #살림팁",
     "pinned": "좌측 하단 [노란색 장바구니] 누르시면 오늘 마감 특가로 바로 확인 가능합니다! 🛒"
    }
   },
   "en": {
    "youtube": {
     "title": "Stop Ruining Your Air Fryer! This 3-Second Hack Changes Everything",
     "caption": "Tired of burning parchment paper and scrubbing non-stick residue? Meet the ultimate dual-chamber silicone air fryer divider.\n\n#airfryer #kitchenhacks #amazonfinds #cleantok #kitchengadgets #shorts",
     "pinned": "🛒 Product link available in the YouTube Shopping Tag below and the pinned link with an exclusive discount! 👇"
    },
    "instagram": {
     "title": "The Ultimate Kitchen Hack for Air Fryer Lovers ✨",
     "caption": "Dual cooking zones, zero mess, 100% food-grade platinum silicone. Cleans in seconds!\n\nLink in bio to shop now. #kitchenorganization #cleaningmotivation #homefinds",
     "pinned": "Tap the link in bio to shop this viral silicone pot! 🍳"
    },
    "tiktok": {
     "title": "My air fryer has never been cleaner!! Viral TikTok kitchen find",
     "caption": "Separates oil automatically and cleans in 3 seconds flat. Check the yellow cart! #tiktokmademebuyit #kitchenfinds #lifehack #foryou",
     "pinned": "Grab yours now via the yellow basket at bottom left! ⬇️"
    }
   }
  }
 },
 "ramen_bgrade": {
  "version": 3,
  "meta": {
   "topic": "라면 물 550ml 완벽 조절을 위한 궁극의 시스템",
   "top_title": "라면 물 조절 실패하는 사람 필독",
   "category": "bgrade",
   "category2": "",
   "format": "",
   "style": "diorama",
   "language": "ko",
   "source_url": "https://www.youtube.com/shorts/JNcjKUSolis",
   "source_script": "(벤치마킹 원본: 우산을 써도 다리가 젖는 사소한 불편 -> 과도한 공학 장치를 하나씩 추가 -> 결국 거대 기계 완성 -> 원래 문제로 회귀하는 허무한 클로징)"
  },
  "options": {
   "zero_text": true,
   "safe_margin": true,
   "adult_safe": true,
   "camera_warn": true
  },
  "timing": {
   "chars_per_sec": 0
  },
  "assets": [
   {
    "id": "hero",
    "type": "character",
    "name": "주인공 피규어",
    "label": "the deadpan PVC man figure",
    "appearance": "a 30-year-old adult male PVC figure with a deadpan painted face, short black hair, wearing a plain white t-shirt and grey shorts",
    "keywords": "남자, 주인공, 사람, 나",
    "done": false
   },
   {
    "id": "pot",
    "type": "object",
    "name": "냄비",
    "label": "the small silver pot",
    "appearance": "a small round stainless-steel cooking pot with two black side handles and a clear glass lid",
    "keywords": "냄비, 물, 라면",
    "done": false
   },
   {
    "id": "kitchen",
    "type": "place",
    "name": "주방",
    "label": "the tiny apartment kitchen",
    "appearance": "a tiny miniature studio-apartment kitchen diorama with white tile walls, a light wooden counter and a small gas stove",
    "keywords": "주방, 싱크대, 부엌, 방",
    "done": false
   }
  ],
  "analysis": {
   "hook_technique": "\"우산을 써도 다리가 젖는다\"는 100% 공감 가능한 사소한 불편으로 1초 만에 시선 확보",
   "retention_psychology": "해결 장치를 하나 더할 때마다 새 문제가 생기는 점진적 과장(Escalation)을 극도로 진지한 톤으로 전개",
   "skeleton": "[사소한 불편] → [과도한 공학 장치 1] → [파생 문제 해결 장치 2] → [거대 기계 완성] → [원래 문제로 회귀하는 허무한 반전]"
  },
  "plan": {
   "titles": [
    "라면 물 550ml 칼같이 맞추려다 공장을 지어버린 사람",
    "라면 물 조절 실패하는 사람들을 위한 최종 병기",
    "물 1방울 오차도 용납 못 하는 이과생의 라면 끓이기"
   ],
   "description": "라면 끓일 때마다 한강물 만들던 분들 주목하세요. 오차 0.01ml 이하의 유체역학 라면 조리 시스템입니다.",
   "hashtags": [
    "#라면물조절",
    "#병맛",
    "#공학시뮬레이션",
    "#피규어",
    "#디오라마",
    "#shorts"
   ]
  },
  "scenes": [
   {
    "id": 1,
    "beats": [
     "라면 끓일 때마다 물 맞추기 실패한다면",
     "눈대중 대신 냄비 위에",
     "정밀 유량 조절기를 달면 됩니다."
    ],
    "frame1": "medium macro shot of the male PVC figure staring blankly at a miniature silver pot overflowing with clear water on a tiny kitchen counter",
    "frame2": "low-angle shot of a miniature stainless steel IV drip regulator with precision brass dials clamping onto the pot rim",
    "refs": [
     "hero",
     "pot",
     "kitchen"
    ],
    "cuts": [
     {
      "type": "Medium Close-up",
      "prompt": "Rapid push-in zoom toward the plastic figure's disappointed deadpan face above the flooded pot"
     },
     {
      "type": "Low-angle Tilt",
      "prompt": "A mechanical steel clamp snaps securely onto the pot rim with brass valves gleaming under a spotlight, micro-camera shake on impact"
     },
     {
      "type": "Tracking Side Profile",
      "prompt": "A single water droplet drips slowly through a clear glass chamber, sharp freeze at 7.5s"
     }
    ]
   },
   {
    "id": 2,
    "beats": [
     "그런데 수압 오차까지 없애려고",
     "항공기용 유압 펌프를 붙였더니",
     "무게 때문에 싱크대가 주저앉았죠."
    ],
    "frame1": "medium shot of heavy miniature hydraulic tubes and an industrial steel pump humming beside the small pot, metallic reflections",
    "frame2": "Dutch angle wide shot of the miniature kitchen counter cracking and tilting downward under immense heavy machinery weight",
    "refs": [
     "hero",
     "pot",
     "kitchen"
    ],
    "cuts": [
     {
      "type": "Tracking Medium Shot",
      "prompt": "Fast tracking shot along high-pressure hydraulic pipes pulsing with subtle mechanical vibration"
     },
     {
      "type": "Dutch Angle Wide",
      "prompt": "The miniature counter buckles with a sharp downward tilt, plaster dust falling, dynamic camera shake on impact"
     },
     {
      "type": "Whip-pan Upward",
      "prompt": "Fast whip-pan upward to the PVC figure standing rigidly with hands on hips, head tilted in disbelief, freeze at 7.5s"
     }
    ]
   },
   {
    "id": 3,
    "beats": [
     "붕괴를 막으려 바닥에 철골 기둥을 세우고",
     "증발량 계산용 레이저 센서를",
     "천장 위에도 따로 설치했습니다."
    ],
    "frame1": "low-angle shot of sturdy red industrial H-beam miniature steel pillars supporting the cracked counter from below",
    "frame2": "medium close-up of a ceiling-mounted miniature laser emitter projecting a glowing circular grid downward onto the pot surface",
    "refs": [
     "hero",
     "pot"
    ],
    "cuts": [
     {
      "type": "Low-angle Tilt",
      "prompt": "Smooth upward tilt tracking the heavy red steel support beams holding the sagging structure"
     },
     {
      "type": "Ceiling Angle",
      "prompt": "A sleek laser sensor rotates smoothly, firing an intricate grid pattern downward into the pot"
     },
     {
      "type": "Whip-pan Downward",
      "prompt": "Snappy whip-pan downward to the boiling water surface illuminated in green laser light, crisp freeze at 7.5s"
     }
    ]
   },
   {
    "id": 4,
    "beats": [
     "기화된 수분은 초저온 냉각 돔으로",
     "0.1ml 단위까지 회수했더니",
     "오차율 0%, 550ml가 완성됐죠."
    ],
    "frame1": "medium shot of a massive spherical glass condenser dome descending mechanically over the bubbling pot, frosty white vapor curling",
    "frame2": "medium close-up of a tiny glowing cyan liquid droplet falling into a calibrated glass chamber, soft rim lighting",
    "refs": [
     "hero",
     "pot"
    ],
    "cuts": [
     {
      "type": "Dramatic Rush Down",
      "prompt": "Dramatic camera rush down as the glass condensation dome clamps tightly over the boiling steam"
     },
     {
      "type": "Macro Chamber",
      "prompt": "A single droplet falls in ultra-slow motion with water ripple physics, glowing softly"
     },
     {
      "type": "Snap Whip-pan",
      "prompt": "Snappy whip-pan to an automated mechanical valve hissing open, releasing a burst of cooling mist, sharp freeze at 7.5s"
     }
    ]
   },
   {
    "id": 5,
    "beats": [
     "문제는 기계에서 나오는 열기 때문에 방 안 온도가",
     "순식간에 사우나 수준인 60도까지",
     "올라간다는 겁니다."
    ],
    "frame1": "eye-level wide shot of the entire kitchen transformed into a sprawling industrial chemical plant diorama, glowing orange heat aura",
    "frame2": "close-up of the male PVC figure sweating painted sweat droplets, holding chopsticks weakly in the melting kitchen diorama",
    "refs": [
     "hero",
     "pot",
     "kitchen"
    ],
    "cuts": [
     {
      "type": "Slow Pull-back",
      "prompt": "Cinematic slow pull-back revealing the ridiculously oversized industrial piping filling the tiny apartment kitchen"
     },
     {
      "type": "Dutch Tilt Close-up",
      "prompt": "Heat haze ripples across the camera lens, the plastic figure stands dazed in exhaustion"
     },
     {
      "type": "Whip-pan Downward",
      "prompt": "Fast whip-pan downward to chopsticks drooping under the intense heat, sharp snap freeze at 7.5s"
     }
    ]
   },
   {
    "id": 6,
    "beats": [
     "결국 땀 뻘뻘 흘리며 뚜껑을 열었더니",
     "스프 넣는 걸 깜빡했더라고요.",
     "그러니까 그냥 눈대중으로 드세요."
    ],
    "frame1": "medium shot of the PVC figure opening the pot lid, showing completely clear plain water with plain yellow noodles and zero soup broth",
    "frame2": "close-up of an unopened silver seasoning packet resting on the counter while the figure stares directly at camera in frozen despair",
    "refs": [
     "hero",
     "pot"
    ],
    "cuts": [
     {
      "type": "Tracking Forward",
      "prompt": "Camera tracks forward into the pot showing completely pale, clear broth without seasoning"
     },
     {
      "type": "Close-up Hold",
      "prompt": "The unopened seasoning packet glints under the lamp while the figure stares deadpan directly into the lens"
     },
     {
      "type": "Push-in Fourth Wall",
      "prompt": "Snappy push-in zoom toward the figure's unblinking eyes breaking the fourth wall, sudden hard blackout transition at 7.5s"
     }
    ]
   }
  ],
  "render": {
   "crop_scale": 1.06,
   "fit": "cover",
   "top_bar": 240,
   "bottom_bar": 400,
   "bar_color": "000000",
   "title_font": "",
   "title_size": 66,
   "title_color": "FFE500",
   "title_outline": 2,
   "title_outline_color": "000000",
   "title_y": 0,
   "title_chars_per_line": 15,
   "sub_font": "",
   "sub_size": 52,
   "sub_color": "FFFFFF",
   "sub_outline": 0,
   "sub_outline_color": "000000",
   "sub_box": true,
   "sub_box_color": "000000",
   "sub_box_alpha": 0.65,
   "sub_box_border": 14,
   "sub_gap": 8,
   "sub_bottom": 0,
   "sub_bottom_gap": 20,
   "sub_chars_per_line": 18
  },
  "metadata": {}
 }
};
