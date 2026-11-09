# 프롬프트 예시 모음 (엔진 자동 생성)

> 이 문서는 `python tools_gen_docs.py` 가 `samples/*.json` 과 `config.json` 에서 **자동 생성**합니다. 직접 고치지 말고 샘플/설정을 고친 뒤 다시 생성하세요.
> 모든 Frame 프롬프트는 `화풍 앵커 → 그 씬에 등장하는 기준 이미지 대상의 외형 → 장면 묘사 → 안전 마진 → --no 접미사` 순서로 합성되고, Omni 프롬프트는 연결 문구와 화풍 질감이 자동 합성됩니다.

## 케이스: 라면 물 550ml 완벽 조절을 위한 궁극의 시스템

- 카테고리: 현대인 공감 B급 병맛 시트콤
- 화풍: 7. 고정밀 피규어 & 디오라마
- 상단 타이틀: 라면 물 조절 실패하는 사람 필독
- 대본 분량: 330자 (목표 320~350)

### 6씬 대본 (2.5초 비트)

| 씬 | 0.0~2.5s | 2.5~5.0s | 5.0~7.5s | 글자수 |
|---|---|---|---|---|
| 01 | 라면 끓일 때마다 물 맞추기 실패한다면 | 눈대중 대신 냄비 위에 | 정밀 유량 조절기를 달면 됩니다. | 53 |
| 02 | 그런데 수압 오차까지 없애려고 | 항공기용 유압 펌프를 붙였더니 | 무게 때문에 싱크대가 주저앉았죠. | 52 |
| 03 | 붕괴를 막으려 바닥에 철골 기둥을 세우고 | 증발량 계산용 레이저 센서를 | 천장 위에도 따로 설치했습니다. | 56 |
| 04 | 기화된 수분은 초저온 냉각 돔으로 | 0.1ml 단위까지 회수했더니 | 오차율 0%, 550ml가 완성됐죠. | 56 |
| 05 | 문제는 기계에서 나오는 열기 때문에 방 안 온도가 | 순식간에 사우나 수준인 60도까지 | 올라간다는 겁니다. | 57 |
| 06 | 결국 땀 뻘뻘 흘리며 뚜껑을 열었더니 | 스프 넣는 걸 깜빡했더라고요. | 그러니까 그냥 눈대중으로 드세요. | 56 |

### 기준 이미지 (등장 대상별 - 씬 이미지보다 먼저 생성)

**주인공 피규어** (character) - 등장 씬: 1, 2, 3, 4, 5, 6

대표 1컷
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult male PVC figure with a deadpan painted face, short black hair, wearing a plain white t-shirt and grey shorts, all characters are clearly adult, full-body character reference image, standing in a neutral relaxed pose facing the camera, centered, plain seamless neutral studio background, even soft lighting, every costume and body detail clearly visible, generous empty margin around the subject --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
3면 턴어라운드 시트(선택)
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult male PVC figure with a deadpan painted face, short black hair, wearing a plain white t-shirt and grey shorts, all characters are clearly adult, character turnaround reference sheet showing the same character in three views (front view, three-quarter view, side view) standing in a neutral pose side by side, plain seamless neutral background, identical proportions, costume and colors in every view --no text, letters, words, typography, subtitles, font, signage, watermark --ar 16:9
```

**냄비** (object) - 등장 씬: 1, 2, 3, 4, 5, 6

대표 1컷
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a small round stainless-steel cooking pot with two black side handles and a clear glass lid, single hero object reference image, centered, shown from a clear three-quarter front angle, plain seamless neutral studio background, even soft lighting, every material, shape and color detail clearly visible, generous empty margin around the object --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
3면 턴어라운드 시트(선택)
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a small round stainless-steel cooking pot with two black side handles and a clear glass lid, object turnaround reference sheet showing the same object in three views (front view, three-quarter view, side view) side by side, plain seamless neutral background, identical shape, material and colors in every view --no text, letters, words, typography, subtitles, font, signage, watermark --ar 16:9
```

**주방** (place) - 등장 씬: 1, 2, 5

대표 1컷
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a tiny miniature studio-apartment kitchen diorama with white tile walls, a light wooden counter and a small gas stove, wide establishing reference image of the location, empty of people, eye-level view, even soft lighting, all architectural and prop details clearly visible, centered composition with generous margins --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
3면 턴어라운드 시트(선택)
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a tiny miniature studio-apartment kitchen diorama with white tile walls, a light wooden counter and a small gas stove, location reference sheet showing the same place from three angles (wide front view, left corner view, right corner view), empty of people, even soft lighting, identical layout, materials and colors in every view --no text, letters, words, typography, subtitles, font, signage, watermark --ar 16:9
```

### Scene 01 - 충격적 훅 (Hook) (0.0~7.5s)

**대사**: 라면 끓일 때마다 물 맞추기 실패한다면 눈대중 대신 냄비 위에 정밀 유량 조절기를 달면 됩니다.

**Frame 1 (0s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult male PVC figure with a deadpan painted face, short black hair, wearing a plain white t-shirt and grey shorts, a small round stainless-steel cooking pot with two black side handles and a clear glass lid, a tiny miniature studio-apartment kitchen diorama with white tile walls, a light wooden counter and a small gas stove, medium macro shot of the male PVC figure staring blankly at a miniature silver pot overflowing with clear water on a tiny kitchen counter, all characters are clearly adult, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Frame 2 (2.5s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult male PVC figure with a deadpan painted face, short black hair, wearing a plain white t-shirt and grey shorts, a small round stainless-steel cooking pot with two black side handles and a clear glass lid, a tiny miniature studio-apartment kitchen diorama with white tile walls, a light wooden counter and a small gas stove, low-angle shot of a miniature stainless steel IV drip regulator with precision brass dials clamping onto the pot rim, all characters are clearly adult, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Omni 1.2 (I2V, 7.5초)**
```
A continuous 7.5-second vertical 9:16 clip with snappy transitions every 2.5 seconds, consistent visual style, pure visual storytelling without any letters or text:

[0.0s - 2.5s]: Start from Frame 1. Rapid push-in zoom toward the plastic figure's disappointed deadpan face above the flooded pot.

[2.5s - 5.0s]: Instant hard cut to the Frame 2 view. A mechanical steel clamp snaps securely onto the pot rim with brass valves gleaming under a spotlight, micro-camera shake on impact.

[5.0s - 7.5s]: Snappy whip-pan transition to a brand-new third angle. A single water droplet drips slowly through a clear glass chamber, sharp freeze at 7.5s.

Visual Polish: Miniature stop-motion feel, precise macro depth of field, subtle plastic reflections, flawless scale consistency, no morphing artifacts between cuts, subject stays centered in the safe zone, all characters are clearly adult, no text, letters or typography.
```

### Scene 02 - 문제 심화 / 기존 대안 실패 (7.5~15.0s)

**대사**: 그런데 수압 오차까지 없애려고 항공기용 유압 펌프를 붙였더니 무게 때문에 싱크대가 주저앉았죠.

**Frame 1 (0s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult male PVC figure with a deadpan painted face, short black hair, wearing a plain white t-shirt and grey shorts, a small round stainless-steel cooking pot with two black side handles and a clear glass lid, a tiny miniature studio-apartment kitchen diorama with white tile walls, a light wooden counter and a small gas stove, medium shot of heavy miniature hydraulic tubes and an industrial steel pump humming beside the small pot, metallic reflections, all characters are clearly adult, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Frame 2 (2.5s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult male PVC figure with a deadpan painted face, short black hair, wearing a plain white t-shirt and grey shorts, a small round stainless-steel cooking pot with two black side handles and a clear glass lid, a tiny miniature studio-apartment kitchen diorama with white tile walls, a light wooden counter and a small gas stove, Dutch angle wide shot of the miniature kitchen counter cracking and tilting downward under immense heavy machinery weight, all characters are clearly adult, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Omni 1.2 (I2V, 7.5초)**
```
A continuous 7.5-second vertical 9:16 clip with snappy transitions every 2.5 seconds, consistent visual style, pure visual storytelling without any letters or text:

[0.0s - 2.5s]: Start from Frame 1. Fast tracking shot along high-pressure hydraulic pipes pulsing with subtle mechanical vibration.

[2.5s - 5.0s]: Instant hard cut to the Frame 2 view. The miniature counter buckles with a sharp downward tilt, plaster dust falling, dynamic camera shake on impact.

[5.0s - 7.5s]: Snappy whip-pan transition to a brand-new third angle. Fast whip-pan upward to the PVC figure standing rigidly with hands on hips, head tilted in disbelief, freeze at 7.5s.

Visual Polish: Miniature stop-motion feel, precise macro depth of field, subtle plastic reflections, flawless scale consistency, no morphing artifacts between cuts, subject stays centered in the safe zone, all characters are clearly adult, no text, letters or typography.
```

### Scene 03 - 원인 해부 / 솔루션 등장 (15.0~22.5s)

**대사**: 붕괴를 막으려 바닥에 철골 기둥을 세우고 증발량 계산용 레이저 센서를 천장 위에도 따로 설치했습니다.

**Frame 1 (0s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult male PVC figure with a deadpan painted face, short black hair, wearing a plain white t-shirt and grey shorts, a small round stainless-steel cooking pot with two black side handles and a clear glass lid, low-angle shot of sturdy red industrial H-beam miniature steel pillars supporting the cracked counter from below, all characters are clearly adult, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Frame 2 (2.5s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult male PVC figure with a deadpan painted face, short black hair, wearing a plain white t-shirt and grey shorts, a small round stainless-steel cooking pot with two black side handles and a clear glass lid, medium close-up of a ceiling-mounted miniature laser emitter projecting a glowing circular grid downward onto the pot surface, all characters are clearly adult, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Omni 1.2 (I2V, 7.5초)**
```
A continuous 7.5-second vertical 9:16 clip with snappy transitions every 2.5 seconds, consistent visual style, pure visual storytelling without any letters or text:

[0.0s - 2.5s]: Start from Frame 1. Smooth upward tilt tracking the heavy red steel support beams holding the sagging structure.

[2.5s - 5.0s]: Instant hard cut to the Frame 2 view. A sleek laser sensor rotates smoothly, firing an intricate grid pattern downward into the pot.

[5.0s - 7.5s]: Snappy whip-pan transition to a brand-new third angle. Snappy whip-pan downward to the boiling water surface illuminated in green laser light, crisp freeze at 7.5s.

Visual Polish: Miniature stop-motion feel, precise macro depth of field, subtle plastic reflections, flawless scale consistency, no morphing artifacts between cuts, subject stays centered in the safe zone, all characters are clearly adult, no text, letters or typography.
```

### Scene 04 - 기능 검증 / 핵심 카타르시스 (22.5~30.0s)

**대사**: 기화된 수분은 초저온 냉각 돔으로 0.1ml 단위까지 회수했더니 오차율 0%, 550ml가 완성됐죠.

**Frame 1 (0s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult male PVC figure with a deadpan painted face, short black hair, wearing a plain white t-shirt and grey shorts, a small round stainless-steel cooking pot with two black side handles and a clear glass lid, medium shot of a massive spherical glass condenser dome descending mechanically over the bubbling pot, frosty white vapor curling, all characters are clearly adult, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Frame 2 (2.5s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult male PVC figure with a deadpan painted face, short black hair, wearing a plain white t-shirt and grey shorts, a small round stainless-steel cooking pot with two black side handles and a clear glass lid, medium close-up of a tiny glowing cyan liquid droplet falling into a calibrated glass chamber, soft rim lighting, all characters are clearly adult, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Omni 1.2 (I2V, 7.5초)**
```
A continuous 7.5-second vertical 9:16 clip with snappy transitions every 2.5 seconds, consistent visual style, pure visual storytelling without any letters or text:

[0.0s - 2.5s]: Start from Frame 1. Dramatic camera rush down as the glass condensation dome clamps tightly over the boiling steam.

[2.5s - 5.0s]: Instant hard cut to the Frame 2 view. A single droplet falls in ultra-slow motion with water ripple physics, glowing softly.

[5.0s - 7.5s]: Snappy whip-pan transition to a brand-new third angle. Snappy whip-pan to an automated mechanical valve hissing open, releasing a burst of cooling mist, sharp freeze at 7.5s.

Visual Polish: Miniature stop-motion feel, precise macro depth of field, subtle plastic reflections, flawless scale consistency, no morphing artifacts between cuts, subject stays centered in the safe zone, all characters are clearly adult, no text, letters or typography.
```

### Scene 05 - 반전 펀치라인 / 극적 대비 (30.0~37.5s)

**대사**: 문제는 기계에서 나오는 열기 때문에 방 안 온도가 순식간에 사우나 수준인 60도까지 올라간다는 겁니다.

**Frame 1 (0s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult male PVC figure with a deadpan painted face, short black hair, wearing a plain white t-shirt and grey shorts, a small round stainless-steel cooking pot with two black side handles and a clear glass lid, a tiny miniature studio-apartment kitchen diorama with white tile walls, a light wooden counter and a small gas stove, eye-level wide shot of the entire kitchen transformed into a sprawling industrial chemical plant diorama, glowing orange heat aura, all characters are clearly adult, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Frame 2 (2.5s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult male PVC figure with a deadpan painted face, short black hair, wearing a plain white t-shirt and grey shorts, a small round stainless-steel cooking pot with two black side handles and a clear glass lid, a tiny miniature studio-apartment kitchen diorama with white tile walls, a light wooden counter and a small gas stove, close-up of the male PVC figure sweating painted sweat droplets, holding chopsticks weakly in the melting kitchen diorama, all characters are clearly adult, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Omni 1.2 (I2V, 7.5초)**
```
A continuous 7.5-second vertical 9:16 clip with snappy transitions every 2.5 seconds, consistent visual style, pure visual storytelling without any letters or text:

[0.0s - 2.5s]: Start from Frame 1. Cinematic slow pull-back revealing the ridiculously oversized industrial piping filling the tiny apartment kitchen.

[2.5s - 5.0s]: Instant hard cut to the Frame 2 view. Heat haze ripples across the camera lens, the plastic figure stands dazed in exhaustion.

[5.0s - 7.5s]: Snappy whip-pan transition to a brand-new third angle. Fast whip-pan downward to chopsticks drooping under the intense heat, sharp snap freeze at 7.5s.

Visual Polish: Miniature stop-motion feel, precise macro depth of field, subtle plastic reflections, flawless scale consistency, no morphing artifacts between cuts, subject stays centered in the safe zone, all characters are clearly adult, no text, letters or typography.
```

### Scene 06 - 결론 / 행동 유도 (CTA) (37.5~45.0s)

**대사**: 결국 땀 뻘뻘 흘리며 뚜껑을 열었더니 스프 넣는 걸 깜빡했더라고요. 그러니까 그냥 눈대중으로 드세요.

**Frame 1 (0s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult male PVC figure with a deadpan painted face, short black hair, wearing a plain white t-shirt and grey shorts, a small round stainless-steel cooking pot with two black side handles and a clear glass lid, medium shot of the PVC figure opening the pot lid, showing completely clear plain water with plain yellow noodles and zero soup broth, all characters are clearly adult, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Frame 2 (2.5s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult male PVC figure with a deadpan painted face, short black hair, wearing a plain white t-shirt and grey shorts, a small round stainless-steel cooking pot with two black side handles and a clear glass lid, close-up of an unopened silver seasoning packet resting on the counter while the figure stares directly at camera in frozen despair, all characters are clearly adult, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Omni 1.2 (I2V, 7.5초)**
```
A continuous 7.5-second vertical 9:16 clip with snappy transitions every 2.5 seconds, consistent visual style, pure visual storytelling without any letters or text:

[0.0s - 2.5s]: Start from Frame 1. Camera tracks forward into the pot showing completely pale, clear broth without seasoning.

[2.5s - 5.0s]: Instant hard cut to the Frame 2 view. The unopened seasoning packet glints under the lamp while the figure stares deadpan directly into the lens.

[5.0s - 7.5s]: Snappy whip-pan transition to a brand-new third angle. Snappy push-in zoom toward the figure's unblinking eyes breaking the fourth wall, sudden hard blackout transition at 7.5s.

Visual Polish: Miniature stop-motion feel, precise macro depth of field, subtle plastic reflections, flawless scale consistency, no morphing artifacts between cuts, subject stays centered in the safe zone, all characters are clearly adult, no text, letters or typography.
```

---

## 케이스: 에어프라이어 실리콘 원형 디바이더 팟 (쿠팡 트렌드 꿀템)

- 카테고리: 소비 심리 저격 쇼핑 (꿀템)
- 화풍: 7. 고정밀 피규어 & 디오라마
- 상단 타이틀: 아직도 종이호일 태우세요?
- 대본 분량: 325자 (목표 320~350)

### 6씬 대본 (2.5초 비트)

| 씬 | 0.0~2.5s | 2.5~5.0s | 5.0~7.5s | 글자수 |
|---|---|---|---|---|
| 01 | 아직도 에어프라이어에 종이호일 깔고 | 타서 눌어붙은 기름때 닦느라 | 손목 다 나가고 계신가요? | 50 |
| 02 | 기름때는 안 지워지고 코팅은 다 벗겨져서 | 비싼 기계 통째로 버릴 뻔한 적 | 다들 한 번쯤 있으시죠? | 54 |
| 03 | 이제 이거 하나만 넣으세요! | 내열 250도 플래티넘 실리콘 팟 | 에어프라이어 전용 분할 디바이더예요. | 55 |
| 04 | 가운데 칸막이로 고기와 감자튀김을 | 냄새 섞임 없이 동시에 조리하고 | 기름은 웨이브 바닥으로 쏙 빠집니다. | 57 |
| 05 | 다 먹고 뒤집어서 물로 깨끗이 헹구면 | 기름이 미끄러지듯 떨어져서 | 설거지 3초 컷으로 끝납니다. | 52 |
| 06 | 오늘만 반값 특가 진행 중이니 | 놓치면 재고 소진이에요. | 제품 정보는 하단 쇼핑 태그와 고정 댓글 확인! | 57 |

### 기준 이미지 (등장 대상별 - 씬 이미지보다 먼저 생성)

**실리콘 팟** (object) - 등장 씬: 3, 4, 5, 6

대표 1컷
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a pastel sage-green platinum silicone round air fryer divider pot with radial wave grooves on the bottom and a central divider wall, single hero object reference image, centered, shown from a clear three-quarter front angle, plain seamless neutral studio background, even soft lighting, every material, shape and color detail clearly visible, generous empty margin around the object --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
3면 턴어라운드 시트(선택)
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a pastel sage-green platinum silicone round air fryer divider pot with radial wave grooves on the bottom and a central divider wall, object turnaround reference sheet showing the same object in three views (front view, three-quarter view, side view) side by side, plain seamless neutral background, identical shape, material and colors in every view --no text, letters, words, typography, subtitles, font, signage, watermark --ar 16:9
```

**요리하는 주인공** (character) - 등장 씬: 1, 2, 5

대표 1컷
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult PVC figure of a home cook with short brown hair and a cream apron, all characters are clearly adult, full-body character reference image, standing in a neutral relaxed pose facing the camera, centered, plain seamless neutral studio background, even soft lighting, every costume and body detail clearly visible, generous empty margin around the subject --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
3면 턴어라운드 시트(선택)
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult PVC figure of a home cook with short brown hair and a cream apron, all characters are clearly adult, character turnaround reference sheet showing the same character in three views (front view, three-quarter view, side view) standing in a neutral pose side by side, plain seamless neutral background, identical proportions, costume and colors in every view --no text, letters, words, typography, subtitles, font, signage, watermark --ar 16:9
```

**에어프라이어** (object) - 등장 씬: 1, 2, 4

대표 1컷
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a compact round black basket-style air fryer with a silver handle, single hero object reference image, centered, shown from a clear three-quarter front angle, plain seamless neutral studio background, even soft lighting, every material, shape and color detail clearly visible, generous empty margin around the object --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
3면 턴어라운드 시트(선택)
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a compact round black basket-style air fryer with a silver handle, object turnaround reference sheet showing the same object in three views (front view, three-quarter view, side view) side by side, plain seamless neutral background, identical shape, material and colors in every view --no text, letters, words, typography, subtitles, font, signage, watermark --ar 16:9
```

### Scene 01 - 충격적 훅 (Hook) (0.0~7.5s)

**대사**: 아직도 에어프라이어에 종이호일 깔고 타서 눌어붙은 기름때 닦느라 손목 다 나가고 계신가요?

**Frame 1 (0s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult PVC figure of a home cook with short brown hair and a cream apron, a compact round black basket-style air fryer with a silver handle, medium shot of a dirty greasy air fryer basket with burnt paper foil smoking slightly, dim moody kitchen lighting, all characters are clearly adult, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Frame 2 (2.5s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult PVC figure of a home cook with short brown hair and a cream apron, a compact round black basket-style air fryer with a silver handle, low-angle shot of the frustrated PVC cook waving both hands in despair beside the messy air fryer, all characters are clearly adult, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Omni 1.2 (I2V, 7.5초)**
```
A continuous 7.5-second vertical 9:16 clip with snappy transitions every 2.5 seconds, consistent visual style, pure visual storytelling without any letters or text:

[0.0s - 2.5s]: Start from Frame 1. Rapid push-in zoom toward the smoking burnt foil and sticky residue.

[2.5s - 5.0s]: Instant hard cut to the Frame 2 view. Snap cut to the cook looking up at the greasy basket, micro-camera shake.

[5.0s - 7.5s]: Snappy whip-pan transition to a brand-new third angle. Snappy whip-pan pull-back revealing the whole smoky messy countertop.

Visual Polish: Miniature stop-motion feel, precise macro depth of field, subtle plastic reflections, flawless scale consistency, no morphing artifacts between cuts, subject stays centered in the safe zone, all characters are clearly adult, no text, letters or typography.
```

### Scene 02 - 문제 심화 / 기존 대안 실패 (7.5~15.0s)

**대사**: 기름때는 안 지워지고 코팅은 다 벗겨져서 비싼 기계 통째로 버릴 뻔한 적 다들 한 번쯤 있으시죠?

**Frame 1 (0s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult PVC figure of a home cook with short brown hair and a cream apron, a compact round black basket-style air fryer with a silver handle, top-down view of peeled non-stick coating flakes and a harsh metallic sponge scrubbing the basket surface, all characters are clearly adult, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Frame 2 (2.5s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a 30-year-old adult PVC figure of a home cook with short brown hair and a cream apron, a compact round black basket-style air fryer with a silver handle, 45-degree view of a worn-out cooking basket covered in scratch marks under harsh kitchen side lighting, all characters are clearly adult, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Omni 1.2 (I2V, 7.5초)**
```
A continuous 7.5-second vertical 9:16 clip with snappy transitions every 2.5 seconds, consistent visual style, pure visual storytelling without any letters or text:

[0.0s - 2.5s]: Start from Frame 1. Fast tracking over the flaking coating as the metal sponge scrapes across it.

[2.5s - 5.0s]: Instant hard cut to the Frame 2 view. Hard cut to the scratched basket with dust particles floating in the harsh side light.

[5.0s - 7.5s]: Snappy whip-pan transition to a brand-new third angle. Slow zoom-out revealing the cluttered messy kitchen counter with grease stains.

Visual Polish: Miniature stop-motion feel, precise macro depth of field, subtle plastic reflections, flawless scale consistency, no morphing artifacts between cuts, subject stays centered in the safe zone, all characters are clearly adult, no text, letters or typography.
```

### Scene 03 - 원인 해부 / 솔루션 등장 (15.0~22.5s)

**대사**: 이제 이거 하나만 넣으세요! 내열 250도 플래티넘 실리콘 팟 에어프라이어 전용 분할 디바이더예요.

**Frame 1 (0s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a pastel sage-green platinum silicone round air fryer divider pot with radial wave grooves on the bottom and a central divider wall, front hero shot of the pastel sage-green silicone pot dropping gracefully into the center of the clean air fryer basket, studio spotlight, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Frame 2 (2.5s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a pastel sage-green platinum silicone round air fryer divider pot with radial wave grooves on the bottom and a central divider wall, medium close-up of the grooved wave bottom ridges of the silicone pot with wide negative space around it, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Omni 1.2 (I2V, 7.5초)**
```
A continuous 7.5-second vertical 9:16 clip with snappy transitions every 2.5 seconds, consistent visual style, pure visual storytelling without any letters or text:

[0.0s - 2.5s]: Start from Frame 1. Smooth push-in as the pot lands softly in the middle of the frame with a gentle bounce.

[2.5s - 5.0s]: Instant hard cut to the Frame 2 view. Hard cut to a circular camera orbit around the pot showcasing its grooved bottom ridges.

[5.0s - 7.5s]: Snappy whip-pan transition to a brand-new third angle. Snap focus on the flexible soft silicone bending smoothly without deformation, then fast pull-back.

Visual Polish: Miniature stop-motion feel, precise macro depth of field, subtle plastic reflections, flawless scale consistency, no morphing artifacts between cuts, subject stays centered in the safe zone, no text, letters or typography.
```

### Scene 04 - 기능 검증 / 핵심 카타르시스 (22.5~30.0s)

**대사**: 가운데 칸막이로 고기와 감자튀김을 냄새 섞임 없이 동시에 조리하고 기름은 웨이브 바닥으로 쏙 빠집니다.

**Frame 1 (0s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a pastel sage-green platinum silicone round air fryer divider pot with radial wave grooves on the bottom and a central divider wall, a compact round black basket-style air fryer with a silver handle, high-angle shot showing the center divider separating sizzling crispy pork belly on one side and golden french fries on the other, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Frame 2 (2.5s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a pastel sage-green platinum silicone round air fryer divider pot with radial wave grooves on the bottom and a central divider wall, a compact round black basket-style air fryer with a silver handle, medium close-up of hot golden oil draining cleanly down the radial wave grooves away from the food, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Omni 1.2 (I2V, 7.5초)**
```
A continuous 7.5-second vertical 9:16 clip with snappy transitions every 2.5 seconds, consistent visual style, pure visual storytelling without any letters or text:

[0.0s - 2.5s]: Start from Frame 1. Slow tracking glide across both sides of the divider as the food sizzles.

[2.5s - 5.0s]: Instant hard cut to the Frame 2 view. Hard cut to slow-motion golden oil draining down the wave grooves with fluid ripples.

[5.0s - 7.5s]: Snappy whip-pan transition to a brand-new third angle. Snappy whip-pan to an eye-level shot of delicate steam rising from the golden cooked meal.

Visual Polish: Miniature stop-motion feel, precise macro depth of field, subtle plastic reflections, flawless scale consistency, no morphing artifacts between cuts, subject stays centered in the safe zone, no text, letters or typography.
```

### Scene 05 - 반전 펀치라인 / 극적 대비 (30.0~37.5s)

**대사**: 다 먹고 뒤집어서 물로 깨끗이 헹구면 기름이 미끄러지듯 떨어져서 설거지 3초 컷으로 끝납니다.

**Frame 1 (0s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a pastel sage-green platinum silicone round air fryer divider pot with radial wave grooves on the bottom and a central divider wall, a 30-year-old adult PVC figure of a home cook with short brown hair and a cream apron, medium shot of the PVC cook flipping the flexible silicone pot inside-out with an effortless snap, pristine clean surface, all characters are clearly adult, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Frame 2 (2.5s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a pastel sage-green platinum silicone round air fryer divider pot with radial wave grooves on the bottom and a central divider wall, a 30-year-old adult PVC figure of a home cook with short brown hair and a cream apron, medium close-up of a crystal clear water stream splashing over the non-stick surface while oil slides off, all characters are clearly adult, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Omni 1.2 (I2V, 7.5초)**
```
A continuous 7.5-second vertical 9:16 clip with snappy transitions every 2.5 seconds, consistent visual style, pure visual storytelling without any letters or text:

[0.0s - 2.5s]: Start from Frame 1. Fast tracking as the hands flip the pot inside-out with a springy snap.

[2.5s - 5.0s]: Instant hard cut to the Frame 2 view. Hard cut to a high-speed water stream splashing across the surface, oil sliding off in one second.

[5.0s - 7.5s]: Snappy whip-pan transition to a brand-new third angle. Snappy whip-pan to the sparkling clean pot drying on a wooden miniature rack with a gleam effect.

Visual Polish: Miniature stop-motion feel, precise macro depth of field, subtle plastic reflections, flawless scale consistency, no morphing artifacts between cuts, subject stays centered in the safe zone, all characters are clearly adult, no text, letters or typography.
```

### Scene 06 - 결론 / 행동 유도 (CTA) (37.5~45.0s)

**대사**: 오늘만 반값 특가 진행 중이니 놓치면 재고 소진이에요. 제품 정보는 하단 쇼핑 태그와 고정 댓글 확인!

**Frame 1 (0s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a pastel sage-green platinum silicone round air fryer divider pot with radial wave grooves on the bottom and a central divider wall, wide beauty shot of neatly stacked sage green, cream and blush pink silicone pots on a modern clean kitchen island, empty space in the lower area, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Frame 2 (2.5s)**
```
Hyper-detailed collectible PVC figure, premium resin statue texture, visible mold seams, matte paint finish, miniature diorama set, studio macro lighting, tilt-shift photography, a pastel sage-green platinum silicone round air fryer divider pot with radial wave grooves on the bottom and a central divider wall, medium shot of a miniature wooden pointing arrow indicating downward toward the lower safe area, subject centered within the central 70% safe area with 15% negative margin around all edges, pulled-back framing, no extreme close-up --no text, letters, words, typography, subtitles, font, signage, watermark --ar 9:16
```
**Omni 1.2 (I2V, 7.5초)**
```
A continuous 7.5-second vertical 9:16 clip with snappy transitions every 2.5 seconds, consistent visual style, pure visual storytelling without any letters or text:

[0.0s - 2.5s]: Start from Frame 1. Smooth push-in on the stacked colorful pots with a shimmering clean kitchen background.

[2.5s - 5.0s]: Instant hard cut to the Frame 2 view. Hard cut to the wooden arrow bouncing and pointing downward with a playful motion.

[5.0s - 7.5s]: Snappy whip-pan transition to a brand-new third angle. Snappy whip-pan pull-back to a centered wide beauty shot of the whole product set, then hard blackout.

Visual Polish: Miniature stop-motion feel, precise macro depth of field, subtle plastic reflections, flawless scale consistency, no morphing artifacts between cuts, subject stays centered in the safe zone, no text, letters or typography.
```

---
