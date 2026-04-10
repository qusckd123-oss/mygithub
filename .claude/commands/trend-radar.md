# 트렌드 레이더

멀티소스 트렌드 시그널을 수집하고 5축 스코어링으로 정량화하여 BTA 트렌드 매핑까지 수행합니다.

## 사용법
`/trend-radar [옵션]` — 옵션을 생략하면 스캔 모드/데이터 소스/카드 수를 물어봅니다.

## 절차

1. `system/skills/data/trend-radar.md` 스킬 파일을 읽어 실행 절차 확인
2. **AskUserQuestion으로 스캔 설정** (모드, 데이터 소스, 카드 수)
3. 4단계 시그널 수집 (서치 → 글로벌 → 리테일 → 비주얼)
4. 5축 스코어링 (Velocity, Volume, Relevance, Longevity, Whitespace)
5. BTA 매핑 (Basic/Trend/Accent 배분)
6. 트렌드 카드 생성 + 시즌 트렌드 맵

## 데이터 소스
- **서치**: market-intelligence (네이버 데이터랩, 구글 트렌드)
- **글로벌**: 웹서치 (런웨이, 스트릿 스냅, SNS 바이럴)
- **리테일**: musinsa-ranking, musinsa-release, 자사 판매 데이터
- **비주얼**: pinterest-crawl, 웹서치 (컬러/실루엣/소재 트렌드)

## 스캔 모드
- **전체 스캔**: 시즌 기획용, 모든 카테고리+소스
- **카테고리 포커스**: 특정 카테고리 집중
- **테마 포커스**: 특정 테마의 시그널만 추적
- **경쟁 레이더**: 경쟁사 동향 중심

## 예시
```
/trend-radar                      → 설정 선택 → 전체 실행
/trend-radar 전체 스캔              → 전체 스캔 모드로 실행
/trend-radar 키치 테마 포커스       → 키치 관련 시그널만 추적
```

## 출력
- 트렌드 레이더 리포트: `workspace/[시즌]/season-strategy/plan_trend-radar_YYYY-MM-DD.md`
- 트렌드 카드 (5~15장), 스코어보드, BTA 매핑, 시즌 맵, 타임라인

## 인수
$ARGUMENTS
