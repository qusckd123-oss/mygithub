# 컬러 인텔리전스

브랜드 시그니처 컬러 기반으로 트렌드/경쟁사 컬러를 분석하고 시즌 마스터 팔레트(12~16색)와 카테고리별 BTA 컬러 배분을 설계합니다.

## 사용법
`/color-intelligence [옵션]` — 옵션 생략 시 전체 시즌 팔레트를 생성합니다.

## 절차

1. `system/skills/creative/color-intelligence.md` 스킬 파일을 읽어 실행 절차 확인
2. 브랜드 컬러 DNA 로드 (Signature Yellow #FEF200, Black, White, Sky Blue #68A8DB)
3. 트렌드 컬러 수집 (PANTONE COTY, 런웨이, SNS)
4. 경쟁사 컬러 스캔 (무신사 랭킹 데이터 / 웹서치)
5. 시즌 마스터 팔레트 설계 (Core 4 + Season 4~6 + Accent 2~3 + Neutral 2~3)
6. 컬러 스코어링 (Trend/Brand/Commercial/Whitespace 4축)
7. 카테고리별 컬러 배분 (UNI/W/ACC × BTA)
8. 컬러 스토리 작성

## 예시
```
/color-intelligence                    → 시즌 전체 팔레트 생성
/color-intelligence 그래픽 티 컬러웨이   → 특정 카테고리 컬러 배분
```

## 출력
- 컬러 인텔리전스 리포트: `workspace/[시즌]/season-strategy/plan_color-intelligence_YYYY-MM-DD.md`

## 인수
$ARGUMENTS
