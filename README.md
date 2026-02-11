# 지원공고알리미 MVP

## 실행
- `index.html` 더블클릭

## 데이터 갱신
- `../gov-support-hub/build_notices.py` 실행 후
- 생성된 `notices.json`을 이 폴더로 복사

## 핵심 기능
- 공고 우선순위 점수화
- 마감 임박 공고 우선 노출
- 오늘의 실행 플랜 자동 생성

## 배포 운영 규칙 (UI/데이터 분리)
앞으로 커밋을 2종류로 분리해서 관리:

- **UI 수정 배포** (HTML/CSS/JS)
  - `./scripts/deploy_ui.sh "feat: ui tweak"`
  - `notices.json/js`는 커밋에서 자동 제외

- **데이터 갱신 배포** (`notices.json/js`)
  - `./scripts/deploy_data.sh "chore: data refresh"`
  - `build_notices.py` 실행 후 데이터 파일만 커밋/푸시

GitHub Pages는 `main` 푸시 시 자동 반영됨.
