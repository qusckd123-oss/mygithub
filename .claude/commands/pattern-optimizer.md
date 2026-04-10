# 패턴 최적화

아이템의 패턴 구성을 분석하여 원단 용척 최적화, 마커 효율 개선, 대안 소재 제안, 원가 절감 시뮬레이션을 수행합니다.

## 사용법
`/pattern-optimizer [옵션]` — 옵션 생략 시 아이템과 최적화 목적을 물어봅니다.

## 절차

1. `system/skills/product/pattern-optimizer.md` 스킬 파일을 읽어 실행 절차 확인
2. **AskUserQuestion으로 분석 설정** (아이템, 최적화 목적)
3. 패턴 피스 분석 (아이템별 표준 구성)
4. 용척 계산 & 마커 효율 분석 (목표 85%+)
5. 대안 소재 매트릭스 (Cost/Quality/Availability/Sustainability 4축)
6. 원가 절감 종합 시뮬레이션 (3시나리오)
7. 지속가능성 분석 (선택)

## 최적화 목적
- **원가 절감**: 소재비/로스율 절감 중심
- **대안 소재 탐색**: 동등 품질 저비용 또는 친환경 소재
- **마커 효율**: 패턴 배치 최적화
- **지속가능성**: 폐기율, 재활용, 친환경 전환

## 예시
```
/pattern-optimizer                       → 설정 선택 → 분석
/pattern-optimizer 그래픽 티 원가 절감     → 특정 아이템 원가 최적화
/pattern-optimizer 후드티 대안 소재        → 소재 대체 분석
```

## 출력
- 패턴 최적화 리포트: `workspace/[시즌]/[프로젝트]/design_pattern-optimization.md`

## 인수
$ARGUMENTS
