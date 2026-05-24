# 키즈노트 마크다운 백업

> 이 프로젝트는 [redchupa/kidsnote-backup](https://github.com/redchupa/kidsnote-backup)을
> fork한 뒤, Notion 백업 대신 Obsidian Markdown 백업 용도로 수정한 버전입니다.

키즈노트 데이터를 Obsidian에서 관리하기 좋은 Markdown 파일로 내려받는 도구입니다.

키즈노트의 알림장, 공지사항, 사진, 동영상, 첨부파일을 다운로드해서 로컬 Markdown 노트와
assets 폴더로 저장합니다. 두 자녀 계정을 기준으로 만들었지만, 아이 이름을 기준으로 폴더를
나누기 때문에 한 명 또는 세 명 이상이어도 동작합니다.

## 0. 사전 준비

> 약 5분 정도 걸립니다. 이미 가입과 로그인이 되어 있다면 1분 안에 끝납니다.

시작 전에 아래 환경을 준비합니다.

- 데스크톱 또는 노트북
- 인터넷 연결
- Chrome 또는 Edge 브라우저
- 키즈노트 계정
- GitHub 계정
- Obsidian vault 위치

브라우저 탭을 열어 두 사이트에 로그인되어 있는지 확인합니다.

| 사이트 | URL | 확인할 것 |
|---|---|---|
| 키즈노트 | https://www.kidsnote.com | 로그인 후 내 자녀 알림장 또는 메인 화면이 보여야 함 |
| GitHub | https://github.com | 로그인 후 우측 상단에 내 프로필 사진이 보여야 함 |

Obsidian은 백업 결과를 옮겨둘 vault 위치만 미리 정해두면 됩니다.

```text
%Obsidian_Vault%\KidsNote Backup\
```

이 README를 휴대폰으로 보고 있다면, 휴대폰은 안내 확인용으로 두고 실제 작업은 노트북이나
데스크톱 브라우저에서 진행하는 것이 편합니다.

## 1. 생성되는 결과

기본 로컬 저장 경로는 다음과 같습니다.

```text
%Obsidian_Vault%\KidsNote Backup\
```

생성되는 폴더 구조는 다음과 같습니다.

```text
KidsNote Backup/
├── 아이(1)/
│   ├── 2026/
│   │   └── 05/
│   │       ├── 2026-05-13_[교사]_알림장.md
│   │       ├── 2026-05-13_[부모]_알림장.md
│   │       └── assets/
│   │           ├── 20260513_1392587707_001.jpg
│   │           └── ...
│   ├── 공지사항/
│   │   └── 2026/
│   │       └── 05/
│   │           ├── 2026-05-13_준비물 안내.md
│   │           └── assets/
│   └── _index/
│       ├── monthly-growth-stories.md
│       └── milestones.md
└── 아이(2)/
    ├── 2026/
    ├── 공지사항/
    └── _index/
```

알림장 파일명은 사람이 읽기 쉽게 저장됩니다.

```text
2026-05-13_[교사]_알림장.md
2026-05-13_[부모]_알림장.md
2026-05-13_[공지]_알림장.md
```

키즈노트 내부 ID는 파일명에는 드러내지 않고, 중복 방지와 검색을 위해 frontmatter에만
저장합니다.

```md
---
type: kidsnote-report
report_id: 1392587707
date: "2026-05-13"
author: "teacher"
child: "아이(1)"
weather: "sunny"
tags:
  - kidsnote
  - alimnota
---

> ☀️ 날씨: 맑음

## Summary

...

## Original

...

## Photos

![20260513_1392587707_001.jpg](assets/20260513_1392587707_001.jpg)

## Menu

...
```

Obsidian에서 속성 영역이 거슬리면 아래 설정으로 숨길 수 있습니다.

```text
Settings -> Editor -> Properties in document -> Hidden
```

## 2. 주요 기능

- `--all-children` 옵션으로 계정의 모든 아이를 export
- 알림장을 Obsidian 친화적인 Markdown 파일로 저장
- 키즈노트 공지사항을 아이별 `공지사항/` 폴더에 저장
- 사진, 동영상, 일반 첨부파일 다운로드
- JPEG 사진의 GPS EXIF 정보 제거
- 너무 큰 JPEG 사진은 Obsidian vault에 적당한 크기로 축소
- 알림장 본문 상단에 날씨를 이모지와 텍스트로 표시
- 일일 식단은 사진과 첨부파일 뒤, 마지막 섹션으로 추가
- `report_id`, `notice_id` frontmatter를 이용해 중복 다운로드 방지
- Ollama가 있으면 LLM 요약과 index 페이지 생성

## 3. LLM으로 생성되는 내용

Ollama가 사용 가능하면 다음 내용이 추가됩니다.

- 각 알림장의 `## Summary`
- `_index/monthly-growth-stories.md`
- `_index/milestones.md`

GitHub Actions에서는 workflow 안에서 Ollama와 `llama3.1:8b` 모델을 실행합니다.
로컬에서 실행할 때도 `OLLAMA_HOST`가 설정되어 있으면 같은 방식으로 사용할 수 있습니다.
외부 유료 LLM API key는 필요하지 않습니다.

Ollama를 사용할 수 없는 경우에도 알림장, 공지사항, 사진, 첨부파일은 정상적으로 저장됩니다.
LLM 섹션만 생략됩니다.

## 4. 키즈노트 sessionid 쿠키 가져오기

> 약 3분 정도 걸립니다.
>
> 시작 전 확인: Chrome 또는 Edge 브라우저에서 키즈노트 로그인이 완료되어 있어야 합니다.

이 도구는 키즈노트에 로그인된 브라우저의 `sessionid` 쿠키를 사용합니다. 여기가 가장 어려워
보이지만 차근차근 따라하면 30초 안에 끝납니다.

Chrome 외에도 Edge는 같은 화면에서 진행할 수 있고, Firefox는 `F12` → `저장소`에서 확인할 수
있습니다. 아래는 Chrome 기준입니다.

### 4-1. 키즈노트 로그인 + 개발자 도구 열기

1. Chrome으로 https://www.kidsnote.com 에 접속한 뒤 평소처럼 로그인합니다.
   - 카카오 SSO로 로그인하는 경우 `카카오로 로그인` → 카카오 페이지 → 로그인 → 키즈노트로 돌아오면 됩니다.
   - 로그인 후 자녀 알림장 화면 또는 메인 화면이 보여야 합니다.
2. 키즈노트가 로그인된 상태에서 키보드 `F12` 키를 눌러 개발자 도구를 엽니다.
   - `F12`가 안 먹는 노트북은 `Fn + F12` 또는 `Ctrl + Shift + I`를 사용합니다.
   - 그래도 안 되면 Chrome 우측 상단 `⋮` → `도구 더보기` → `개발자 도구`를 클릭합니다.

### 4-2. Application 탭에서 쿠키 찾기

1. 개발자 도구 상단 메뉴에서 `Application`을 클릭합니다.
   - 한국어 Chrome에서도 메뉴 이름은 보통 영문 그대로 보입니다.
   - 안 보이면 메뉴 끝의 `>>`를 클릭한 뒤 `Application`을 선택합니다.
2. 왼쪽 사이드바에서 `Storage` 아래 `Cookies` 폴더를 펼칩니다.
3. `https://www.kidsnote.com`을 클릭합니다.
4. 오른쪽에 `Name`, `Value`, `Domain`, `Path`, `Expires` 같은 컬럼이 있는 표가 나타납니다.

### 4-3. sessionid 행 찾아서 값 복사

표에서 다음 두 조건을 모두 만족하는 행을 찾습니다.

- `Name` 컬럼이 정확히 `sessionid`
- `Domain` 컬럼이 정확히 `.kidsnote.com`

그 행의 `Value` 컬럼 값을 복사합니다.

- 방법 A: 셀이 다 보이면 더블클릭 후 `Ctrl+C`
- 방법 B: 셀이 잘려 보이면 행을 클릭한 뒤 표 하단의 `Cookie Value` 영역에서 값을 드래그 선택 후 `Ctrl+C`

![Chrome 개발자 도구에서 sessionid 쿠키 위치](images/chrome-cookie-sessionid.png)

쿠키 값 예시:

```text
ycen2ydnwm2vsoj3zxe618k5nugt7j33
```

메모장에 잠시 붙여두세요.

### 4-4. 헷갈리지 말아야 할 쿠키

쿠키 표를 보면 `sessionid`처럼 보이는 이름이 여럿 있을 수 있습니다. 다음은 모두 다른 용도이므로
무시합니다.

| 쿠키 이름 | 정체 |
|---|---|
| `_kau`, `_kawlt`, `_kdt`, `_karb`, `_kasl` 등 `_k*` | Domain이 `.kakao.com`인 카카오 로그인/광고용 쿠키 |
| `ch-session-127152`, `ch-veil-id` | 채널톡 세션 |
| `current_user` | 사용자 ID 표시용. 값이 짧고 sessionid가 아님 |
| `_kn_visitorId`, `_gcl_au`, `_ga*`, `_dd_s` | 방문자 통계용 |

정답은 단 하나입니다.

```text
Name: sessionid
Domain: .kidsnote.com
```

성공하면 메모장에 32자 정도의 영문+숫자 문자열이 있어야 합니다.

### 4-5. 쿠키 추출이 막혔다면

| 증상 | 원인 / 해결 |
|---|---|
| `sessionid` 행이 없음 | 키즈노트 로그아웃 상태일 수 있습니다. 로그인 상태를 다시 확인합니다. |
| `Application` 탭이 없음 | 개발자 도구 창이 너무 좁을 수 있습니다. 창 크기를 늘리거나 `>>` 더보기에서 선택합니다. |
| 쿠키 값이 너무 길어서 셀이 잘림 | 하단 `Cookie Value` 패널에서 드래그 선택합니다. |
| `F12`, `Ctrl+Shift+I` 모두 안 먹음 | 시크릿 모드일 수 있습니다. 일반 창에서 다시 시도합니다. |

이 `sessionid`는 약 30일 후 만료됩니다. 만료되면 이 섹션을 다시 진행한 뒤 GitHub Secret 값을
업데이트하면 됩니다.

## 5. GitHub에 비밀 값 등록하기

> 약 3분 정도 걸립니다.
>
> 시작 전 확인: 메모장에 `sessionid` 쿠키 값이 있고, GitHub repository 페이지를 열 수 있어야 합니다.

방금 복사한 `sessionid` 값을 GitHub repository에 안전하게 저장합니다. GitHub Secrets는 암호화되어
저장되며, workflow 실행 시에만 사용됩니다.

### 5-1. repository Settings로 이동

1. GitHub에서 이 repository 페이지로 이동합니다.
2. 페이지 가운데 메뉴 줄의 `Settings`를 클릭합니다.
   - 우측 상단 프로필 사진 옆 `Settings`가 아니라, repository 메뉴의 `Settings`입니다.

### 5-2. Secrets 페이지로 이동

1. 좌측 사이드바에서 `Secrets and variables`를 클릭합니다.
2. 하위 메뉴에서 `Actions`를 클릭합니다.
3. 페이지 우측 상단의 `New repository secret` 버튼을 클릭합니다.

### 5-3. KIDSNOTE_SESSION_COOKIE 등록

아래 값 하나만 등록하면 됩니다.

| Name | Secret 값 |
|---|---|
| `KIDSNOTE_SESSION_COOKIE` | 4단계에서 복사한 `sessionid` 쿠키 값 |

등록 방법:

1. `Name` 칸에 `KIDSNOTE_SESSION_COOKIE`를 입력합니다.
2. `Secret` 칸에 쿠키 값을 붙여넣습니다.
3. 앞뒤 공백이나 줄바꿈이 들어가지 않았는지 확인합니다.
4. `Add secret` 버튼을 클릭합니다.

이름 오타가 가장 흔한 실수입니다. 반드시 대문자와 언더바까지 아래 이름과 정확히 같아야 합니다.

```text
KIDSNOTE_SESSION_COOKIE
```

성공하면 Secrets 목록에 아래처럼 표시됩니다. 값은 보이지 않고 `Updated` 시간만 보이는 것이
정상입니다.

```text
KIDSNOTE_SESSION_COOKIE       Updated now
```

### 5-4. Secret 등록이 막혔다면

| 증상 | 원인 / 해결 |
|---|---|
| `Settings` 탭이 안 보임 | 다른 사람의 repo를 보고 있을 수 있습니다. 본인 repository인지 확인합니다. |
| `Secrets and variables` 메뉴가 없음 | 좌측 사이드바 아래쪽 `Code and automation` 섹션을 확인합니다. |
| Add secret 후 목록에 없음 | 이름에 공백 또는 특수문자가 들어갔을 수 있습니다. 다시 등록합니다. |
| 이전에 만든 다른 Secret이 있음 | `KIDSNOTE_SESSION_COOKIE`가 정확히 있으면 다른 Secret은 이 workflow에서 사용하지 않습니다. |

### 5-5. 로컬에서 실행하려면

GitHub Actions가 아니라 내 PC에서 증분 백업을 실행하려면 repository root에 `.env` 파일을 만들고
아래처럼 저장합니다.

```env
KIDSNOTE_SESSION_COOKIE=your_sessionid_value_here
```

이 값은 4단계에서 복사한 `sessionid` 쿠키 값입니다. `.env` 파일은 절대 commit하지 마세요.
이 repository의 `.gitignore`에는 `.env`가 포함되어 있어서 정상적으로는 Git에 올라가지 않습니다.

## 6. GitHub Actions로 첫 대량 백업하기

처음 전체 데이터를 받을 때는 오래 걸릴 수 있습니다. 과거 알림장, 공지사항, 사진, 동영상,
첨부파일을 모두 받고 Ollama 모델도 내려받기 때문입니다. 이 첫 백업은 GitHub Actions에서
실행하면 PC를 꺼두어도 계속 진행됩니다.

대략적인 시간은 알림장 개수와 사진 개수에 따라 달라집니다.

```text
최근 몇 개 테스트        15~25분
50개 미만                5~30분
100~200개                4~10시간
300개 이상 + 사진 많음   여러 번의 workflow 실행 필요
```

첫 실행이 5분보다 오래 걸리는 가장 큰 이유는 GitHub Actions가 무료 Ollama 모델
`llama3.1:8b`를 처음 다운로드하기 때문입니다. 모델은 cache에 저장되므로 두 번째 실행부터는
훨씬 빠르게 시작합니다.

### 6-1. 시작 전 확인

아래 항목이 준비되어 있어야 합니다.

- repository secret `KIDSNOTE_SESSION_COOKIE` 등록
- `Actions` 탭에서 workflow 활성화
- Obsidian vault의 최종 저장 위치 확인

### 6-2. Actions 활성화

fork한 repository에서 처음 실행하는 경우 GitHub가 workflow 실행을 막아둡니다.

1. repository 상단의 `Actions` 탭을 클릭합니다.
2. `Workflows aren't running on this fork.` 안내가 보이면 확인합니다.
3. `I understand my workflows, go ahead and enable them` 버튼을 클릭합니다.

이미 활성화되어 있으면 이 화면 없이 workflow 목록이 바로 보입니다.

### 6-3. 첫 실행은 안전하게 테스트

처음에는 전체 백업을 바로 돌리지 말고 최근 몇 개만 테스트하는 것을 추천합니다.

1. 좌측 workflow 목록에서 `Kidsnote -> Obsidian Markdown`을 클릭합니다.
2. 우측 상단의 `Run workflow` 드롭다운을 클릭합니다.
3. `Branch: main`은 그대로 둡니다.
4. 아래 값으로 실행합니다.

```text
limit: 5
monthly_sample: false
force_refresh: true
```

15~25분 정도 기다린 뒤 workflow가 성공하면 artifact를 확인합니다.

```text
kidsnote-obsidian-export
```

artifact를 다운로드하고 압축을 풀어 아래 항목이 정상인지 확인합니다.

- 알림장 Markdown 파일 생성
- 공지사항 Markdown 파일 생성
- 사진과 첨부파일이 `assets/` 폴더에 저장
- 본문 상단 날씨 표시
- `Summary` 섹션 생성
- `_index/monthly-growth-stories.md`
- `_index/milestones.md`

`limit=5`일 때 LLM 요약과 index 문서는 빈약할 수 있습니다. 알림장이 몇 개 없으면 성장 기록이나
마일스톤을 풍부하게 만들기 어렵기 때문에, 이 실행은 셋업 검증용으로 보면 됩니다.

### 6-4. 전체 백업 실행

테스트가 정상이면 같은 방법으로 다시 실행하되 이번에는 `limit`을 비워둡니다.

```text
limit:
monthly_sample: false
force_refresh: false
```

GitHub-hosted runner는 job 하나를 최대 6시간까지 실행할 수 있으므로, workflow의
`timeout-minutes`는 `360`으로 설정되어 있습니다. 스크립트는 6시간 하드캡에 가까워지기 전에
작업을 멈추고, 지금까지 만들어진 Markdown 파일을 artifact/cache로 남기도록 설계되어 있습니다.

이미 만들어진 노트는 다음 실행에서 `report_id`, `notice_id` frontmatter로 감지되어 자동으로
건너뜁니다. 따라서 첫 백업이 한 번에 끝나지 않아도 다음 수동 실행이나 다음 cron 실행에서
이어 받을 수 있습니다.

현재 workflow는 한국 시간 기준 매일 오후 11시에 자동 실행됩니다.

```text
KST 23:00 = UTC 14:00
cron: 0 14 * * *
```

동시에 두 workflow가 겹쳐 실행되지 않도록 아래 설정도 들어 있습니다.

```yaml
concurrency:
  group: kidsnote-to-obsidian
  cancel-in-progress: false
```

이미 실행 중인 workflow가 있으면 다음 실행은 queue에서 기다리고, 진행 중인 작업을 취소하지
않습니다.

### 6-5. artifact를 Obsidian vault로 옮기기

workflow가 완료되면 `kidsnote-obsidian-export` artifact를 다운로드합니다. 압축을 푼 뒤,
아이별 폴더를 아래 경로에 복사합니다.

artifact 보관 기간은 32일로 설정되어 있습니다. 매일 내려받지 않아도, 한 달에 한 번 정도
최신 성공 run의 artifact를 받으면 그 시점까지의 누적 백업을 가져올 수 있습니다.

```text
%Obsidian_Vault%\KidsNote Backup\
```

최종 구조는 이렇게 되어야 합니다.

```text
KidsNote Backup/
├── 아이(1)/
└── 아이(2)/
```

아래처럼 한 단계 더 깊게 들어가면 안 됩니다.

```text
KidsNote Backup/
└── obsidian-export/
    ├── 아이(1)/
    └── 아이(2)/
```

### 6-6. 진행 상황 보기

workflow 실행 중인 run을 클릭하면 로그를 볼 수 있습니다.

1. `Actions` 탭에서 실행 중인 run을 클릭합니다.
2. `export` job을 클릭합니다.
3. `Export Kidsnote -> Markdown` step을 펼칩니다.

로그는 이런 식으로 출력됩니다.

```text
Markdown child=아이(1) id=5000421: fetched 342 reports
  child=아이(1) detail enrich 5/342 done
Markdown child=아이(1)  12.3% (42/342) | id=1390908410 images=5 files=0
Markdown child=아이(1): fetched 20 notices
Markdown notice export child=아이(1) DONE: 3 new notes, 17 already existed
Markdown all-children export DONE: 45 report notes, 297 report skips, 3 notice notes, 17 notice skips
```

로그의 의미는 다음과 같습니다.

- `images=N`: 저장된 사진 개수
- `files=N`: 저장된 일반 첨부파일 개수
- `already existed`: 기존 Markdown 파일이 있어서 건너뛴 항목
- `time budget reached`: 6시간 제한 전에 안전하게 멈춘 상태

GitHub Actions 로그는 자동 새로고침이 늦을 수 있습니다. 최신 로그가 안 보이면 페이지를
새로고침하세요.

### 6-7. `force_refresh` 옵션

일반 사용은 `force_refresh=false`로 충분합니다.

다음 경우에는 `force_refresh=true`를 사용할 수 있습니다.

- Markdown 템플릿을 바꾼 뒤 기존 노트를 다시 만들고 싶을 때
- 파일명 규칙을 바꾼 뒤 기존 파일을 정리하고 싶을 때
- LLM Summary와 index 문서를 새 prompt 기준으로 다시 만들고 싶을 때

단, 기존 노트를 다시 생성하므로 첫 백업과 비슷하게 오래 걸릴 수 있습니다.

### 6-8. cron 자동 실행을 끄고 싶다면

가끔 수동으로만 돌리고 싶다면 workflow를 비활성화할 수 있습니다.

```text
Actions -> Kidsnote -> Obsidian Markdown -> ... -> Disable workflow
```

이렇게 하면 cron과 수동 실행이 모두 비활성화됩니다. 다시 사용하려면 같은 위치에서 workflow를
활성화하면 됩니다.

## 7. 로컬 증분 백업

첫 대량 백업 이후에는 로컬 실행이 더 편합니다. 기존 Markdown 파일의 `report_id`와
`notice_id`를 읽고, 이미 받은 항목은 건너뜁니다. 새 알림장과 새 공지사항만 직접
Obsidian vault에 저장됩니다.

실행:

```powershell
.\tools\kidsnote_fetch\export-obsidian-local.ps1
```

최근 몇 개만 테스트:

```powershell
.\tools\kidsnote_fetch\export-obsidian-local.ps1 -Limit 5
```

LLM 없이 원문과 첨부파일만 빠르게 확인:

```powershell
.\tools\kidsnote_fetch\export-obsidian-local.ps1 -NoLlm
```

파일명이나 템플릿 변경 후 기존 노트를 다시 생성:

```powershell
.\tools\kidsnote_fetch\export-obsidian-local.ps1 -Limit 5 -ForceRefresh
```

## 8. Python으로 직접 실행하기

GitHub Actions와 PowerShell helper는 내부적으로 모두 `fetch.py`를 호출합니다.

동일한 로컬 명령은 다음과 같습니다.

```powershell
python tools\kidsnote_fetch\fetch.py `
  --auth-mode session-cookie-env `
  --export-markdown `
  --all-children `
  --no-local-save `
  --backup-root "%Obsidian_Vault%\KidsNote Backup"
```

자주 쓰는 옵션:

```text
--limit N          아이별 최근 N개 알림장만 export
--monthly-sample  테스트용으로 월별 알림장 1개씩 export
--force-refresh   기존 노트를 다시 생성하고 예전 파일명을 정리
--no-llm          LLM 요약과 index 페이지 생성 생략
--no-menus        교사 알림장에 일일 식단을 붙이지 않음
--no-notices      키즈노트 공지사항을 export하지 않음
```

## 9. 중복 방지 방식

exporter는 기존 Markdown 파일의 frontmatter를 읽습니다.

```yaml
report_id: 1392587707
notice_id: 123456
```

같은 ID가 이미 있으면 해당 항목은 건너뜁니다.

`--force-refresh`를 사용하면 기존 노트를 다시 생성합니다. 파일명이나 레이아웃을 바꾼 뒤
기존 노트를 정리할 때 유용합니다. 예전 파일명에 숫자 ID가 포함되어 있던 중복 노트도
새 파일명으로 다시 쓰면서 정리됩니다.

## 10. 개인정보와 보안

- 키즈노트 session cookie는 비밀 값입니다. GitHub Secrets 또는 `.env`에만 저장하세요.
- `.env`는 commit하지 마세요.
- JPEG 사진의 GPS EXIF 정보는 저장 전에 제거됩니다.
- LLM 처리는 Ollama로 실행되며, 유료 외부 API를 사용하지 않습니다.

## 11. 문제 해결

### 11-1. GitHub Action은 성공했는데 PC에 파일이 없습니다

GitHub Actions는 GitHub 서버에서 실행됩니다. `kidsnote-obsidian-export` artifact를
다운로드한 뒤 로컬 Obsidian vault에 복사해야 합니다.

### 11-2. 로컬 실행에서 `KIDSNOTE_SESSION_COOKIE missing`이 나옵니다

repository root에 `.env` 파일을 만들고 아래 값을 넣으세요.

```env
KIDSNOTE_SESSION_COOKIE=your_sessionid_value_here
```

### 11-3. 템플릿을 바꿨는데 기존 노트가 바뀌지 않습니다

기존 노트는 기본적으로 skip됩니다. 다시 생성하려면 `--force-refresh`를 사용하세요.

```powershell
.\tools\kidsnote_fetch\export-obsidian-local.ps1 -ForceRefresh
```

### 11-4. Summary가 없습니다

`Summary`는 Ollama가 생성합니다. 다음 경우에는 생략됩니다.

- Ollama를 사용할 수 없음
- 알림장 본문이 너무 짧음
- 이미 존재하는 노트라 skip됨

기존 노트의 Summary를 다시 만들고 싶다면 `-ForceRefresh`를 사용하세요.

## 12. License

MIT. 자세한 내용은 [LICENSE](LICENSE)를 확인하세요.
