# 키즈노트 마크다운 백업

> 이 프로젝트는 [redchupa/kidsnote-backup](https://github.com/redchupa/kidsnote-backup)을
> fork한 뒤, Notion 백업 대신 Obsidian Markdown 백업 용도로 수정한 버전입니다.

키즈노트 데이터를 Obsidian에서 관리하기 좋은 Markdown 파일로 내려받는 도구입니다.

키즈노트의 알림장, 공지사항, 사진, 동영상, 첨부파일을 다운로드해서 로컬 Markdown 노트와
assets 폴더로 저장합니다. 두 자녀 계정을 기준으로 만들었지만, 아이 이름을 기준으로 폴더를
나누기 때문에 한 명 또는 세 명 이상이어도 동작합니다.

## 생성되는 결과

기본 로컬 저장 경로는 다음과 같습니다.

```text
D:\Obisian\Obsidian_Vault\KidsNote Backup\
```

생성되는 폴더 구조는 다음과 같습니다.

```text
KidsNote Backup/
├── 하랑/
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
└── 태하/
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
child: "하랑"
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

## 주요 기능

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

## LLM으로 생성되는 내용

Ollama가 사용 가능하면 다음 내용이 추가됩니다.

- 각 알림장의 `## Summary`
- `_index/monthly-growth-stories.md`
- `_index/milestones.md`

GitHub Actions에서는 workflow 안에서 Ollama와 `llama3.1:8b` 모델을 실행합니다.
로컬에서 실행할 때도 `OLLAMA_HOST`가 설정되어 있으면 같은 방식으로 사용할 수 있습니다.
외부 유료 LLM API key는 필요하지 않습니다.

Ollama를 사용할 수 없는 경우에도 알림장, 공지사항, 사진, 첨부파일은 정상적으로 저장됩니다.
LLM 섹션만 생략됩니다.

## 필요한 Secret

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

## GitHub Actions로 첫 대량 백업하기

처음 전체 데이터를 받을 때는 오래 걸릴 수 있습니다. 과거 알림장, 사진, 공지사항, 첨부파일을
모두 받고 Ollama 모델도 내려받기 때문입니다. 이 첫 백업은 GitHub Actions에서 실행하면
PC를 꺼두어도 계속 진행됩니다.

1. GitHub repository를 엽니다.
2. `Settings -> Secrets and variables -> Actions`로 이동합니다.
3. `KIDSNOTE_SESSION_COOKIE`를 등록합니다.
4. `Actions` 탭으로 이동합니다.
5. `Kidsnote -> Obsidian Markdown` workflow를 선택합니다.
6. `Run workflow`를 클릭합니다.

작게 테스트할 때는 아래처럼 실행하는 것을 추천합니다.

```text
limit: 5
monthly_sample: false
force_refresh: true
```

workflow가 완료되면 artifact가 생성됩니다.

```text
kidsnote-obsidian-export
```

artifact를 다운로드하고 압축을 푼 뒤, 아이별 폴더를 아래 경로에 복사합니다.

```text
D:\Obisian\Obsidian_Vault\KidsNote Backup\
```

최종 구조는 이렇게 되어야 합니다.

```text
KidsNote Backup/
├── 하랑/
└── 태하/
```

아래처럼 한 단계 더 깊게 들어가면 안 됩니다.

```text
KidsNote Backup/
└── obsidian-export/
    ├── 하랑/
    └── 태하/
```

## 로컬 증분 백업

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

## Python으로 직접 실행하기

GitHub Actions와 PowerShell helper는 내부적으로 모두 `fetch.py`를 호출합니다.

동일한 로컬 명령은 다음과 같습니다.

```powershell
python tools\kidsnote_fetch\fetch.py `
  --auth-mode session-cookie-env `
  --export-markdown `
  --all-children `
  --no-local-save `
  --backup-root "D:\Obisian\Obsidian_Vault\KidsNote Backup"
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

## 중복 방지 방식

exporter는 기존 Markdown 파일의 frontmatter를 읽습니다.

```yaml
report_id: 1392587707
notice_id: 123456
```

같은 ID가 이미 있으면 해당 항목은 건너뜁니다.

`--force-refresh`를 사용하면 기존 노트를 다시 생성합니다. 파일명이나 레이아웃을 바꾼 뒤
기존 노트를 정리할 때 유용합니다. 예전 파일명에 숫자 ID가 포함되어 있던 중복 노트도
새 파일명으로 다시 쓰면서 정리됩니다.

## 개인정보와 보안

- 키즈노트 session cookie는 비밀 값입니다. GitHub Secrets 또는 `.env`에만 저장하세요.
- `.env`는 commit하지 마세요.
- JPEG 사진의 GPS EXIF 정보는 저장 전에 제거됩니다.
- LLM 처리는 Ollama로 실행되며, 유료 외부 API를 사용하지 않습니다.

## 문제 해결

### GitHub Action은 성공했는데 PC에 파일이 없습니다

GitHub Actions는 GitHub 서버에서 실행됩니다. `kidsnote-obsidian-export` artifact를
다운로드한 뒤 로컬 Obsidian vault에 복사해야 합니다.

### 로컬 실행에서 `KIDSNOTE_SESSION_COOKIE missing`이 나옵니다

repository root에 `.env` 파일을 만들고 아래 값을 넣으세요.

```env
KIDSNOTE_SESSION_COOKIE=your_sessionid_value_here
```

### 템플릿을 바꿨는데 기존 노트가 바뀌지 않습니다

기존 노트는 기본적으로 skip됩니다. 다시 생성하려면 `--force-refresh`를 사용하세요.

```powershell
.\tools\kidsnote_fetch\export-obsidian-local.ps1 -ForceRefresh
```

### Summary가 없습니다

`Summary`는 Ollama가 생성합니다. 다음 경우에는 생략됩니다.

- Ollama를 사용할 수 없음
- 알림장 본문이 너무 짧음
- 이미 존재하는 노트라 skip됨

기존 노트의 Summary를 다시 만들고 싶다면 `-ForceRefresh`를 사용하세요.

## License

MIT. 자세한 내용은 [LICENSE](LICENSE)를 확인하세요.
