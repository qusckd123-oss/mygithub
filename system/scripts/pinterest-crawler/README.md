# Pinterest Crawler — Wacky Willy Moodboard

와키윌리 브랜드 무드(Kitsch Street & IP Universe)에 맞는 핀터레스트 이미지를 수집하는 파이프라인.

## 구조

```
pinterest-crawler/
├── crawler.py    # Selenium 크롤러 (검색 → 수집 → 다운로드)
├── filter.py     # Claude Vision 브랜드 적합성 필터
└── README.md
```

## 설치

```bash
pip install selenium webdriver-manager requests Pillow anthropic
```

## 사용법

### 1단계: 크롤링

```bash
# 전체 카테고리 크롤링 (7개 카테고리, 약 200~400장)
python crawler.py

# 로그인 모드 (검색 결과 제한 해제)
python crawler.py --email your@email.com --password yourpass

# 특정 카테고리만
python crawler.py --category brand_mood
python crawler.py --category character_ip

# 단일 키워드
python crawler.py --keyword "kitsch street fashion" --count 50

# 헤드리스 모드 (백그라운드)
python crawler.py --headless

# 저장 경로 지정
python crawler.py -o ~/Desktop/moodboard
```

### 2단계: AI 필터링 (선택)

```bash
# 전체 폴더 필터 (7점 이상 유지)
python filter.py ./workspace/moodboard/pinterest_20260320 -r

# 기준 올리기 (8점 이상만)
python filter.py ./workspace/moodboard/pinterest_20260320 -r -t 8

# 미리보기 (파일 이동 안 함)
python filter.py ./workspace/moodboard/pinterest_20260320 -r --dry-run
```

## 카테고리

| 카테고리 | 키워드 수 | 설명 |
|----------|----------|------|
| `brand_mood` | 6 | 키치 스트릿 전반 무드 |
| `character_ip` | 6 | 캐릭터·그래픽·IP 감성 |
| `color_vivid` | 6 | 비비드 컬러 트렌드 |
| `target_styling` | 6 | 18~25세 코어타겟 스타일링 |
| `campaign_ref` | 4 | 캠페인·룩북 레퍼런스 |
| `accessories` | 4 | 용품·악세서리 |
| `visual_merch` | 4 | VM·매장 디스플레이 |

## 출력 구조

```
workspace/moodboard/pinterest_20260320/
├── brand_mood/           # 카테고리별 이미지
├── character_ip/
├── color_vivid/
├── target_styling/
├── campaign_ref/
├── accessories/
├── visual_merch/
├── _metadata.json        # 크롤링 메타데이터
└── _filter_report.json   # AI 필터링 리포트 (filter.py 실행 시)
```

## 주의사항

- 핀터레스트 ToS는 자동 크롤링을 금지합니다. 내부 리서치/무드보드 용도로만 사용하세요.
- 과도한 크롤링 시 IP 차단될 수 있습니다. 키워드 간 2초, 카테고리 간 3초 쿨다운이 설정되어 있습니다.
- AI 필터링은 Anthropic API 키가 필요합니다 (환경변수 `ANTHROPIC_API_KEY`).
