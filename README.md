# 🏗️ SiteReportX (건설 현장 배관 검사 보고서 자동화 웹 플랫폼)

> **SiteReportX**는 건설 현장의 배관 내시경 검사 영상 및 사진을 AI(Vision AI)로 자동 분석하여, 현장 표준 **마스터 엑셀 서식(.xlsx)**으로 자동 생성·출력해 주는 차세대 스마트 리포트 플랫폼입니다.

---

## 📌 목차
1. [프로젝트 소개](#-프로젝트-소개)
2. [핵심 워크플로우 & 3대 작업 모드](#-핵심-워크플로우--3대-작업-모드)
3. [🎨 디자이너 협업 가이드](#-디자이너-협업-가이드)
4. [💻 개발자 시작 가이드](#-개발자-시작-가이드)
5. [📁 프로젝트 아키텍처](#-프로젝트-아키텍처)
6. [🤝 협업 및 Git 워크플로우](#-협업-및-git-워크플로우)
7. [📚 상세 기술 문서](#-상세-기술-문서)

---

## 💡 프로젝트 소개

건설 현장에서 수백 편씩 쏟아지는 배관 내시경 동영상과 결함 사진을 일일이 수기로 엑셀에 붙여 넣던 비효율을 해결합니다.
- **영상/사진 자동 타임스탬프 페어링**: 동영상 녹화 시간대와 사진 촬영 시간을 매칭하여 결함 사진을 비디오에 자동 귀속
- **AI 명판 자동 인식 & 지능형 스냅**: 동영상 앞부분 명판(동, 호, 배관종류, 배관명)을 AI가 인식하고 현장 표준 규격으로 자동 보정
- **실무 엑셀 마스터 서식 1:1 완벽 매핑**: 셀 크기(199x158px)에 맞춰 결함 사진을 무여백 가득 채우고, 하이라이트 및 수식 일괄 적용

---

## 🖥️ 핵심 워크플로우 & 3대 작업 모드

화면 상단의 3대 탭을 통해 누구나 직관적으로 작업할 수 있습니다:

```
[ 동영상 / 사진 일괄 업로드 ]
            ↓
┌─────────────────────────────────────────────────────────────┐
│ 1️⃣ AI 명판 검수 에디터   : 돋보기 확대경 ↔ 실시간 자동저장 테이블 │
│ 2️⃣ 마스터 엑셀 웹 미리보기 : 실제 서식과 100% 동일한 웹 뷰어       │
│ 3️⃣ 실시간 작업 로그      : 백엔드 처리 과정 터미널 스트리밍        │
└─────────────────────────────────────────────────────────────┘
            ↓
[ 원클릭 최종 엑셀 보고서 다운로드 (.xlsx) ]
```

---

## 🎨 디자이너 협업 가이드

디자이너 분들이 UI/UX를 파악하고 스타일링을 개선할 때 참고할 핵심 정보입니다.

### 1. 화면 컴포넌트 위치 (`frontend/src/components/`)
- `ProjectDashboard.jsx`: 현장 프로젝트 목록 및 신규 현장 생성 모달
- `InspectionWorkspace.jsx`: 3대 모드 탭이 통합된 핵심 작업 공간
- `ReportPreview.jsx`: 실제 엑셀 시트와 동일한 레이아웃을 렌더링하는 실시간 웹 뷰어
- `ProcessLogViewer.jsx`: 실시간 분석 터미널 로그 뷰어
- `TemplateUploadModal.jsx`: 현장별 엑셀 마스터 서식 업로드 모달
- `ProjectSettingsModal.jsx`: 현장별 동/호/배관명 커스텀 관리 모달

### 2. 디자인 시스템 및 스타일 가이드
- **CSS Framework**: Tailwind CSS 기반 유틸리티 스타일링
- **타이포그래피**: 고해상도 가독성을 위한 Pretendard / Inter 글꼴 권장
- **아이콘 시스템**: `lucide-react` 아이콘 세트 적용
- **메인 테마**: 신뢰감을 주는 딥 네이비(Deep Navy) & 인더스트리얼 슬레이트(Slate) 악센트

### 3. 고도화 집중 UX 과제
- [ ] **대용량 미디어 업로드 UX 개선**: 대용량 동영상/사진 드래그앤드롭 시 프로그레스 피드백 강화
- [ ] **명판 검수 테이블 편의성**: 키보드 단축키(Tab, Enter) 및 인라인 편집 사용성 극대화
- [ ] **태블릿/모바일 반응형 대응**: 현장 사무소 및 태블릿 기기에서의 뷰어 사용성 최적화
- [ ] **Figma 링크**: *(디자인 완료 시 피그마 공유 링크 삽입 예정)*

---

## 💻 개발자 시작 가이드

### 1. 기술 스택
- **Backend**: Python 3.10+, FastAPI, SQLite (WAL 모드), OpenCV, OpenPyXL, Gemini Vision AI
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide React
- **Packaging/Serving**: FastAPI 정적 파일 서빙(`frontend/dist`) + 원클릭 구동 스크립트

### 2. 가장 빠른 로컬 실행 (Windows 원클릭)
```bash
# 루트 디렉토리에서 배치 파일 더블클릭 또는 터미널 실행
start_sitereportx.bat
```
> 브라우저가 자동으로 열리며 `http://localhost:8000`에 접속됩니다.

### 3. 개발 모드 개별 실행

#### 백엔드 (FastAPI)
```bash
cd backend
pip install -r requirements.txt

# 환경변수 설정 (.env.example 복사하여 .env 생성)
copy ..\.env.example ..\.env

# 서버 실행 (포트 8000)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 프론트엔드 (Vite Hot-Reload)
```bash
cd frontend
npm install
npm run dev
# 접속: http://localhost:5173 (프록시로 백엔드 8000 포트 연결)
```

#### 배포용 프론트엔드 빌드
```bash
cd frontend
npm run build
# 빌드 결과물이 frontend/dist에 생성되어 FastAPI에서 일괄 서빙됩니다.
```

---

## 📁 프로젝트 아키텍처

```
SiteReportX/
├── backend/
│   ├── config.py             # 전역 경로 및 환경변수(API 키) 로드
│   ├── main.py               # FastAPI 엔드포인트 및 정적 서빙
│   ├── requirements.txt      # 백엔드 필수 패키지 목록
│   ├── core/
│   │   ├── database.py       # SQLite 커넥션 풀 & WAL 모드 초기화
│   │   └── project_manager.py# 프로젝트/검사 항목 CRUD 비즈니스 로직
│   ├── services/
│   │   ├── video_engine.py   # 비디오 명판 추출 & 타임스탬프 페어링
│   │   ├── vision_engine.py  # Gemini 비전 AI 분석 및 지능형 스냅 매핑
│   │   └── excel_engine.py   # 마스터 엑셀 서식 복제 및 정밀 셀 주입
│   └── templates/
│       └── master_sample_0416.xlsx # 실무 마스터 엑셀 원본 서식
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # 메인 라우팅 & 전역 상태
│   │   └── components/       # 핵심 UI 컴포넌트 셋
│   ├── package.json
│   └── vite.config.js
├── .doc/                     # 상세 기획, 설계, 인수인계 문서
├── .env.example              # 환경 변수 설정 템플릿
├── .gitignore                # Git 제외 파일 규칙
├── run_server.py             # 파이썬 원클릭 구동기
└── start_sitereportx.bat      # 윈도우 원클릭 배치 파일
```

---

## 🤝 협업 및 Git 워크플로우

1. **브랜치 전략**:
   - `main`: 상시 배포 가능한 안정 버전
   - `feat/기능명`: 신규 기능 개발 브랜치 (예: `feat/designer-ui-update`, `feat/excel-export-speedup`)
   - `fix/버그명`: 버그 수정 브랜치
2. **커밋 메시지 규칙**:
   - `feat:` 새로운 기능 추가
   - `fix:` 버그 수정
   - `style:` 코드 포맷팅, UI 스타일 변경 (디자인 반영)
   - `docs:` 문서 수정 및 추가
   - `refactor:` 코드 리팩토링

---

## 📚 상세 기술 문서

프로젝트의 심층적인 설계와 실무 배경은 [.doc](file:///.doc) 디렉토리에서 확인하실 수 있습니다:
- [현장 검사 & SOP 워크플로우 명세서 (.doc/field_inspection_workflow.md)](file:///.doc/field_inspection_workflow.md)
- [시스템 기술 스펙 (.doc/techspec.md)](file:///.doc/techspec.md)
- [핸드오버 및 개발 히스토리 (.doc/handover.md)](file:///.doc/handover.md)
- [원격 테스트 및 터널링 가이드 (.doc/remote_testing_guide.md)](file:///.doc/remote_testing_guide.md)

---
© 2026 SiteReportX Team. All rights reserved.
