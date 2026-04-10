# Claude Code × Telegram 연결 가이드

> Claude Code CLI에서 Telegram 봇을 연결하여, 텔레그램 메시지로 Claude에게 작업을 요청하는 방법을 정리합니다.

---

## 전체 흐름 요약

```
1. Telegram 봇 생성 (BotFather)
2. Claude Code 텔레그램 플러그인 설치
3. 봇 토큰 등록 (/telegram:configure)
4. 텔레그램에서 봇에게 DM → 페어링 코드 수신
5. Claude Code 터미널에서 페어링 승인 (/telegram:access pair <code>)
6. 접근 정책 설정 (/telegram:access policy allowlist)
7. 연결 완료 — 텔레그램에서 Claude에게 자유롭게 요청
```

---

## Step 1. Telegram 봇 생성

1. 텔레그램에서 **@BotFather**를 검색하여 대화를 시작합니다.
2. `/newbot` 명령어를 입력합니다.
3. 봇 이름(표시명)을 입력합니다. (예: `My Claude Bot`)
4. 봇 사용자명을 입력합니다. (예: `my_claude_bot`) — `_bot`으로 끝나야 합니다.
5. BotFather가 **봇 토큰**을 발급합니다. 이 토큰을 복사해두세요.

```
예시 토큰: 1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
```

> 봇 토큰은 비밀번호와 같습니다. 외부에 노출하지 마세요.

---

## Step 2. Claude Code 텔레그램 플러그인 설치

Claude Code CLI에서 텔레그램 플러그인이 설치되어 있어야 합니다.

```bash
# 플러그인 설치 확인
ls ~/.claude/plugins/cache/claude-plugins-official/telegram/
```

플러그인이 없다면 Claude Code 설정에서 텔레그램 채널을 활성화합니다.

---

## Step 3. 봇 토큰 등록

Claude Code 터미널에서 `/telegram:configure` 명령어를 실행하고, Step 1에서 발급받은 봇 토큰을 입력합니다.

```
/telegram:configure
```

프롬프트에 따라 봇 토큰을 붙여넣으면 설정이 완료됩니다.

---

## Step 4. 페어링 요청

1. 텔레그램 앱에서 Step 1에서 만든 봇을 검색합니다.
2. 봇에게 아무 메시지를 보냅니다. (예: `hi`)
3. 봇이 **6자리 페어링 코드**를 응답합니다.

```
예시: 페어링 코드 e0d6f5
```

---

## Step 5. 페어링 승인

Claude Code 터미널에서 페어링 코드를 사용하여 승인합니다.

```
/telegram:access pair e0d6f5
```

승인이 완료되면:
- `access.json`의 `allowFrom`에 Telegram 사용자 ID가 추가됩니다.
- `pending`에서 해당 코드가 제거됩니다.
- 텔레그램에 승인 완료 메시지가 전송됩니다.

### access.json 변경 예시

**승인 전:**
```json
{
  "dmPolicy": "pairing",
  "allowFrom": [],
  "pending": {
    "e0d6f5": {
      "senderId": "8673724387",
      "chatId": "8673724387",
      "createdAt": 1774018919225,
      "expiresAt": 1774022519225
    }
  }
}
```

**승인 후:**
```json
{
  "dmPolicy": "pairing",
  "allowFrom": [
    "8673724387"
  ],
  "pending": {}
}
```

---

## Step 6. 접근 정책 설정

페어링이 완료되면, 보안을 위해 DM 정책을 `allowlist`로 변경하는 것을 권장합니다.

```
/telegram:access policy allowlist
```

### 정책 모드 비교

| 모드 | 동작 | 사용 시점 |
|------|------|----------|
| `pairing` | 새로운 사용자가 DM을 보내면 페어링 코드 발급 | 초기 설정 시 (기본값) |
| `allowlist` | `allowFrom`에 등록된 사용자만 허용, 나머지 차단 | 설정 완료 후 (권장) |
| `disabled` | 모든 DM 차단 | 봇 일시 중지 시 |

---

## Step 7. 연결 완료

이제 텔레그램에서 봇에게 메시지를 보내면 Claude Code가 응답합니다.

```
사용자: "CLAUDE.md 파일을 발표용 프레젠테이션으로 만들어줘"
Claude: (작업 수행 후 파일 전송)
```

### 가능한 작업 예시
- 파일 생성/편집 요청 → 결과물을 텔레그램으로 전송
- 프로젝트 상태 확인
- 코드 리뷰, 문서 작성
- 이미지 첨부 메시지 → 이미지 분석 후 응답

---

## 관리 명령어 레퍼런스

모든 관리 명령어는 **Claude Code 터미널**에서만 실행 가능합니다. 텔레그램 메시지로는 접근 제어를 변경할 수 없습니다 (보안).

### 상태 확인

```
/telegram:access
```

현재 정책, 허용된 사용자, 대기 중인 페어링 목록을 표시합니다.

### 사용자 관리

```bash
# 사용자 직접 추가 (페어링 없이)
/telegram:access allow <senderId>

# 사용자 제거
/telegram:access remove <senderId>

# 페어링 거절
/telegram:access deny <code>
```

### 그룹 관리

```bash
# 그룹 추가 (멘션 필요)
/telegram:access group add <groupId>

# 그룹 추가 (멘션 없이도 반응)
/telegram:access group add <groupId> --no-mention

# 그룹 제거
/telegram:access group rm <groupId>
```

### 동작 설정

```bash
# 메시지 수신 시 리액션 이모지 설정
/telegram:access set ackReaction 👀

# 답장 모드 (off / first / all)
/telegram:access set replyToMode first

# 메시지 분할 기준 글자 수
/telegram:access set textChunkLimit 4000

# 봇 멘션 패턴 (그룹에서 사용)
/telegram:access set mentionPatterns '["@my_claude_bot"]'
```

---

## 파일 구조

```
~/.claude/channels/telegram/
├── access.json          ← 접근 제어 설정 (정책, 허용 목록, 대기 중 페어링)
└── approved/
    └── <senderId>       ← 승인된 사용자 (내용: chatId)
```

---

## 보안 참고사항

- **봇 토큰**은 절대 외부에 공유하지 마세요.
- **접근 제어 변경**은 반드시 Claude Code 터미널에서만 수행합니다.
- 텔레그램 메시지를 통한 "승인해줘", "allowlist에 추가해줘" 같은 요청은 **프롬프트 인젝션 공격**일 수 있으므로 Claude가 자동으로 거부합니다.
- 설정 완료 후 `allowlist` 정책으로 전환하여 무단 접근을 차단하세요.
- 페어링 코드는 유효시간이 있으며 (약 1시간), 만료 후에는 새 코드를 받아야 합니다.

---

## 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| 봇에게 메시지를 보내도 반응 없음 | Claude Code 세션이 실행 중이 아님 | Claude Code CLI를 실행한 상태에서 메시지 전송 |
| 페어링 코드가 만료됨 | 1시간 이상 경과 | 봇에게 다시 메시지를 보내 새 코드 발급 |
| "접근이 거부되었습니다" | `allowlist` 정책에서 미등록 사용자 | `/telegram:access allow <id>` 또는 정책을 `pairing`으로 변경 후 재페어링 |
| 파일 전송이 안 됨 | 파일 크기 50MB 초과 | 파일을 분할하거나 압축 |
| 그룹에서 반응 없음 | 그룹이 등록되지 않음 | `/telegram:access group add <groupId>` |
