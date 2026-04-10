---
name: comfyui-engine
description: ComfyUI로 패션 이미지·영상 생성. design-generator/visual-factory 시트 실행. 트리거 "이미지 생성", "시안 뽑아줘", "렌더링".
---

# ComfyUI Engine v2 — 패션 이미지/영상 생성 실행 엔진

> FPOF 크리에이티브 파이프라인의 "실행 레이어".
> 브랜드 DNA를 단일 소스(`references/brand-prompt-kit.json`)에서 주입하고,
> 섹션 타입별 프로파일로 프롬프트 충돌을 방지하며,
> 워크플로우를 자동 선택하여 일관된 결과물을 생산한다.

## When to Use

**v2 핵심 가치**: 브랜드 DNA SSOT 주입 + 섹션별 프로파일 분기 + 워크플로우 자동 선택 + 메타데이터 재현성. (자세한 변경사항은 아래 § "v1 → v2 변경 사항" 표 참조.)

**자동으로 발동해야 하는 상황** (description의 트리거 키워드 외 추가):
- "이미지 생성해줘", "프롬프트 돌려줘", "ComfyUI로 만들어줘", "시안 이미지로 뽑아줘"
- "비주얼 에셋 생성 실행", "영상으로 만들어줘", "프롬프트 시트 실행해줘"
- "디자인 결과물을 이미지로", "생성 AI로 뽑아줘", "렌더링해줘"

**컨텍스트 기반 자동 제안**:
- 프롬프트 시트(`design_generator-sheet.md`, `visual-factory-sheet.md`)가 워크스페이스에 존재하지만 아직 이미지가 생성되지 않은 상태 → 사용자가 명시적으로 요청하지 않아도 이 스킬을 자동으로 제안할 것

## v2.1 추가 (2026-04-10, NotebookLM "패션하우스 AI 프롬프트 디자인 품질 리서치" 반영)

럭셔리 패션하우스(Zegna/Kering/Moncler/G-Star RAW)와 Style3D/Onbrand PLM 가이드 180개 소스를 분석한 리서치 기반 5대 기능:

1. **Foundation Formula 7슬롯** — `brand-prompt-kit.json`의 `foundation_formula` 섹션이 정의하는 구조화 프롬프트: `[샷]+[실루엣]+[소재]+[디테일]+[색상]+[제작방식]+[조명·품질]`. `PromptComposer.compose_foundation_formula()`가 조립. CLI: `--shot / --silhouette / --material / --details / --color-slot / --construction / --lighting-quality`
2. **Material Intelligence 사전** — `references/material-intelligence.json`에 소재 25종 × primary_keywords / optical_properties / drape_behavior 수록. `--material french_terry_brushed` 처럼 키로 지정하면 소재별 전문 용어가 자동 주입됨. 디버그: `python3.12 scripts/prompt_composer.py materials`
3. **Style Lock (컬렉션 일관성)** — `--style-lock <name>`으로 seed + sampler + scheduler + cfg + steps + ref_image + lighting_quality를 컬렉션 단위로 고정. 첫 호출 시 `~/.comfyui-engine/style-locks/<name>.json`에 저장되고 이후 재사용. 빌트인 프리셋: `wacky_street_26ss`, `trusted_comfort_wellness`, `flat_tech_pack` (brand-prompt-kit.json의 `style_lock_presets`)
4. **Iterate (BUG 벤치마크 반복 수정)** — `--iterate <prev_image> --revise "수정 지시"`로 이전 이미지를 ref로 삼아 수정본 생성. 출력 파일명에 `_iter<N>` 자동 suffix, 부모 메타의 seed 자동 상속, 메타데이터에 `parent_image/iteration/revise_directive` 기록. 자동으로 `moodboard` 워크플로우(IPAdapter)로 라우팅
5. **ControlNet 구조 제어 (`structure_control` 섹션)** — 새 워크플로우 3종:
   - `controlnet/sdxl_canny_structure.json` — 봉제선·카라·실루엣 락 (strength 0.85)
   - `controlnet/sdxl_depth_drape.json` — MiDaS depth 기반 드레이프/볼륨 제어 (strength 0.75)
   - `controlnet/sdxl_softedge_material_swap.json` — HED SoftEdge, 기존 텍스처 유지하며 소재/색상만 교체 (strength 0.65)

   → 사용: `--section-type structure_control --ref-image <ref.png> --phase-limit 2 --prompt "..."`

**남은 Phase 3+ 항목** (이번 리팩토링 범위 외, 별도 세션 필요): 브랜드 LoRA 학습, IP 캐릭터 LoRA, Living Tech Pack 통합, 윤리·저작권 가이드라인 문서.

## v1 → v2 변경 사항 (요약)

| 영역 | v1 | v2 |
|------|-----|-----|
| 브랜드 부스터 | `generate.py`에 하드코딩 | `references/brand-prompt-kit.json` SSOT |
| 플랫 스케치 | 컬러 부스터 충돌 | `section_type=flat_sketch`에서 부스터 자동 OFF |
| 시트 파서 | 정규식 (첫 블록만) | 마크다운 AST (복수 코드블록 전부) |
| 워크플로우 선택 | 사용자 지정 | section_type + channel + ref 유무로 자동 선택 |
| 해상도 | 수동 `--width --height` | 채널 → SDXL 해상도 자동 매핑 |
| IPAdapter API | 구형 `IPAdapterApply` (깨짐) | `IPAdapterUnifiedLoader + IPAdapterAdvanced` v2 |
| 메타데이터 | 없음 | 모든 이미지에 `*.meta.json` 동반 저장 |
| 재현성 | 없음 | `--from-meta` 모드 |
| 시트 상태 | 문서 약속만 | `PROMPT → GENERATED` 자동 갱신 |
| 섹션 타입 | 단순 추론 | 5종 (flat_sketch/lookbook/graphic/moodboard/colorway) 프로파일 |

## 아키텍처

```
[브랜드 프리셋] system/presets/wacky-willy/
  visual-identity.json + ip-bible.json + tone-manner.json
            │
            ▼
[SSOT] references/brand-prompt-kit.json  +  references/section-profiles.json
            │
            ▼
[design-generator] / [visual-factory]  →  prompt sheet (.md)
            │
            ▼
┌─ comfyui-engine v2 ─────────────────────────────────┐
│  sheet_parser.py    → 마크다운 AST → 엔트리 리스트  │
│  workflow_resolver.py → section+channel+ref → 워크플로우 │
│  prompt_composer.py  → positive/negative/샘플러     │
│  generate.py        → ComfyUI 큐 → 메타데이터 저장  │
│  sheet_state.py     → PROMPT → GENERATED 갱신      │
└────────────────────────────────────────────────────┘
            │
            ▼
workspace/[시즌]/[프로젝트]/generated/
  000_v1-front.png + 000_v1-front.meta.json
  ...
  report.md (자동 생성)
```

## 전제 조건

ComfyUI가 설치되어 있어야 한다. 설치 안 됐으면 먼저 셋업:

```bash
bash "<this-skill-dir>/scripts/setup.sh"              # Tier 2 (기본)
bash "<this-skill-dir>/scripts/setup.sh" --tier slim  # Tier 1 + RealVisXL V5 + Lightning LoRA + 4xUltraSharp
```

서버 시작 / 상태 확인:

```bash
bash "<this-skill-dir>/scripts/server_ctl.sh" start
bash "<this-skill-dir>/scripts/server_ctl.sh" status
```

서버가 `http://127.0.0.1:8188`에서 응답하면 준비 완료.

## Python 실행 환경

스크립트는 `sheet_parser.py` (mistune 의존) 와 `resize_channel.py` (Pillow 의존) 를 포함하는데,
해당 패키지는 `~/ComfyUI/venv` 안에만 설치되어 있다.

**신경쓸 필요 없다** — `scripts/_bootstrap.py` 가 시스템 `python3.12` 로 스크립트가 실행될 때
필요한 모듈이 없으면 자동으로 `~/ComfyUI/venv/bin/python` 으로 재실행한다.
그래서 아래 두 방식 모두 동작한다:

```bash
# A. 시스템 python3.12 (권장, 부트스트랩이 자동 처리)
python3.12 "<this-skill-dir>/scripts/generate.py" --section-type lookbook ...

# B. venv python 직접 지정 (명시적)
"$HOME/ComfyUI/venv/bin/python" "<this-skill-dir>/scripts/generate.py" ...
```

새 터미널에서 동작 검증:
```bash
bash "<this-skill-dir>/tests/smoke/run_smoke.sh"
```

## 섹션 타입 (section_type)

v2의 핵심 개념. 사용자가 무엇을 만들고 싶은지에 따라 프로파일이 달라진다.

| 섹션 | 용도 | 브랜드 부스터 | 기본 샘플러 | 기본 해상도 |
|------|------|-------------|-----------|------------|
| `flat_sketch` | 기술 도식화 (무채색 선화) | **OFF** | euler / normal / cfg 5.0 | 1024×1024 |
| `lookbook` | 모델 착장 에디토리얼 | ON | dpmpp_2m / karras / cfg 6.5 | 832×1216 |
| `graphic` | 프린트/자수 원고 | ON | euler_ancestral / cfg 7.5 | 1024×1024 |
| `moodboard` | 스타일 레퍼런스 기반 | ON | dpmpp_2m / karras / cfg 6.0 | 1024×1024 |
| `colorway` | 동일 아이템 컬러 배리에이션 | ON (고정 시드) | dpmpp_2m / karras / cfg 6.0 | 1024×1024 |

프로파일 상세: `references/section-profiles.json`

## 워크플로우 카탈로그

워크플로우는 **의도별 디렉토리**로 정리되어 있고 `references/workflow-catalog.json`이 선택 규칙을 정의한다.

```
workflows/
├── flat-sketch/sdxl_flat_linework.json
├── lookbook/
│   ├── sdxl_street_hires.json              ← Phase 1 balanced (SDXL Base)
│   └── sdxl_realvis_lightning.json         ← Phase 2 fast (RealVisXL V5 + Lightning LoRA 4-step)
├── moodboard/sdxl_ipadapter_v2.json        ← IPAdapter API v2 (C3 버그 수정)
├── graphic/sdxl_print_vector.json
├── colorway/sdxl_fixed_seed_swap.json
└── legacy/                                 ← v1 아카이브 (롤백용)
    ├── txt2img_sdxl.json
    ├── controlnet_canny.json
    ├── ipadapter_style.json
    └── img2vid_svd.json
```

**WorkflowResolver**가 `section_type + channel + ref_image 유무 + model_family + phase_limit + speed`로 최적 워크플로우를 자동 선택한다.

**속도 프로파일 (`--speed`)**:
- `balanced` (기본): 30-step 샘플링, 장당 ~30-60초. 최고 품질.
- `fast`: `--phase-limit 2` 와 함께 지정 시 RealVisXL + Lightning LoRA 4-step 활성화, 장당 ~5-10초.

**해상도 주의**: 채널 → SDXL 생성 해상도 매핑은 SDXL 학습 해상도(8의 배수)에 맞춘 근사치다.
예: `musinsa_hero` → `3:4` → 생성 시 **896×1152**, 최종 업로드 시 `resize_channel.py --channel musinsa_hero` 로 **860×1148** 로 맞춘다.

## 사용법

### 모드 0: 디자인 디스커버리 (Discovery / Ideation)

**언제**: 사용자가 "여름용 뭔가 만들고 싶은데…" "힙한 후디 하나 떠올려볼래?" 같이 **아이디어가 아직 구체화되지 않은** 상태에서 이 스킬에 들어왔을 때. 키워드만 있고 섹션/실루엣/소재/컬러 무드가 비어있을 때의 기본 진입 모드다.

**핵심 원리**: 질문 트리(`references/design-discovery-flow.json`)를 Claude 가 순차적으로 AskUserQuestion 으로 렌더링해 Foundation Formula 7슬롯 브리프를 수집한 뒤, `scripts/brief_compose.py` 로 `generate.py` 를 호출한다. 옵션 후보는 절대 지어내지 말고 브랜드 프리셋/프롬프트 킷에서 동적으로 로드한다.

**실행 흐름**:

1. `references/design-discovery-flow.json` 을 Read 로 로드.
2. `steps` 배열을 순서대로 순회. 각 스텝마다:
   - `skip_if` 조건이 현재까지 수집된 brief 상태와 매치되면 건너뛴다.
     (예: `section_type=graphic` 이면 silhouette/material/shot/lighting_quality 스텝 스킵)
   - `options_source` 가 `"inline"` 이면 스텝의 `options` 를 그대로 사용.
   - `options_source` 가 `"dynamic"` 이면 `source_file` 을 Read 하고 `source_rule` 에 따라 옵션을 조립한다. 필요 시 `filter_by_category` / `hint_subset_by_category` 로 사용자가 고른 카테고리에 맞게 좁힌다. source 파일 로드에 실패하면 `options_fallback` 을 사용.
   - AskUserQuestion 으로 `question` / `header` / `multiSelect` / `options` 를 전달.
   - 사용자 답변 value 를 `brief[maps_to]` 에 저장.
   - `optional: true` 이고 사용자가 `__none__` 을 선택하면 해당 필드를 brief 에 넣지 않는다.
3. 모든 스텝 완료 후 수집된 brief 를 요약해 보여주고 "이대로 생성할까요? (생성 / 수정 / 취소)" 를 AskUserQuestion 으로 확인.
4. 사용자가 "수정" 하면 어느 필드를 바꿀지 묻고 해당 스텝만 다시 실행.
5. "생성" 승인되면:
   - brief 를 `workspace/[시즌]/[프로젝트]/brief_[timestamp].json` 으로 저장.
   - `python3.12 scripts/brief_compose.py --brief <path>` 실행.
   - brief_compose.py 가 내부적으로 `generate.py` 를 Foundation Formula 모드로 호출한다.
6. 결과 이미지가 만족스럽지 않으면 메타데이터 기반으로 seed 유지 + 일부 필드만 교체해 재생성 (동일 brief 의 특정 스텝만 rerun → 다시 brief_compose.py).

**옵션 소스 매핑** (Claude 가 각 스텝의 `source_file` + `source_rule` 을 해석할 때):

| 스텝 | source_file | source_rule 요약 |
|------|-------------|------------------|
| category | `system/presets/wacky-willy/categories.json` | `lines[].sub_categories[]` 를 flatten, `{line_id}_{sub_id}` 가 value |
| silhouette | `references/brand-prompt-kit.json` | `foundation_formula.silhouette_templates` 키 전체, `filter_by_category` 로 카테고리에 맞게 서브셋 |
| material | `references/material-intelligence.json` | `materials` 전체, `hint_subset_by_category` 로 카테고리 우선 추천 |
| details | `references/brand-prompt-kit.json` | `foundation_formula.details_options` 키 전체 |
| lighting_quality | `references/brand-prompt-kit.json` | `foundation_formula.lighting_quality_tags` 키 전체 |
| shot | `references/brand-prompt-kit.json` | `foundation_formula.shot_type_options` 키 전체 |

**스킵 규칙 요약**:

| section_type | 스킵되는 스텝 |
|--------------|-------------|
| `flat_sketch` | color, lighting_quality, shot, style_lock |
| `graphic` | category, silhouette, material, details, lighting_quality, shot |
| `moodboard` | category, silhouette, details (+ ref_image 입력 추가 요청) |
| `colorway` | — (모든 스텝 진행, 단 --seed 고정 권장) |
| `lookbook` | — (전체 스텝) |

**예시 흐름** (사용자: "여름용 후디 하나 디자인해볼래?"):

```
Claude → design-discovery-flow.json 로드
Claude → Q1: 무엇을 만들까요? → 사용자: "착장 룩"                   → section_type=lookbook
Claude → Q2: 카테고리? → 사용자: "유니섹스 상의"                      → category=unisex_tops
Claude → Q3: 실루엣? (categories 로 필터링된 4개 옵션)
          → 사용자: "오버사이즈 후디"                                → silhouette=oversized_hoodie
Claude → Q4: 소재? (tops 카테고리 힌트 서브셋)
          → 사용자: "french terry brushed"                           → material=french_terry_brushed
Claude → Q5: 디테일? → 사용자: "signature stitching"                → details=signature_stitching
Claude → Q6: 컬러? → 사용자: "시그니처 옐로우 도미넌트"                → color="signature canary yellow..."
Claude → Q7: 조명/씬? → 사용자: "golden hour"                       → lighting_quality=golden_hour
Claude → Q8: 샷 앵글? → 사용자: "three-quarter"                     → shot=three_quarter
Claude → Q9: 채널? → 사용자: "무신사 대표"                           → channel=musinsa_hero
Claude → Q10: 스타일 락? → 사용자: "Wacky Street 26SS"               → style_lock=wacky_street_26ss
Claude → 브리프 요약 → 사용자: "생성"
Claude → workspace/26ss/summer-hoodie/brief_20260410-1432.json 저장
Claude → Bash: python3.12 scripts/brief_compose.py --brief <path>
          → brief_compose.py 검증 → generate.py --section-type lookbook \
             --shot three_quarter --silhouette oversized_hoodie \
             --material french_terry_brushed --details signature_stitching \
             --color-slot "signature canary yellow..." \
             --lighting-quality golden_hour --channel musinsa_hero \
             --style-lock wacky_street_26ss --output <out.png>
```

**원칙**:
- 질문은 한 번에 하나씩만 렌더링 (사용자 피로도 최소화).
- 옵션 라벨은 한국어, value 는 generate.py 가 인식하는 영문 키.
- 절대 옵션을 지어내지 말 것 — 항상 source_file 에서 로드. 로드 실패 시 `options_fallback` 사용.
- 사용자가 "직접 입력"을 원하면 AskUserQuestion 의 자유 텍스트로 받아 자유 텍스트 value 로 저장 (generate.py 가 자유 텍스트 fallback 을 지원).
- brief 는 반드시 workspace 에 저장 — 재현/히스토리 추적용.

**결과물**:
- `workspace/[시즌]/[프로젝트]/brief_*.json` — 수집된 brief
- `workspace/[시즌]/[프로젝트]/*.png` + `*.meta.json` — 생성 이미지 + 재현 메타
- brief_compose.py 로 언제든 동일 brief 재실행 가능

---

### 모드 0-Quick: 의도 선택 (Quick Intent)

**언제**: 사용자가 이미 무엇을 만들지는 알지만 섹션/채널 같은 기본 파라미터만 확인이 필요할 때. Full Discovery 가 과할 때의 단축 경로.

사용자 요청이 모호하면 먼저 의도를 묻는다:

```json
{
  "questions": [
    {
      "question": "무엇을 생성할까요?",
      "header": "섹션 타입",
      "multiSelect": false,
      "options": [
        {"label": "플랫 스케치", "description": "기술 도식화 — 무채색 선화, 봉제선·디테일 중심"},
        {"label": "착장 룩", "description": "모델 에디토리얼 — 한국 20대, 거리 현장감"},
        {"label": "그래픽/프린트", "description": "벡터 스타일 원고 — 프린트·자수용"},
        {"label": "무드보드", "description": "레퍼런스 이미지 기반 스타일 전이"},
        {"label": "컬러웨이 배리에이션", "description": "동일 아이템 컬러 교체"}
      ]
    }
  ]
}
```

이어서 **채널**을 묻는다 (해상도 자동 결정):

```json
{
  "questions": [
    {
      "question": "어떤 채널/용도로 생성할까요?",
      "header": "출력 채널",
      "multiSelect": false,
      "options": [
        {"label": "원본 (1024×1024)", "description": "후속 리사이즈 가능"},
        {"label": "무신사 대표 (860×1148)", "description": "외부몰 PDP"},
        {"label": "인스타 피드 (1080×1080)", "description": "정사각 피드"},
        {"label": "인스타 스토리 (1080×1920)", "description": "세로형 릴스"},
        {"label": "룩북 전신 (2000×3000)", "description": "고해상도 에디토리얼"},
        {"label": "자사몰 히어로 (1920×800)", "description": "메인 배너"},
        {"label": "자사몰 PDP (1000×1300)", "description": "상품 상세"}
      ]
    }
  ]
}
```

### 모드 1: 직접 프롬프트 실행

```bash
python3.12 "<this-skill-dir>/scripts/generate.py" \
  --section-type lookbook \
  --channel musinsa_hero \
  --prompt "Korean male model wearing oversized graphic hoodie" \
  --output "<workspace>/output_001.png"
```

주요 인자:
- `--section-type` (필수): flat_sketch | lookbook | graphic | moodboard | colorway
- `--channel`: 채널명 (해상도 자동 결정)
- `--prompt`: 이미지 생성 프롬프트 (영문)
- `--negative`: 네거티브 오버라이드 (기본은 섹션 프로파일)
- `--ref-image`: 참조 이미지 (moodboard/controlnet 시 필수)
- `--ref-strength`: 참조 강도 0.0~1.0 (기본 0.7)
- `--width`, `--height`: 해상도 직접 지정 (CLI가 최우선)
- `--seed`: 재현 가능한 시드
- `--output`: 출력 경로
- `--model-family`: sdxl (기본) | flux (Phase 2 이후)
- `--phase-limit`: 워크플로우 phase 상한 (기본 1)
- `--workflow-rel`: 워크플로우 직접 지정 (예: `lookbook/sdxl_street_hires.json`)
- `--dry-run`: 실제 생성 없이 프롬프트 미리보기
- `--from-meta`: 메타데이터 JSON으로 재현 생성

### 모드 2: 프롬프트 시트 배치 실행

기존 스킬이 생성한 시트를 파싱하여 일괄 실행:

```bash
python3.12 "<this-skill-dir>/scripts/batch_generate.py" \
  --sheet "<workspace>/design_generator-sheet.md" \
  --output-dir "<workspace>/generated/" \
  --default-channel musinsa_hero
```

v2 파서(SheetParser)가:
1. 마크다운 AST로 헤더 계층을 이해한다 (Front/Back/Detail 3뷰 전부 잡음)
2. 섹션 헤더 텍스트에서 `section_type`을 추론한다
3. 인라인 메타 주석 `<!-- workflow: ... -->`, `<!-- channel: ... -->`, `<!-- seed: 12345 -->` 지원
4. YAML front-matter로 시트 공통 설정 지정 가능

배치 완료 후:
- 모든 이미지 옆에 `*.meta.json` 동반 저장
- 시트의 에셋 매트릭스가 `PROMPT → GENERATED`로 자동 갱신
- `generated/report.md` 자동 생성 (섹션별 집계, 성공/실패 상세)

### 모드 3: 채널별 리사이즈

```bash
python3.12 "<this-skill-dir>/scripts/resize_channel.py" \
  --input "<image>" \
  --channel musinsa_hero \
  --output "<resized>"
```

### 모드 4: 재현 (메타데이터 기반)

```bash
python3.12 "<this-skill-dir>/scripts/generate.py" \
  --from-meta "<existing>.meta.json" \
  --output "<repro>.png"
```

메타데이터 JSON에서 모든 파라미터(seed, prompt, workflow, 샘플러 등)를 로드하여 동일 이미지 재현.

## 실행 절차 (Claude가 따를 순서)

### 1. 서버 상태 확인
```bash
bash "<this-skill-dir>/scripts/server_ctl.sh" status
```
응답 없으면 시작 안내 또는 직접 시작.

### 2. 입력 분석
- **프롬프트 시트**: SheetParser로 파싱 → 섹션 타입별 엔트리 확인
- **직접 요청**: 사용자 의도 파악 → section_type / channel 결정 (AskUserQuestion)

### 3. Dry-run으로 프롬프트 미리보기
```bash
python3.12 generate.py --section-type ... --prompt "..." --dry-run
```
사용자가 positive/negative/해상도/워크플로우 확인.

### 4. 실제 생성 실행
generate.py 또는 batch_generate.py 실행. 진행 상황을 사용자에게 알린다.

### 5. 메타데이터 확인
각 이미지 옆의 `*.meta.json`으로 재현성 보장.

### 6. 채널 규격 리사이즈 (선택)
resize_channel.py로 최종 채널 해상도로 변환.

## 브랜드 프롬프트 킷 (SSOT)

`references/brand-prompt-kit.json`은 와키윌리 브랜드 DNA의 단일 진실 원천:

- **style_tokens**: 필수/회피 스타일 토큰
- **color_tokens**: 시그니처 컬러 HEX + 디스크립터
- **subject_priors**: 한국 20대 모델 묘사 + 회피 키워드
- **photo_direction**: setting / lighting / camera 옵션
- **ip_characters**: KIKY, 릴리, 레오 등 캐릭터 기본 묘사
- **brand_negative**: 브랜드 금기 (3B 착장, 로고 변형 등)
- **never_use_words**: tone-manner.json의 금지 어휘

브랜드 프리셋이 바뀌면 이 JSON을 재동기화하면 되고, 코드 변경은 불필요하다.

## 트러블슈팅

| 문제 | 해결 |
|------|------|
| 서버 시작 안 됨 | `server_ctl.sh status`, 포트 확인 `lsof -i :8188` |
| 메모리 부족 | Activity Monitor 확인. SDXL은 ~12GB 필요 |
| 생성 느림 | M4 Pro에서 1024² 기준 ~30-60초/장. `--steps` 줄이면 빨라짐 |
| 모델 로드 에러 | `~/ComfyUI/models/checkpoints/` 확인 |
| IPAdapter 노드 에러 | 구형 `IPAdapterApply` 사용 중일 수 있음. `ComfyUI_IPAdapter_plus` 저장소 git pull |
| 시트 파서가 빈 리스트 반환 | `pip install mistune` 확인. `python3.12 sheet_parser.py <sheet.md>` 디버그 모드로 직접 실행 |
| 플랫 스케치가 컬러풀하게 나옴 | `--section-type flat_sketch` 사용 확인. v2에서는 brand_booster가 자동 OFF됨 |
| 채널 해상도가 적용 안 됨 | `--channel musinsa_hero` 등 `workflow-catalog.json`의 `channel_to_ratio`에 정의된 이름 사용 |
| 롤백 필요 | `workflows/legacy/`의 v1 워크플로우를 `--workflow-rel legacy/txt2img_sdxl.json`로 직접 지정 가능 |

## 모델 구성 (setup.sh가 설치)

| Tier | 모델 | 용량 | 용도 |
|------|------|------|------|
| 1 (기본) | SDXL Base 1.0 + VAE fp16 fix | ~7.3GB | 메인 이미지 생성 |
| 2 (lifestyle) | + ControlNet Canny + IP-Adapter Plus + CLIP-ViT-H-14 | ~+7.2GB | 레퍼런스 기반 |
| 2.5 (Phase 2, 옵션 A) | + 4xUltraSharp + 4x-AnimeSharp | +130MB | ESRGAN 업스케일 |
| 3 (Phase 2, 옵션 A) | + Juggernaut XL v10 + SDXL Refiner 1.0 | +13GB | 실사 품질 향상 |
| Flux (Phase 2, 옵션 B/C) | + FLUX.1-dev + T5-XXL + CLIP-L + ae.sft | +33GB | 최고 품질 (옵션) |

## 스크립트 참조

| 스크립트 | 용도 |
|---------|------|
| `scripts/setup.sh` | ComfyUI 설치 + 모델 다운로드 (`--tier 1|2|3|slim`) |
| `scripts/server_ctl.sh` | ComfyUI 서버 제어 (`start|stop|status`) |
| `scripts/_bootstrap.py` | venv 자동 전환 헬퍼 — 시스템 python 실행 시 `~/ComfyUI/venv` 로 re-exec |
| `scripts/comfyui_client.py` | ComfyUI HTTP API 클라이언트 |
| `scripts/sheet_parser.py` | 마크다운 AST 기반 시트 파서 (v2, `table_keys` 포함) |
| `scripts/prompt_composer.py` | 브랜드 SSOT 기반 프롬프트 조립기 (v2) |
| `scripts/workflow_resolver.py` | 워크플로우 자동 선택기 (v2, `speed` 지원) |
| `scripts/metadata_store.py` | 이미지 메타데이터 저장/재현 (v2) |
| `scripts/sheet_state.py` | 시트 상태 머신 업데이트 (v2, 다중 키 매칭) |
| `scripts/generate.py` | 단일 이미지 생성 (v2) |
| `scripts/brief_compose.py` | 디자인 디스커버리 브리프 → generate.py 실행기 (모드 0 핸드오프) |
| `scripts/batch_generate.py` | 프롬프트 시트 배치 생성 (v2) |
| `scripts/resize_channel.py` | 채널별 리사이즈 (Pillow) |
| `scripts/upscale.py` | 4xUltraSharp ESRGAN 업스케일 (Phase 2-Slim) |
| `tests/smoke/run_smoke.sh` | 서버 없이 dry-run 기반 회귀 스모크 테스트 |

## 참조 파일

| 파일 | 용도 |
|------|------|
| `references/brand-prompt-kit.json` | 와키윌리 브랜드 DNA SSOT |
| `references/section-profiles.json` | 섹션 타입별 프로파일 |
| `references/workflow-catalog.json` | 워크플로우 선택 규칙 + 채널↔비율 매핑 |
| `references/channel-specs.json` | 리사이즈 채널 규격 |
| `references/design-discovery-flow.json` | 모드 0 디자인 디스커버리 질문 트리 (10-step) |
| `references/material-intelligence.json` | 소재 프롬프트 사전 (material 슬롯 조회) |
