# 세션 15: 플러그인 에코시스템 — 31개 플러그인 프로젝트 통합

> **소요시간**: 35분 (설명 15분 + 데모 10분 + 실습 10분)
> **대상**: 전 AI Committee 멤버
> **목표**: FPOF에 통합된 31개 플러그인의 역할 이해, 프로젝트 단위 설치 구조 파악, 실무 활용법 실습

---

## 1. 왜 플러그인 통합인가?

### 기존 문제
- 플러그인이 **개인 글로벌 설치**로만 존재 → 팀원마다 환경이 다름
- GitHub 클론 후 **플러그인이 누락**되어 기능이 작동하지 않음
- 어떤 플러그인이 설치되어야 하는지 **문서화되지 않음**

### 해결
- `.claude/settings.json`에 **31개 플러그인 + 7개 마켓플레이스**를 프로젝트 단위로 등록
- `git clone` → Claude Code 실행만으로 **자동 설치/활성화**
- 글로벌 설치는 그대로 유지 → **충돌 없이 양립**

---

## 2. 플러그인 구조 이해

### 설치 범위 (Scope)

| 범위 | 위치 | 특징 |
|------|------|------|
| **user (글로벌)** | `~/.claude/plugins/` | 모든 프로젝트에서 사용 가능 |
| **project** | `.claude/settings.json` → `enabledPlugins` | 해당 프로젝트에서만 활성화, git에 포함 |
| **local** | 개별 머신 전용 | git에 포함하지 않음 |

### 핵심 설정 파일: `.claude/settings.json`

```json
{
  "enabledPlugins": {
    "플러그인이름@마켓플레이스": true
  },
  "extraKnownMarketplaces": {
    "마켓플레이스이름": {
      "source": "github",
      "repo": "org/repo"
    }
  }
}
```

- **`enabledPlugins`**: 활성화할 플러그인 목록 (프로젝트 레벨)
- **`extraKnownMarketplaces`**: 비공식 마켓플레이스의 GitHub 소스 등록

---

## 3. 등록된 31개 플러그인 전체 맵

### 공식 플러그인 (claude-plugins-official) — 7개

| 플러그인 | 용도 | 대표 스킬 |
|----------|------|----------|
| **telegram** | 텔레그램 메시징 연동 | reply, react, edit_message |
| **commit-commands** | Git 커밋·푸시·PR 자동화 | /commit, /commit-push-pr |
| **github** | GitHub 이슈/PR 연동 | 이슈 생성, PR 관리 |
| **figma** | Figma 디자인 연동 | 디자인 시스템, 핸드오프 |
| **supabase** | Supabase DB 연동 | Postgres 쿼리, 스토리지 |
| **Notion** | Notion 문서 연동 | 페이지 읽기/쓰기 |
| **vercel** | Vercel 배포/관리 | 배포, 환경변수, 도메인 |

### Knowledge-Work 플러그인 — 18개

패션 실무와 직접 관련되지 않지만, **범용 비즈니스 도메인**을 커버합니다.

| 도메인 | 플러그인 | FPOF 활용 예시 |
|--------|---------|---------------|
| **영업** | sales | 바이어 미팅 준비, 도매 파이프라인 |
| **마케팅** | marketing | SEO 감사, 이메일 시퀀스, 캠페인 분석 |
| **PM** | product-management | 개발팀 스프린트, IT 기능 스펙 |
| **엔지니어링** | engineering | 코드리뷰, 시스템 설계, 인시던트 |
| **데이터** | data | Snowflake/BigQuery SQL, 대시보드 빌드 |
| **디자인** | design | WCAG 접근성, UX 카피, 핸드오프 |
| **재무** | finance | 분개, 결산, SOX 감사 |
| **법무** | legal | 계약검토, 컴플라이언스, NDA |
| **HR** | human-resources | 채용, 보상분석, 온보딩 |
| **운영** | operations | 프로세스 최적화, 런북, 리스크 |
| **CS** | customer-support | 티켓 분류, 에스컬레이션 |
| **검색** | enterprise-search | 크로스플랫폼 검색 |
| **생산성** | productivity | 태스크 관리, 메모리 시스템 |
| **브랜드** | brand-voice | 가이드라인 생성, 톤 적용 |
| **리드생성** | apollo | ICP→리드 파이프라인 |
| **커뮤니티** | common-room | 어카운트/컨택 리서치 |
| **Slack** | slack-by-salesforce | 채널 요약, 스탠드업 |
| **관리** | cowork-plugin-management | 커스텀 플러그인 생성 |

### 전문 도구 플러그인 — 6개

| 플러그인 | 출처 | 용도 |
|----------|------|------|
| **document-skills** | anthropic-agent-skills | PDF·PPTX·DOCX·XLSX 생성 |
| **frontend-design** | claude-code-plugins | 프론트엔드 디자인 가이드 |
| **claude-mem** | thedotmack | 대화 메모리 시스템 |
| **claude-dashboard** | claude-dashboard | AI 사용량 모니터링 |
| **postgres-best-practices** | supabase-agent-skills | Postgres 쿼리 최적화 |
| **obsidian** | obsidian-skills | Obsidian 노트 연동 |

---

## 4. FPOF 이중 라우팅과 플러그인

FPOF는 **패션/브랜드 맥락**과 **범용 비즈니스 맥락**을 자동으로 구분합니다.

```
요청 수신
  ├─ 와키윌리/시즌/PDCA 키워드? ──→ FPOF 내장 스킬 (82개)
  ├─ HR/법무/재무/엔지니어링? ──→ KW 플러그인 스킬 (118개)
  ├─ 겹치는 영역?
  │   ├─ 브랜드 프리셋 필요? ──→ FPOF
  │   └─ 범용 프레임워크? ──→ KW 플러그인
  └─ 모호? ──→ 사용자에게 확인
```

### 명시적 호출 (`@도메인` 접두사)

자동 라우팅 대신 직접 지정할 수도 있습니다:

```
@sales 이 바이어 조사해줘
@marketing SEO 감사 해줘
@legal 계약서 검토해줘
@finance 분개 만들어줘
@eng 코드 리뷰해줘
```

---

## 5. 실습

### 실습 1: 플러그인 상태 확인

터미널에서 현재 프로젝트의 플러그인 상태를 확인합니다.

```bash
# .claude/settings.json 확인
cat .claude/settings.json | python3 -m json.tool

# enabledPlugins 목록만 추출
cat .claude/settings.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
plugins = data.get('enabledPlugins', {})
for name, enabled in plugins.items():
    status = 'ON' if enabled else 'OFF'
    print(f'  [{status}] {name}')
print(f'\n  Total: {len(plugins)} plugins')
"
```

### 실습 2: KW 플러그인 사용해보기

Claude Code에서 다음 명령을 실행해봅니다:

```
# 마케팅 도메인 — 캠페인 기획
@marketing 와키윌리 26SS 런칭 이메일 시퀀스 3개 설계해줘

# 법무 도메인 — NDA 검토
@legal 이 콜라보 계약서 주요 리스크 검토해줘

# 데이터 도메인 — SQL 작성
@data Snowflake에서 채널별 월간 매출 추이 쿼리 짜줘
```

### 실습 3: FPOF vs KW 라우팅 비교

같은 주제를 다른 컨텍스트로 요청하여 라우팅 차이를 확인합니다:

```
# FPOF 라우팅 → competitive-battlecard
"와키윌리 vs 커버낫 경쟁 비교표 만들어줘"

# KW 플러그인 라우팅 → marketing:competitive-brief
"@marketing SaaS 경쟁사 분석 브리프 만들어줘"
```

---

## 6. 마켓플레이스 등록 구조

프로젝트에 등록된 7개 마켓플레이스:

| 마켓플레이스 | GitHub 소스 | 제공 플러그인 |
|-------------|------------|-------------|
| **claude-plugins-official** | anthropics/claude-plugins-official | 7개 (기본 내장, 별도 등록 불필요) |
| **knowledge-work-plugins** | anthropics/knowledge-work-plugins | 18개 |
| **anthropic-agent-skills** | anthropics/skills | document-skills |
| **claude-code-plugins** | anthropics/claude-code | frontend-design |
| **thedotmack** | thedotmack/claude-mem | claude-mem |
| **claude-dashboard** | uppinote20/claude-dashboard | claude-dashboard |
| **supabase-agent-skills** | supabase/agent-skills | postgres-best-practices |
| **obsidian-skills** | kepano/obsidian-skills | obsidian |

---

## 7. 새 팀원 온보딩 체크리스트

GitHub 클론 후 바로 사용 가능한지 확인:

- [ ] `git clone` 완료
- [ ] Claude Code 최신 버전 설치
- [ ] 프로젝트 폴더에서 Claude Code 실행
- [ ] 플러그인 자동 설치 확인 (첫 실행 시 설치 프롬프트)
- [ ] `/status`로 FPOF 상태 확인
- [ ] `@marketing` 등 KW 플러그인 동작 확인

---

## 8. 트러블슈팅

### 플러그인이 활성화되지 않을 때
```bash
# settings.json 문법 확인
python3 -m json.tool .claude/settings.json

# 글로벌 설치 상태 확인
cat ~/.claude/plugins/installed_plugins.json | python3 -m json.tool | head -20
```

### 특정 플러그인만 비활성화하기
`.claude/settings.json`에서 해당 플러그인을 `false`로 변경:
```json
"finance@knowledge-work-plugins": false
```

### 마켓플레이스 업데이트
```bash
# Claude Code에서 플러그인 업데이트
claude /plugin update
```

---

## 핵심 정리

| 항목 | 내용 |
|------|------|
| **총 플러그인** | 31개 (공식 7 + KW 18 + 전문도구 6) |
| **마켓플레이스** | 7개 (+ 공식 1개 기본 내장) |
| **설정 파일** | `.claude/settings.json` (git에 포함) |
| **라우팅** | 패션/브랜드 → FPOF, 범용 비즈니스 → KW 플러그인 |
| **명시적 호출** | `@도메인` 접두사 (예: `@sales`, `@legal`) |
| **클론 사용자** | 자동 설치/활성화 (추가 설정 불필요) |
