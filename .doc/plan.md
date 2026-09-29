# 📋 SiteReportX 개발 과정 관리 마스터 플랜 (Master Plan)

> **문서 버전**: v1.1 (스프린트 1~3 완료)  
> **위치**: `SiteReportX/.doc/plan.md`  
> **관리 주기**: 스프린트 단위 실시간 업데이트

---

## 1. 스프린트 개요 및 마일스톤

```
[ Sprint 1: 백엔드 코어 & 파이프라인 (완료 ✓) ] ➔ [ Sprint 2: 엑셀 보고서 엔진 & 프로젝트 DB (완료 ✓) ] 
       ➔ [ Sprint 3: 프론트엔드 UI & 검수 에디터 (완료 ✓) ] ➔ [ Sprint 4: 통합 연동 & 실무 데이터 검증 (진행 중 🚀) ]
```

---

## 2. 스프린트별 상세 태스크 체크리스트

### 🚀 Sprint 1: 백엔드 아키텍처 & 비전 파이프라인 (완료 ✓)
- [x] **1.1 프로젝트 디렉토리 및 의존성 구성**
  - [x] `SiteReportX/backend` 기본 패키지 구성
  - [x] TaskieX 기존 API 키 자동 감지 모듈 (`config.py`)
- [x] **1.2 비디오 스마트 명판 추출 엔진 (`services/video_engine.py`)**
  - [x] 0~10초 영상 초반 Laplacian 선명도 분석 알고리즘
  - [x] 최적 소판 프레임 고화질 JPEG 저장
- [x] **1.3 TaskieX 호환 AI 비전 파이프라인 (`services/vision_engine.py`)**
  - [x] Google Cloud Vision API 연동
  - [x] Google Gemini 1.5/2.0 Flash 및 OpenAI GPT-4o-mini 연동
  - [x] 현장 동적 필드(동/호/배관) 스키마 주입 및 정규화
- [x] **1.4 백엔드 단위 테스트**
  - [x] SQLite WAL DB 초기화 및 프로젝트 생성 테스트 통과

---

### 📊 Sprint 2: 프로젝트 DB & 엑셀 보고서 엔진 (완료 ✓)
- [x] **2.1 프로젝트 라이프사이클 관리자 (`core/project_manager.py`)**
  - [x] SQLite 기반 프로젝트 생성, 목록 조회, 설정 변경, 이어하기 API
  - [x] 현장별 동/호/배관종류/배관명 드롭다운 프리셋 CRUD
- [x] **2.2 실무 엑셀 보고서 자동 작성 엔진 (`services/excel_engine.py`)**
  - [x] 기존 `master_sample_0416.xlsx` 서식 기반 100% 호환 레이아웃
  - [x] 종횡비 유지 사진 자동 축소 및 정밀 셀 배치
  - [x] 이상소견 셀 조건부 서식(노란색 강조) 자동 적용
- [x] **2.3 파일명 표준화 및 ZIP 패키징 모듈 (`services/excel_engine.py`)**
  - [x] `{dong}동 {ho}호 {pipe_type} {pipe_name}_{defect}_{position}` 명명규칙 적용
  - [x] 표준 파일명 미디어 + 완성된 엑셀 보고서 통합 압축

---

### 🎨 Sprint 3: 프론트엔드 UI/UX 구축 (React + Vite) (완료 ✓)
- [x] **3.1 프론트엔드 기반 셋업 및 디자인 시스템**
  - [x] Vite + React 프로젝트 구성 및 테마 CSS (`index.css`)
  - [x] 상단 헤더, 현장 배지, API 키 설정 모달 (`Header.jsx`, `ApiKeyModal.jsx`)
- [x] **3.2 프로젝트 시작 대시보드 (`ProjectDashboard.jsx`)**
  - [x] 새 현장 프로젝트 생성 모달 (현장명 입력)
  - [x] 최근 작업 현장 카드 목록 및 '이어하기' 클릭 시 세션 복원
- [x] **3.3 현장별 필드 설정 관리 모달 (`ProjectSettingsModal.jsx`)**
  - [x] 동, 호, 배관종류, 배관명, 이상소견 드롭다운 목록 자유 편집/저장
- [x] **3.4 [핵심] 실시간 명판 검수 에디터 (`InspectionWorkspace.jsx`)**
  - [x] 좌측: 캡처된 명판 사진 줌/돋보기 뷰어 (마우스 오버 확대)
  - [x] 우측: 현장 등록 옵션 드롭다운 선택 테이블 (타이핑 제한으로 오타 방지)
  - [x] 500ms 디바운스 실시간 자동저장 (`/api/projects/{id}/items/{item_id}`)
  - [x] 이상소견 시 노란색 하이라이트
- [x] **3.5 보고서 다운로드 뷰어 (`ReportModal.jsx`)**
  - [x] 원클릭 엑셀(.xlsx) 및 ZIP 다운로드
- [x] **3.6 프로덕션 번들 빌드 (`frontend/dist`) 및 통합 서빙 연결**

---

### 🔍 Sprint 4: 통합 연동, 실무 데이터 검증 & 구동 스크립트 (진행 중 🚀)
- [x] **4.1 단일 구동 스크립트 작성**
  - [x] `run_server.py` 및 `start_sitereportx.bat` 작성
- [ ] **4.2 실제 현장 배관 샘플 영상 기반 E2E 종합 테스트**
- [ ] **4.3 최종 사용자 가이드 작성**
