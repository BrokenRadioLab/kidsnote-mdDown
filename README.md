# 키즈노트 마크다운 백업

> 이 프로젝트는 [redchupa/kidsnote-backup](https://github.com/redchupa/kidsnote-backup)을
> fork한 뒤, Notion 백업 대신 Obsidian Markdown 백업 용도로 수정한 버전입니다.

키즈노트 데이터를 Obsidian에서 관리하기 좋은 Markdown 파일로 내려받는 도구입니다.

키즈노트의 알림장, 공지사항, 사진, 동영상, 첨부파일을 다운로드해서 로컬 Markdown 노트와
assets 폴더로 저장합니다. 두 자녀 계정을 기준으로 만들었지만, 아이 이름을 기준으로 폴더를
나누기 때문에 한 명 또는 세 명 이상이어도 동작합니다.

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
│   │       ├── 2026-05-13_교사알림장.md
│   │       ├── 2026-05-13_부모알림장.md
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
2026-05-13_교사알림장.md
2026-05-13_부모알림장.md
2026-05-13_공지알림장.md
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

## 4. 필요한 Secret

이 도구는 키즈노트에 로그인된 브라우저의 세션을 사용합니다.

필요한 값은 `kidsnote.com`의 `sessionid` 쿠키 값입니다.

GitHub Actions에서 실행하려면 repository secret에 아래 이름으로 저장합니다.

```text
KIDSNOTE_SESSION_COOKIE
```

로컬에서 실행하려면 repository root에 `.env` 파일을 만들고 아래처럼 저장합니다.

```env
KIDSNOTE_SESSION_COOKIE=your_sessionid_value_here
```

`.env` 파일은 절대 commit하지 마세요.

## 5. GitHub Actions로 첫 대량 백업하기

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

### 5-1. 시작 전 확인

아래 항목이 준비되어 있어야 합니다.

- repository secret `KIDSNOTE_SESSION_COOKIE` 등록
- `Actions` 탭에서 workflow 활성화
- Obsidian vault의 최종 저장 위치 확인

### 5-2. Actions 활성화

fork한 repository에서 처음 실행하는 경우 GitHub가 workflow 실행을 막아둡니다.

1. repository 상단의 `Actions` 탭을 클릭합니다.
2. `Workflows aren't running on this fork.` 안내가 보이면 확인합니다.
3. `I understand my workflows, go ahead and enable them` 버튼을 클릭합니다.

이미 활성화되어 있으면 이 화면 없이 workflow 목록이 바로 보입니다.

### 5-3. 첫 실행은 안전하게 테스트

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

### 5-4. 전체 백업 실행

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

### 5-5. artifact를 Obsidian vault로 옮기기

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

### 5-6. 진행 상황 보기

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

### 5-7. `force_refresh` 옵션

일반 사용은 `force_refresh=false`로 충분합니다.

다음 경우에는 `force_refresh=true`를 사용할 수 있습니다.

- Markdown 템플릿을 바꾼 뒤 기존 노트를 다시 만들고 싶을 때
- 파일명 규칙을 바꾼 뒤 기존 파일을 정리하고 싶을 때
- LLM Summary와 index 문서를 새 prompt 기준으로 다시 만들고 싶을 때

단, 기존 노트를 다시 생성하므로 첫 백업과 비슷하게 오래 걸릴 수 있습니다.

### 5-8. cron 자동 실행을 끄고 싶다면

가끔 수동으로만 돌리고 싶다면 workflow를 비활성화할 수 있습니다.

```text
Actions -> Kidsnote -> Obsidian Markdown -> ... -> Disable workflow
```

이렇게 하면 cron과 수동 실행이 모두 비활성화됩니다. 다시 사용하려면 같은 위치에서 workflow를
활성화하면 됩니다.

## 6. 로컬 증분 백업

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

## 7. Python으로 직접 실행하기

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

## 8. 중복 방지 방식

exporter는 기존 Markdown 파일의 frontmatter를 읽습니다.

```yaml
report_id: 1392587707
notice_id: 123456
```

같은 ID가 이미 있으면 해당 항목은 건너뜁니다.

`--force-refresh`를 사용하면 기존 노트를 다시 생성합니다. 파일명이나 레이아웃을 바꾼 뒤
기존 노트를 정리할 때 유용합니다. 예전 파일명에 숫자 ID가 포함되어 있던 중복 노트도
새 파일명으로 다시 쓰면서 정리됩니다.

## 9. 개인정보와 보안

- 키즈노트 session cookie는 비밀 값입니다. GitHub Secrets 또는 `.env`에만 저장하세요.
- `.env`는 commit하지 마세요.
- JPEG 사진의 GPS EXIF 정보는 저장 전에 제거됩니다.
- LLM 처리는 Ollama로 실행되며, 유료 외부 API를 사용하지 않습니다.

## 10. 문제 해결

### 10-1. GitHub Action은 성공했는데 PC에 파일이 없습니다

GitHub Actions는 GitHub 서버에서 실행됩니다. `kidsnote-obsidian-export` artifact를
다운로드한 뒤 로컬 Obsidian vault에 복사해야 합니다.

### 10-2. 로컬 실행에서 `KIDSNOTE_SESSION_COOKIE missing`이 나옵니다

repository root에 `.env` 파일을 만들고 아래 값을 넣으세요.

```env
KIDSNOTE_SESSION_COOKIE=your_sessionid_value_here
```

### 10-3. 템플릿을 바꿨는데 기존 노트가 바뀌지 않습니다

기존 노트는 기본적으로 skip됩니다. 다시 생성하려면 `--force-refresh`를 사용하세요.

```powershell
.\tools\kidsnote_fetch\export-obsidian-local.ps1 -ForceRefresh
```

### 10-4. Summary가 없습니다

`Summary`는 Ollama가 생성합니다. 다음 경우에는 생략됩니다.

- Ollama를 사용할 수 없음
- 알림장 본문이 너무 짧음
- 이미 존재하는 노트라 skip됨

기존 노트의 Summary를 다시 만들고 싶다면 `-ForceRefresh`를 사용하세요.

## 11. License

MIT. 자세한 내용은 [LICENSE](LICENSE)를 확인하세요.
