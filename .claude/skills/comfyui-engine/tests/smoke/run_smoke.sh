#!/bin/bash
# ComfyUI Engine v2 smoke test
#
# 서버 없이 dry-run 만으로 composer / resolver / sheet_parser / batch 의 핵심 경로를
# 빠르게 검증한다. 실패 시 즉시 종료하고 에러를 그대로 보여준다.
#
# 사용법: bash tests/smoke/run_smoke.sh
# 종료 코드: 0 성공, 1 실패

set -e

SKILL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$SKILL_DIR"

# venv python 우선 — 인라인 `python -c "..."` 테스트를 위해서는 venv 직접 사용 필수.
# 이유: -c 모드에서 sys.argv[0]=='-c' 이라 _bootstrap 재실행이 불가능 (argv 에서 스크립트 본문 손실).
# 스크립트 파일 실행 (generate.py 등)은 bootstrap 이 정상 처리하므로 시스템 python 도 동작한다.
VENV_PY="$HOME/ComfyUI/venv/bin/python"
if [[ -x "$VENV_PY" ]]; then
    PY="${PY:-$VENV_PY}"
else
    PY="${PY:-python3.12}"
fi

echo "========================================"
echo "  ComfyUI Engine v2 — Smoke Test"
echo "  Skill dir: $SKILL_DIR"
echo "  Python: $PY"
echo "========================================"

pass=0
fail=0

run_test() {
    local name="$1"
    shift
    echo
    echo "── [$name] ──"
    if "$@" > /tmp/fpof_smoke.log 2>&1; then
        echo "  PASS"
        pass=$((pass + 1))
    else
        echo "  FAIL"
        cat /tmp/fpof_smoke.log
        fail=$((fail + 1))
    fi
}

# 1. 모든 파이썬 스크립트 바이트 컴파일
run_test "py_compile all scripts" \
    $PY -m py_compile \
    scripts/_bootstrap.py \
    scripts/batch_generate.py \
    scripts/comfyui_client.py \
    scripts/generate.py \
    scripts/metadata_store.py \
    scripts/prompt_composer.py \
    scripts/resize_channel.py \
    scripts/sheet_parser.py \
    scripts/sheet_state.py \
    scripts/upscale.py \
    scripts/workflow_resolver.py

# 2. 모든 워크플로우 JSON 파싱
run_test "workflow JSON parse" \
    $PY -c "
import json, sys
from pathlib import Path
cat = json.load(open('references/workflow-catalog.json'))
for rel in cat['workflows'].keys():
    p = Path('workflows') / rel
    assert p.exists(), f'Missing workflow file: {rel}'
    json.load(open(p))
print('OK', len(cat['workflows']), 'workflows')
"

# 3. Resolver — 5개 섹션 전부
run_test "resolver flat_sketch" \
    $PY scripts/workflow_resolver.py flat_sketch
run_test "resolver lookbook+channel" \
    $PY scripts/workflow_resolver.py lookbook musinsa_hero
run_test "resolver graphic" \
    $PY scripts/workflow_resolver.py graphic
run_test "resolver colorway" \
    $PY scripts/workflow_resolver.py colorway
run_test "resolver moodboard with ref" \
    $PY scripts/workflow_resolver.py moodboard "" /tmp/ref.png

# 4. Composer — 섹션별 브랜드 부스터 on/off 검증
run_test "composer flat_sketch booster off" \
    $PY -c "
import sys; sys.path.insert(0,'scripts')
from prompt_composer import PromptComposer
c = PromptComposer().compose('test prompt', 'flat_sketch')
assert 'kitsch street fashion' not in c['positive'], 'brand booster must be OFF for flat_sketch'
assert 'canary yellow' not in c['positive'], 'color tokens must be OFF for flat_sketch'
print('OK flat_sketch')
"
run_test "composer lookbook booster on" \
    $PY -c "
import sys; sys.path.insert(0,'scripts')
from prompt_composer import PromptComposer
c = PromptComposer().compose('test prompt', 'lookbook')
assert 'kitsch street fashion' in c['positive'], 'brand booster must be ON for lookbook'
assert 'canary yellow' in c['positive'], 'color tokens must be ON for lookbook'
assert 'Korean model' in c['positive'], 'subject priors must be ON for lookbook'
print('OK lookbook')
"

# 5. Sheet parser — 12 엔트리 + table_keys
run_test "sheet_parser fixture 12 entries" \
    $PY -c "
import sys; sys.path.insert(0,'scripts')
from sheet_parser import SheetParser
entries = SheetParser().parse('tests/fixtures/sample_sheet_4x3.md')
assert len(entries) == 12, f'expected 12 entries, got {len(entries)}'
# table_keys 존재 확인
for e in entries:
    assert 'table_keys' in e
    assert len(e['table_keys']) >= 1
# 첫 엔트리: 'V1 정면 (Front)' → table_keys 에 '정면 (Front)' 와 'V1 키키 그래픽 오버사이즈 후디' 가 들어있어야 함
first = entries[0]
assert 'V1 정면 (Front)' in first['table_keys']
assert '정면 (Front)' in first['table_keys']
print('OK 12 entries, table_keys present')
"

# 6. sheet_state — 매칭 성공 (table_keys 우회)
run_test "sheet_state match via table_keys" \
    $PY -c "
import sys, tempfile, shutil
sys.path.insert(0,'scripts')
from sheet_parser import SheetParser
from sheet_state import update_many
with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False) as tf:
    shutil.copyfile('tests/fixtures/sample_sheet_4x3.md', tf.name)
    tmp = tf.name
entries = SheetParser().parse(tmp)
result = update_many(tmp, entries, new_state='GENERATED')
assert result['updated'] == 12, f'expected 12 updates, got {result}'
assert len(result['missed']) == 0
print('OK all 12 entries matched')
"

# 7. generate.py dry-run — 5 섹션
run_test "generate dry-run flat_sketch" \
    $PY scripts/generate.py --section-type flat_sketch --prompt "front view hoodie" --dry-run
run_test "generate dry-run lookbook+channel" \
    $PY scripts/generate.py --section-type lookbook --channel musinsa_hero --prompt "oversized hoodie" --dry-run
run_test "generate dry-run lookbook+fast (Lightning)" \
    $PY scripts/generate.py --section-type lookbook --phase-limit 2 --speed fast --prompt "oversized hoodie" --dry-run
run_test "generate dry-run graphic" \
    $PY scripts/generate.py --section-type graphic --prompt "kiky print sticker" --dry-run

# 8. batch_generate dry-run 전체
run_test "batch_generate dry-run fixture" \
    $PY scripts/batch_generate.py --sheet tests/fixtures/sample_sheet_4x3.md --output-dir /tmp/fpof_smoke_out --dry-run --no-sheet-update

# ─────────────────────────────────────────────
# 9. v2.1 추가 — Foundation Formula / Material Intelligence / Style Lock / Iterate / ControlNet
# ─────────────────────────────────────────────

# 9a. material-intelligence.json 로드 + 25개 엔트리
run_test "v2.1 material-intelligence catalog 25 entries" \
    $PY -c "
import sys; sys.path.insert(0,'scripts')
from prompt_composer import PromptComposer
composer = PromptComposer()
mats = composer.list_materials()
assert len(mats) >= 25, f'expected >=25 materials, got {len(mats)}'
assert 'french_terry_brushed' in mats
assert 'velvet' in mats
# lookup 동작
entry = composer.look_up_material('french_terry_brushed')
assert entry is not None
assert 'primary_keywords' in entry
assert len(entry['primary_keywords']) >= 3
print(f'OK {len(mats)} materials')
"

# 9b. Foundation Formula compose_foundation_formula()
run_test "v2.1 composer.foundation_formula lookbook" \
    $PY -c "
import sys; sys.path.insert(0,'scripts')
from prompt_composer import PromptComposer
c = PromptComposer().compose_foundation_formula(
    section_type='lookbook',
    shot_type='three_quarter',
    silhouette='oversized_hoodie',
    material='french_terry_brushed',
    details='signature_stitching',
    construction='premium_manufacture',
    lighting_quality='golden_hour',
)
# 7슬롯이 실제로 주입됐는지 확인
assert 'three-quarter angle shot' in c['positive']
assert 'oversized relaxed-fit hoodie' in c['positive']
assert 'brushed french terry interior' in c['positive']  # material lookup
assert 'contrast topstitching' in c['positive']
assert 'premium garment construction' in c['positive']
assert 'warm golden hour natural light' in c['positive']
# 품질 태그 꼬리
assert '8K texture detail' in c['positive']
# 브랜드 SSOT 주입 확인
assert 'kitsch street fashion' in c['positive']
print('OK 7슬롯 Foundation Formula')
"

# 9c. Foundation Formula + flat_sketch에서 브랜드 부스터 OFF 보존
run_test "v2.1 foundation_formula flat_sketch booster off" \
    $PY -c "
import sys; sys.path.insert(0,'scripts')
from prompt_composer import PromptComposer
c = PromptComposer().compose_foundation_formula(
    section_type='flat_sketch',
    shot_type='product_hero',
    silhouette='oversized_hoodie',
)
assert 'kitsch street fashion' not in c['positive'], 'booster should stay OFF for flat_sketch'
assert 'canary yellow' not in c['positive'], 'color tokens should stay OFF for flat_sketch'
print('OK flat_sketch 보존')
"

# 9d. structure_control 라우팅 (ref 필요)
run_test "v2.1 resolver structure_control → canny workflow" \
    $PY -c "
import sys; sys.path.insert(0,'scripts')
from workflow_resolver import WorkflowResolver
r = WorkflowResolver().resolve(
    section_type='structure_control',
    ref_image='/tmp/fake.png',
    phase_limit=2,
)
assert 'controlnet/' in r['workflow_rel']
assert r['meta']['intent'] == 'structure_control'
print('OK', r['workflow_rel'])
"

# 9e. 모든 ControlNet 워크플로우 JSON이 유효한가
run_test "v2.1 controlnet workflows parse" \
    $PY -c "
import json
from pathlib import Path
for rel in ['controlnet/sdxl_canny_structure.json', 'controlnet/sdxl_depth_drape.json', 'controlnet/sdxl_softedge_material_swap.json']:
    p = Path('workflows') / rel
    assert p.exists(), f'missing {rel}'
    wf = json.load(open(p))
    # 필수 노드 체크
    classes = {n['class_type'] for n in wf.values() if isinstance(n, dict) and 'class_type' in n}
    assert 'CLIPTextEncode' in classes
    assert 'KSampler' in classes
    assert 'ControlNetLoader' in classes
    assert 'ControlNetApplyAdvanced' in classes
    assert 'LoadImage' in classes
print('OK 3 controlnet workflows')
"

# 9f. generate dry-run — Foundation Formula 단독 실행
run_test "v2.1 generate dry-run foundation_formula only" \
    $PY scripts/generate.py \
        --section-type lookbook \
        --shot three_quarter \
        --silhouette oversized_hoodie \
        --material french_terry_brushed \
        --lighting-quality golden_hour \
        --dry-run

# 9g. generate dry-run — 빌트인 style-lock preset 로드
run_test "v2.1 generate dry-run style-lock builtin preset" \
    $PY scripts/generate.py \
        --section-type lookbook \
        --style-lock trusted_comfort_wellness \
        --prompt "test wellness hoodie" \
        --dry-run

# 9h. generate dry-run — structure_control + controlnet workflow 라우팅
run_test "v2.1 generate dry-run structure_control ref" \
    $PY -c "
import os
os.makedirs('/tmp', exist_ok=True)
open('/tmp/fpof_smoke_ref.png', 'w').close()
import sys; sys.path.insert(0,'scripts')
import argparse
# argparse namespace 수동 구성 — 실제 main() 우회
from generate import generate, _has_foundation_slot
class NS: pass
a = NS()
a.prompt = 'hoodie structural redesign'
a.negative = None
a.shot = None
a.silhouette = None
a.material = None
a.details = None
a.color_slot = None
a.construction = None
a.lighting_quality = None
a.style_lock = None
a.iterate = None
a.revise = None
a.section_type = 'structure_control'
a.channel = None
a.model_family = 'sdxl'
a.phase_limit = 2
a.speed = 'balanced'
a.workflow_rel = None
a.width = None
a.height = None
a.seed = 12345
a.steps = None
a.cfg = None
a.batch = 1
a.ref_image = '/tmp/fpof_smoke_ref.png'
a.ref_strength = 0.8
a.output = './structure.png'
a.timeout = 600
a.from_meta = None
a.source_sheet = None
a.source_header = None
a.dry_run = True
result = generate(a)
print('OK structure_control dry-run')
"

# 9i. style-lock 저장 파일 정리 (테스트 격리)
rm -f ~/.comfyui-engine/style-locks/smoke_test.json

# 9j. --iterate 파일명 suffix 로직
run_test "v2.1 next_iteration_path suffix logic" \
    $PY -c "
import sys; sys.path.insert(0,'scripts')
from generate import next_iteration_path
p1, n1 = next_iteration_path('/tmp/foo.png')
assert p1 == '/tmp/foo_iter1.png' and n1 == 1, (p1, n1)
p2, n2 = next_iteration_path('/tmp/foo_iter3.png')
assert p2 == '/tmp/foo_iter4.png' and n2 == 4, (p2, n2)
print('OK', p1, p2)
"

# 결과
echo
echo "========================================"
echo "  PASS: $pass"
echo "  FAIL: $fail"
echo "========================================"

if [[ $fail -gt 0 ]]; then
    exit 1
fi
exit 0
