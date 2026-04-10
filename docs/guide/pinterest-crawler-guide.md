# Pinterest Crawler 설치 및 활용 가이드

> 와키윌리 브랜드 무드보드 이미지 수집을 위한 Pinterest 크롤러 가이드입니다.
> macOS와 Windows 환경별 설치부터 실전 활용까지 안내합니다.

---

## 목차

1. [시스템 요구사항](#1-시스템-요구사항)
2. [macOS 설치](#2-macos-설치)
3. [Windows 설치](#3-windows-설치)
4. [구동 방식 이해](#4-구동-방식-이해)
5. [기본 사용법](#5-기본-사용법)
6. [실전 활용 시나리오](#6-실전-활용-시나리오)
7. [AI 브랜드 필터링](#7-ai-브랜드-필터링)
8. [트러블슈팅](#8-트러블슈팅)
9. [주의사항](#9-주의사항)

---

## 1. 시스템 요구사항

| 항목 | 최소 사양 | 권장 사양 |
|------|----------|----------|
| OS | macOS 12+ / Windows 10+ | macOS 13+ / Windows 11 |
| Python | 3.9 이상 | 3.11 이상 |
| Chrome | 설치 필수 (버전 무관) | 최신 버전 |
| RAM | 4GB | 8GB 이상 |
| 디스크 | 수집 이미지 용량 (100장 ≈ 50MB) | — |
| 네트워크 | 인터넷 연결 필수 | — |

### 필요한 Python 패키지

| 패키지 | 역할 | 필수 여부 |
|--------|------|----------|
| `selenium` | Chrome 브라우저 자동화 (페이지 렌더링, 스크롤) | 필수 |
| `webdriver-manager` | ChromeDriver 자동 설치/버전 매칭 | 필수 |
| `requests` | 이미지 파일 다운로드 | 필수 |
| `Pillow` | 이미지 해상도 검증 필터 | 선택 (없으면 해상도 필터 스킵) |
| `anthropic` | AI 브랜드 적합성 필터 (`filter.py`) | 선택 (필터 사용 시만) |

---

## 2. macOS 설치

### Step 1: Python 확인

터미널을 열고 Python 버전을 확인합니다.

```bash
python3 --version
```

Python이 없으면 Homebrew로 설치합니다:

```bash
# Homebrew 설치 (이미 있으면 스킵)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python 설치
brew install python
```

### Step 2: Chrome 브라우저 확인

Chrome이 설치되어 있는지 확인합니다:

```bash
ls /Applications/Google\ Chrome.app
```

설치되어 있지 않다면 [chrome.google.com](https://www.google.com/chrome/)에서 다운로드합니다.

### Step 3: 패키지 설치

```bash
# 프로젝트 폴더로 이동
cd "07. FPOF V2.2 Claude/system/scripts/pinterest-crawler"

# 필수 패키지 설치
pip3 install selenium webdriver-manager requests

# 선택 패키지 (해상도 필터 + AI 필터)
pip3 install Pillow anthropic
```

### Step 4: 설치 확인

```bash
python3 -c "
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import requests
print('selenium:', webdriver.__version__ if hasattr(webdriver, '__version__') else 'OK')
print('webdriver-manager: OK')
print('requests:', requests.__version__)
try:
    from PIL import Image
    print('Pillow: OK')
except ImportError:
    print('Pillow: 미설치 (선택사항)')
try:
    import anthropic
    print('anthropic: OK')
except ImportError:
    print('anthropic: 미설치 (AI 필터 사용 시 필요)')
print()
print('설치 완료!')
"
```

### Step 5: 첫 실행 테스트

```bash
# 가장 간단한 테스트 — 키워드 1개, 5장만 수집
python3 crawler.py --keyword "kitsch street fashion" --count 5 --headless
```

> **macOS 첫 실행 시 주의**: "chromedriver를 확인할 수 없습니다" 보안 경고가 나올 수 있습니다.
> **시스템 설정 → 개인정보 보호 및 보안 → "확인 없이 허용"** 클릭 후 다시 실행하세요.

---

## 3. Windows 설치

### Step 1: Python 설치

PowerShell 또는 명령 프롬프트에서 확인합니다:

```powershell
python --version
```

Python이 없으면:

1. [python.org/downloads](https://www.python.org/downloads/)에서 최신 버전 다운로드
2. 설치 시 **"Add Python to PATH" 체크박스를 반드시 체크**
3. 설치 완료 후 터미널을 **재시작**

```powershell
# 설치 확인
python --version
pip --version
```

> **주의**: Windows에서는 `python3` 대신 `python`, `pip3` 대신 `pip`을 사용합니다.

### Step 2: Chrome 브라우저 확인

Chrome이 설치되어 있는지 확인합니다:

```powershell
# Chrome 설치 경로 확인
Test-Path "C:\Program Files\Google\Chrome\Application\chrome.exe"
```

`False`가 나오면 [chrome.google.com](https://www.google.com/chrome/)에서 다운로드합니다.

### Step 3: 패키지 설치

```powershell
# 프로젝트 폴더로 이동
cd "07. FPOF V2.2 Claude\system\scripts\pinterest-crawler"

# 필수 패키지 설치
pip install selenium webdriver-manager requests

# 선택 패키지 (해상도 필터 + AI 필터)
pip install Pillow anthropic
```

### Step 4: 설치 확인

```powershell
python -c "from selenium import webdriver; from webdriver_manager.chrome import ChromeDriverManager; import requests; print('설치 완료!')"
```

### Step 5: 첫 실행 테스트

```powershell
# 가장 간단한 테스트 — 키워드 1개, 5장만 수집
python crawler.py --keyword "kitsch street fashion" --count 5 --headless
```

> **Windows 첫 실행 시 주의**: "Windows 방화벽에서 chromedriver 차단" 알림이 나올 수 있습니다.
> **"액세스 허용"**을 클릭하세요. 또한 백신 프로그램이 chromedriver를 차단할 수 있으므로
> 예외 등록이 필요할 수 있습니다.

---

## 4. 구동 방식 이해

Pinterest 크롤러는 **Selenium** 기반으로 동작합니다.

### 기술 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│  crawler.py                                             │
│                                                         │
│  ① Selenium → Chrome WebDriver 실행                     │
│       ↓                                                 │
│  ② pinterest.com/search/pins/?q=키워드 접속              │
│       ↓                                                 │
│  ③ JavaScript 무한 스크롤 (최대 40회)                    │
│       ↓                                                 │
│  ④ img[src*='pinimg.com'] CSS 셀렉터로 URL 수집          │
│       ↓                                                 │
│  ⑤ 썸네일 URL → /736x/ 고해상도 URL로 변환               │
│       ↓                                                 │
│  ⑥ requests.get()으로 이미지 파일 다운로드                │
│       ↓                                                 │
│  ⑦ 파일 크기(5KB↑) / 해상도(100px↑) 자동 필터            │
│       ↓                                                 │
│  ⑧ _metadata.json에 수집 결과 기록                       │
└─────────────────────────────────────────────────────────┘
```

### 왜 Selenium인가?

Pinterest는 **SPA(Single Page Application)**로, 페이지 콘텐츠가 JavaScript로 동적 렌더링됩니다.
단순 HTTP 요청(`requests`)으로는 이미지 URL을 얻을 수 없습니다.

| 방식 | Pinterest에서 | 이유 |
|------|-------------|------|
| `requests` + BeautifulSoup | 불가 | JS 렌더링 없음 → 빈 HTML |
| Selenium (현재 방식) | 가능 | 실제 Chrome이 JS 실행 → 이미지 로드됨 |
| Playwright | 가능 (대안) | 비슷한 원리, 현재 미구현 |

### 주요 컴포넌트

| 파일 | 역할 |
|------|------|
| `crawler.py` | Selenium으로 검색·스크롤·이미지 수집·다운로드 |
| `filter.py` | Claude Vision API로 브랜드 적합성 평가 (선택) |
| `_metadata.json` | 수집 결과 메타데이터 (자동 생성) |
| `_pinterest_cookies.pkl` | 로그인 쿠키 저장 (자동 생성) |

### 인증 모드 비교

| 모드 | 명령어 | 특징 |
|------|--------|------|
| **비로그인** (기본) | `python3 crawler.py --headless` | 검색 결과 제한적, 가장 간편 |
| **크롬 프로필** | `python3 crawler.py --login` | 기존 크롬 로그인 세션 재활용, 결과 풍부 |
| **쿠키 저장** | 자동 | 첫 로그인 후 `_pinterest_cookies.pkl`에 저장, 이후 자동 로그인 |

---

## 5. 기본 사용법

### CLI 옵션 전체 목록

```
python3 crawler.py [옵션]

인증:
  --login               크롬 프로필 로그인 (기존 세션 재활용)
  --email EMAIL         이메일 직접 로그인
  --password PASSWORD   비밀번호

크롤링 모드:
  --keyword KEYWORD     단일 키워드 검색
  --category CATEGORY   특정 카테고리만 크롤링
  --interactive, -i     인터랙티브 모드 (대화형)
  --count N             단일 키워드 수집 수 (기본: 50)
  --count-per-keyword N 카테고리 모드 키워드당 수 (기본: 30)

옵션:
  --output, -o PATH     저장 디렉토리 지정
  --headless            헤드리스 모드 (브라우저 안 보임)
```

> **Windows 사용자**: 아래 모든 예시에서 `python3`을 `python`으로 바꿔 실행하세요.

### 5-1. 단일 키워드 검색 (가장 많이 사용)

```bash
# 기본 — 키워드 검색, 50장 수집
python3 crawler.py --keyword "dopamine dressing street style" --headless

# 수량 지정
python3 crawler.py --keyword "kitsch fashion lookbook" --count 30 --headless

# 저장 경로 지정
python3 crawler.py --keyword "Y2K outfit" --count 40 --headless -o ~/Desktop/moodboard
```

**저장 위치**: `workspace/moodboard/pinterest_YYYYMMDD/custom/`

### 5-2. 카테고리 크롤링

사전 정의된 7개 브랜드 카테고리별 키워드로 일괄 수집합니다.

```bash
# 전체 카테고리 (7개, 약 200~400장)
python3 crawler.py --headless

# 특정 카테고리만
python3 crawler.py --category brand_mood --headless
python3 crawler.py --category character_ip --headless
```

**사용 가능한 카테고리:**

| 카테고리 | 키워드 수 | 내용 |
|----------|----------|------|
| `brand_mood` | 6 | 키치 스트릿 전반 무드 |
| `character_ip` | 6 | 캐릭터·그래픽·IP 감성 |
| `color_vivid` | 6 | 비비드 컬러 트렌드 |
| `target_styling` | 6 | 18~25세 코어타겟 스타일링 |
| `campaign_ref` | 4 | 캠페인·룩북 레퍼런스 |
| `accessories` | 4 | 용품·악세서리 |
| `visual_merch` | 4 | VM·매장 디스플레이 |

### 5-3. 인터랙티브 모드

터미널에서 키워드를 입력하며 실시간으로 수집합니다.

```bash
python3 crawler.py --interactive --headless
```

실행하면 프롬프트가 나타납니다:

```
  🔍 검색 키워드: kitsch fashion lookbook
  → 수집 중... 30장 완료

  🔍 검색 키워드: neon streetwear, bold graphic tee /50
  → 수집 중... 50장 완료

  🔍 검색 키워드: q
  → 세션 종료 — 총 80장 수집
```

**인터랙티브 모드 팁:**
- 쉼표(`,`)로 여러 키워드 동시 검색: `kitsch fashion, pop art outfit`
- `/숫자`로 수량 변경: `dopamine dressing /50`
- `q` 또는 `exit`로 종료

### 5-4. 로그인 모드 (결과 더 많이 보기)

비로그인 상태에서는 Pinterest가 검색 결과를 제한합니다.
더 많은 결과가 필요하면 로그인 모드를 사용하세요.

```bash
# 크롬 프로필 모드 (권장) — 기존 크롬 로그인 재활용
# ⚠️ 실행 전 Chrome 브라우저를 닫아주세요
python3 crawler.py --login --keyword "kitsch street fashion" --count 50
```

> **주의**: `--login` 모드는 `--headless`와 함께 사용할 수 없습니다.
> 크롬 프로필은 브라우저 창이 열려야 작동합니다.

---

## 6. 실전 활용 시나리오

### 시나리오 A: 시즌 무드보드 이미지 수집

시즌 기획 초기에 전체 카테고리를 한 번에 수집합니다.

```bash
# 1. 전체 카테고리 크롤링
python3 crawler.py --headless

# 2. 결과 확인
ls workspace/moodboard/pinterest_20260323/
# → brand_mood/ character_ip/ color_vivid/ ... _metadata.json
```

### 시나리오 B: 특정 아이템 레퍼런스 수집

디자이너가 특정 아이템의 레퍼런스 이미지를 요청했을 때:

```bash
# 싸커져지 스트릿 스타일링
python3 crawler.py --keyword "soccer jersey street outfit" --count 40 --headless

# 오버사이즈 후디 그래픽
python3 crawler.py --keyword "oversized hoodie graphic print" --count 40 --headless
```

### 시나리오 C: 트렌드 리서치

특정 트렌드 키워드로 빠르게 시각 자료를 모읍니다.

```bash
# 2026 트렌드
python3 crawler.py --keyword "2026 street fashion trend" --count 30 --headless

# 도파민 드레싱 트렌드
python3 crawler.py --keyword "dopamine dressing colorful outfit" --count 30 --headless
```

### 시나리오 D: FPOF에서 사용 (Claude Code)

Claude Code에서 `/pinterest` 명령으로 사용하면, Claude가 키워드 설계부터 수집까지 자동으로 처리합니다.

```
/pinterest 도파민 드레싱 레퍼런스
/pinterest 키치 스트릿 패션 50
/pinterest [이미지 첨부]        → 이미지 분석 후 키워드 자동 설계
```

---

## 7. AI 브랜드 필터링

수집된 이미지 중 브랜드 무드에 맞는 것만 선별하는 기능입니다.
Claude Vision API를 사용하므로 **Anthropic API 키**가 필요합니다.

### 환경변수 설정

**macOS:**
```bash
export ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxxxxx"

# 영구 설정 (zsh 기준)
echo 'export ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxxxxx"' >> ~/.zshrc
source ~/.zshrc
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-xxxxxxxxxxxxxxxx"

# 영구 설정
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-xxxxxxxxxxxxxxxx", "User")
# PowerShell 재시작 필요
```

### 브랜드 적합성 필터

와키윌리 브랜드 무드(키치, 비비드, 스트릿)에 맞는지 10점 척도로 평가합니다.

```bash
# 전체 폴더 필터 (7점 이상 유지, 기본)
python3 filter.py workspace/moodboard/pinterest_20260323 -r

# 기준 높이기 (8점 이상만)
python3 filter.py workspace/moodboard/pinterest_20260323 -r -t 8

# 미리보기 (파일 이동 없이 점수만 확인)
python3 filter.py workspace/moodboard/pinterest_20260323 -r --dry-run

# 특정 폴더만
python3 filter.py workspace/moodboard/pinterest_20260323/brand_mood
```

### 키워드 적합성 필터

검색 키워드 의도에 맞는 이미지인지 평가합니다.
Pinterest 검색 노이즈(키워드 개별 단어에 매칭된 무관 이미지)를 제거할 때 유용합니다.

```bash
# 키워드 적합성 필터
python3 filter.py workspace/moodboard/pinterest_20260323/soccer-jersey \
  --keyword "soccer jersey street outfit"
```

### 필터 결과

```
workspace/moodboard/pinterest_20260323/brand_mood/
├── abc123def456.jpg     ← 적합 (유지)
├── 789ghi012jkl.jpg     ← 적합 (유지)
├── _filtered/            ← 부적합 이미지 이동됨
│   └── mno345pqr678.jpg
└── _filter_report.json   ← 평가 결과 리포트
```

### filter.py CLI 옵션

```
python3 filter.py <디렉토리> [옵션]

필수:
  directory              필터링할 이미지 디렉토리 경로

옵션:
  --threshold, -t N      최소 적합 점수 (기본: 7)
  --keyword, -k KEYWORD  키워드 적합성 모드 (브랜드 필터 대신)
  --model MODEL          Claude 모델 (기본: claude-sonnet-4-6)
  --api-key KEY          API 키 (없으면 환경변수 ANTHROPIC_API_KEY)
  --recursive, -r        하위 폴더 재귀 필터링
  --dry-run              미리보기만 (파일 이동 안 함)
```

---

## 8. 트러블슈팅

### 공통 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| `ModuleNotFoundError: No module named 'selenium'` | 패키지 미설치 | `pip3 install selenium webdriver-manager requests` |
| `WebDriverException: chromedriver not found` | ChromeDriver 없음 | `webdriver-manager`가 자동 해결 — 네트워크 확인 |
| 이미지 0장 수집 | 키워드에 결과 없음 또는 차단 | 영문 키워드로 변경, `--login` 모드 시도 |
| `NoSuchWindowException` | 브라우저 창 닫힘 | `--headless` 모드로 재실행 |
| 수집 속도 느림 | 네트워크 또는 스크롤 대기 | 정상 동작 (키워드당 1~3분 소요) |

### macOS 전용 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| "chromedriver를 확인할 수 없습니다" | macOS 보안 정책 (Gatekeeper) | **시스템 설정 → 개인정보 보호 및 보안 → "확인 없이 허용"** |
| `xattr` 관련 에러 | 격리 속성 | `xattr -d com.apple.quarantine $(which chromedriver)` |
| Chrome 프로필 경로 에러 | 프로필 경로 다름 | 기본값: `~/Library/Application Support/Google/Chrome` |

### Windows 전용 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| "방화벽에서 chromedriver 차단" | Windows Defender 방화벽 | **"액세스 허용"** 클릭 |
| 백신이 chromedriver 삭제 | 바이러스로 오탐 | 백신 예외 등록: `%USERPROFILE%\.wdm\` 폴더 |
| `python3`을 찾을 수 없음 | Windows는 `python` 명령 사용 | `python` 또는 `py` 명령으로 변경 |
| `pip`을 찾을 수 없음 | PATH 미등록 | Python 재설치 시 "Add to PATH" 체크 |
| 한글 경로 에러 | 파일 경로에 한글 포함 | 프로젝트를 영문 경로에 배치 (예: `C:\Projects\`) |
| `UnicodeEncodeError` | 콘솔 인코딩 | `chcp 65001` 실행 후 재시도 (UTF-8 설정) |
| Chrome 프로필 경로 에러 | Windows 경로 다름 | `%LOCALAPPDATA%\Google\Chrome\User Data` |

### ChromeDriver 수동 해결 (최후 수단)

`webdriver-manager` 자동 설치가 실패할 경우:

1. Chrome 버전 확인: 주소창에 `chrome://version` 입력
2. [chromedriver.chromium.org](https://chromedriver.chromium.org/downloads)에서 같은 버전 다운로드
3. 다운받은 파일을 PATH가 잡힌 경로에 배치
   - macOS: `/usr/local/bin/chromedriver`
   - Windows: `C:\Windows\chromedriver.exe`

---

## 9. 주의사항

### 이용 정책
- Pinterest ToS는 자동 크롤링을 금지합니다. **내부 리서치/무드보드 용도로만** 사용하세요.
- 수집된 이미지의 저작권은 원작자에게 있습니다. 상업적 사용 시 별도 라이선스를 확인하세요.

### 크롤링 제한
- 과도한 크롤링 시 **IP 차단** 가능합니다.
- 크롤러에는 키워드 간 2초, 카테고리 간 3초 쿨다운이 내장되어 있습니다.
- 한 번에 200장 이상 수집 시 차단 확률이 높아집니다. 여러 세션에 나눠 수집하세요.

### 출력 구조

```
workspace/moodboard/pinterest_YYYYMMDD/
├── brand_mood/             ← 카테고리별 이미지
├── character_ip/
├── custom/                 ← 단일 키워드 수집 (폴더 분류 전)
├── dopamine-dressing/      ← 키워드별 분류 폴더
├── _metadata.json          ← 수집 메타데이터
├── _filter_report.json     ← AI 필터 리포트 (filter.py 실행 시)
└── _pinterest_cookies.pkl  ← 로그인 쿠키 (자동 생성)
```

---

## 빠른 참조 카드

### macOS

```bash
# 설치
pip3 install selenium webdriver-manager requests Pillow

# 단일 키워드 수집
python3 crawler.py --keyword "키워드" --count 30 --headless

# 전체 카테고리 수집
python3 crawler.py --headless

# AI 필터링
export ANTHROPIC_API_KEY="sk-ant-xxx"
python3 filter.py workspace/moodboard/pinterest_20260323 -r
```

### Windows

```powershell
# 설치
pip install selenium webdriver-manager requests Pillow

# 단일 키워드 수집
python crawler.py --keyword "키워드" --count 30 --headless

# 전체 카테고리 수집
python crawler.py --headless

# AI 필터링
$env:ANTHROPIC_API_KEY = "sk-ant-xxx"
python filter.py workspace\moodboard\pinterest_20260323 -r
```
