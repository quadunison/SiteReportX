# ⚙️ SiteReportX 기술 스펙 정의서 (Technical Specification v1.1)

> **문서 버전**: v1.1 (실무 고도화)  
> **위치**: `SiteReportX/.doc/techspec.md`  
> **작성 일자**: 2026-08-15  
> **워크스페이스**: `d:\berodu\BaroEco\TaskieX\SiteReportX`

---

## 1. 시스템 아키텍처 개요

SiteReportX는 건설 현장 배관내시경 영상/사진의 명판을 AI로 자동 인식하여 파일명을 표준화하고 실무 규격 엑셀 보고서를 자동 작성하는 **FastAPI 백엔드 + Vite/React 프론트엔드** 웹 애플리케이션입니다.

```
[ Frontend (React SPA) ]
   ├── Vite + React 18 + Vanilla CSS (프리미엄 다크/라이트 테마)
   ├── 프로젝트 관리자 (새 현장 생성, 동/호/배관 프리셋 설정, 이어하기)
   ├── 일괄 파일 업로더 (드래그앤드롭, 스트리밍 청크 전송)
   ├── 실시간 분석 모니터 (SSE/폴링 기반 [12/50 분석 중 (24%)] 진행률 바)
   ├── 실시간 명판 검수 테이블 (현장 등록 드롭다운 선택, 500ms 디바운스 자동저장)
   └── 보고서 미리보기 & 원클릭 다운로더 (Excel, ZIP)
          │ (REST API & Server-Sent Events)
          ▼
[ Backend (FastAPI / Python) ]
   ├── REST API 컨트롤러 (Projects, Uploads, Inspections, Reports)
   ├── Video Processor (OpenCV / FFmpeg 기반 0~10초 명판 프레임 선명도 추출)
   ├── AI Vision Pipeline (TaskieX 호환: Google Vision, Gemini Flash, ChatGPT)
   ├── Dynamic Field Mapper (현장 프로젝트 설정 스키마 정규화)
   └── Excel Report Engine (OpenPyXL 기반 기존 마스터 엑셀 서식 100% 호환 사진 배치)
          │
          ▼
[ Data & Storage ]
   ├── SQLite (WAL 모드) : 프로젝트 메타데이터, 검수 항목 상태 보관
   ├── 로컬 스토리지 / NAS (업로드 미디어, 추출 프레임, 생성된 보고서 .xlsx, .zip)
   └── 기존 TaskieX API 키 폴더 연동 (`vision-api-key`, `gemini-api-key`, `chatgpt-api-key`)
```

---

## 2. 백엔드 기술 스펙 (Backend Specs)

### 2.1 기술 스택
- **Language / Runtime**: Python 3.12 (Windows / Linux)
- **Web Framework**: FastAPI (0.110+) & Uvicorn ASGI Server
- **Media Engine**: OpenCV (`opencv-python`), Pillow (PIL), FFmpeg
- **Report Engine**: `openpyxl` (서식 100% 보존 및 셀 좌표 기반 이미지 자동 리사이징 삽입)
- **AI Vision Engine**:
  - Google Cloud Vision API
  - Google Generative AI (Gemini 1.5/2.0 Flash)
  - OpenAI API (GPT-4o-mini)
  - TaskieX 룰베이스 폴백 정규화 모듈
- **Database / State**: SQLite (`sqlite3` / SQLAlchemy, WAL 모드 활성화)

### 2.2 대용량 미디어 스트리밍 및 메모리 보호
- 대용량 영상(수백 MB ~ 1GB+) 업로드 시 메모리 과부하를 원천 차단하기 위해 `shutil.copyfileobj` 기반 **청크 버퍼 디스크 스트리밍** 적용.
- 분석 완료 후 임시 썸네일/프레임 캐시 주기적 관리.

### 2.3 핵심 API 엔드포인트 명세
| 메소드 | 엔드포인트 | 설명 |
|:---|:---|:---|
| `GET` | `/api/projects` | 현장 프로젝트 전체 목록 조회 |
| `POST` | `/api/projects` | 새 현장 프로젝트 생성 (동, 호, 배관종류, 배관명 프리셋 등록) |
| `GET` | `/api/projects/{id}` | 특정 프로젝트 데이터 및 검수 항목 전체 로드 (열기/이어하기) |
| `PUT` | `/api/projects/{id}/settings` | 프로젝트 설정(동/호/배관 드롭다운 옵션) 수정 |
| `POST` | `/api/projects/{id}/upload` | 미디어 파일 다중 업로드 (영상/사진 스트리밍 저장) |
| `POST` | `/api/projects/{id}/analyze` | 비디오 0~10초 명판 프레임 추출 및 AI 비전 분석 백그라운드 작업 시작 |
| `GET` | `/api/projects/{id}/analyze-progress` | 실시간 분석 진행률 (SSE / Progress JSON) |
| `PATCH` | `/api/projects/{id}/items/{item_id}` | 검수 에디터에서 드롭다운 선택 데이터 실시간 자동저장 |
| `POST` | `/api/projects/{id}/generate-report` | 실무 엑셀 보고서 및 표준화 ZIP 파일 생성 |
| `GET` | `/api/projects/{id}/download/{type}` | 생성된 엑셀(.xlsx) 또는 압축팩(.zip) 다운로드 |
| `GET` | `/api/keys` | 감지된 Vision/Gemini/OpenAI 키 상태 확인 |

### 2.4 비디오 프레임 추출 알고리즘 (`video_engine.py`)
- **탐색 범위**: 영상 시작 0초부터 10.0초 구간
- **샘플링 레이트**: 초당 2~3개 프레임 추출
- **선명도 계산 (Blur Detection)**: `cv2.Laplacian(gray, cv2.CV_64F).var()` 연산으로 최고 점수 프레임 1장 자동 선정 및 JPEG 저장.

---

## 3. 프론트엔드 기술 스펙 (Frontend Specs)

### 3.1 기술 스택
- **Framework**: React 18+ (Vite 번들러)
- **Styling**: Vanilla CSS (CSS 변수 기반 프리미엄 다크/라이트 테마, 글래스모피즘, 고대비 현장 모드)
- **Icons**: Lucide React
- **HTTP Client**: Fetch API / Axios
- **State & AutoSave**:
  - React State + 500ms Debounced Auto-Save
  - 낙관적 업데이트(Optimistic Update)로 입력 딜레이 제로

### 3.2 핵심 UI 컴포넌트 구조
```
src/
├── App.jsx                     # 메인 상태 및 화면 라우팅 (대시보드 ↔ 작업 에디터)
├── index.css                   # 디자인 시스템 (색상, 타이포그래피, 테마 토큰)
├── components/
│    ├── Header.jsx             # 상단 네비게이션, 현장명, 프로젝트 상태 배지, API 키 모달
│    ├── ProjectDashboard.jsx   # 프로젝트 시작 화면 (새 현장 생성, 최근 현장 목록, 이어하기)
│    ├── ProjectSettings.jsx    # 현장별 동/호/배관종류/배관명 드롭다운 목록 관리 모달
│    ├── MediaUploader.jsx      # 드래그 앤 드롭 파일 일괄 업로더 및 실시간 진행률 바
│    ├── InspectionEditor.jsx   # [핵심] 좌측 명판 사진 줌 뷰어 ↔ 우측 드롭다운 검수 테이블
│    └── ReportExportModal.jsx  # 엑셀 보고서 및 표준화 압축팩 생성/다운로드 모달
```

### 3.3 검수 에디터 UX 정책 (데이터 무결성)
- 작업자는 **텍스트 임의 타이핑이 제한**되며, 현장 프로젝트에 등록된 **동, 호, 배관종류, 배관명, 이상소견 드롭다운 목록에서만 선택** 가능.
- 키보드 `[Tab]` 키로 다음 필드 이동, `[방향키]`로 옵션 선택, `[Enter]`로 다음 행 이동 지원.

---

## 4. 데이터베이스 및 스키마 구조 (SQLite Schema)

```sql
-- 현장 프로젝트 테이블
CREATE TABLE IF NOT EXISTS projects (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'draft', -- draft, reviewing, completed
    naming_template VARCHAR(200) DEFAULT '{dong}동 {ho}호 {pipe_type} {pipe_name}_{defect}_{position}',
    field_settings TEXT NOT NULL, -- JSON (동/호/배관종류/배관명 옵션 목록)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 검사 항목 (영상/사진) 테이블
CREATE TABLE IF NOT EXISTS inspection_items (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    original_file_path TEXT NOT NULL,
    frame_image_path TEXT,
    is_video BOOLEAN DEFAULT TRUE,
    
    -- AI 인식 및 검수된 데이터 (현장 설정 옵션만 허용)
    dong VARCHAR(50),
    ho VARCHAR(50),
    pipe_type VARCHAR(50),
    pipe_name VARCHAR(100),
    defect VARCHAR(50) DEFAULT '정상',
    position VARCHAR(50) DEFAULT '입구',
    standard_filename VARCHAR(255),
    
    status VARCHAR(20) DEFAULT 'uploaded', -- uploaded, analyzed, verified
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

---

## 5. 단일 실행 배포 모델 (Single Executable / Desktop Web)

- 백엔드(FastAPI)가 프론트엔드 정적 빌드 디렉토리(`frontend/dist`)를 `/` 루트로 통합 마운트하여 서빙.
- `python run_server.py` 또는 `start_sitereportx.bat` 단일 실행으로 브라우저가 자동 열림 (`http://localhost:8000`).
