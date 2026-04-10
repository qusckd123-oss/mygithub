# 수요 예측 & 가격 최적화

판매 데이터 기반으로 재고 소진 예측, 리오더 타이밍/물량, 가격 최적화, SPOT 후보, BTA 리밸런싱을 산출합니다.

## 사용법
`/demand-optimizer [옵션]` — 옵션 생략 시 분석 모드와 기간을 물어봅니다.

## 절차

1. `system/skills/data/demand-optimizer.md` 스킬 파일을 읽어 실행 절차 확인
2. **AskUserQuestion으로 분석 설정** (모드, 기간)
3. 대시보드 JSON 데이터 로드 (data_sales, data_per-styles 등)
4. 판매 속도 분석 (STR, DRR, 등급 S/A/B/C/D)
5. 재고 소진 예측 (3시나리오)
6. 리오더 알림 (긴급/정상/대기) + 물량 산정
7. 가격 최적화 (할인 대상 + 시뮬레이션)
8. SPOT 후보 추천
9. BTA 리밸런싱 권고
10. 경영목표 #2, #3 KPI 연동

## 분석 모드
- **전체 스캔**: 전 스타일 판매 속도 → 리오더/SPOT/할인 자동 추출
- **리오더 판단**: 특정 아이템 리오더 타이밍 & 물량
- **가격 최적화**: 할인/가격 조정 대상 분석
- **BTA 리밸런싱**: 실적 기반 포트폴리오 재배분

## 예시
```
/demand-optimizer                       → 설정 선택 → 전체 실행
/demand-optimizer 전체 스캔              → 전 스타일 스캔
/demand-optimizer 리오더 그래픽 티       → 특정 아이템 리오더 판단
```

## 출력
- 수요 최적화 리포트: `workspace/[시즌]/season-strategy/check_demand-optimization_YYYY-MM-DD.md`
- 리오더 알림, 할인 시뮬레이션, SPOT 후보, BTA 리밸런싱

## 인수
$ARGUMENTS
