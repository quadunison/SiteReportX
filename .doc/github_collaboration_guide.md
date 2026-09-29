# 🌐 GitHub 협업 및 저장소 구축 보고서

> **작성 일시**: 2026-09-30  
> **프로젝트**: SiteReportX (건설 현장 배관내시경 검사 보고서 자동화 웹 플랫폼)  
> **저장소**: [https://github.com/quadunison/SiteReportX.git](https://github.com/quadunison/SiteReportX.git)  
> **협업 팀 구성**: 개발자 1인, 디자이너 1인, 총괄 PM  

---

## 1. 개요 및 목적
SiteReportX 프로젝트의 신속한 기능 고도화와 UI/UX 개선을 위해 외부 개발자 및 디자이너와 협업을 개시합니다.
본 문서는 보안(API 키 및 현장 미디어 유출 방지), 온보딩 편의성, 브랜치 전략을 체계화하여 두 직군이 혼선 없이 프로젝트에 기여할 수 있도록 지원합니다.

---

## 2. 저장소 보안 및 파일 관리 (.gitignore)
- **현장 데이터 보호**: `uploads/`, `outputs/`에 저장되는 현장 배관 영상, 사진, 생성된 엑셀 보고서는 `.gitignore` 처리되어 깃헙에 업로드되지 않음.
- **데이터베이스 격리**: `data/*.db` (SQLite 로컬 DB)는 각 작업자의 로컬 환경에서 독립 생성되도록 제외.
- **보안 자격증명 차단**: `.env`, `*.key`, `vision-api-key/*.json` 차단. 개발자는 `.env.example`을 복사하여 개별 API 키를 설정함.
- **마스터 서식 보존**: `backend/templates/master_sample_0416.xlsx`는 보고서 출력의 핵심 엔진 서식이므로 Git 추적 대상에 포함.

---

## 3. 직군별 온보딩 프로세스

### 🎨 디자이너 온보딩
1. 저장소 Clone 후 `start_sitereportx.bat` 실행만으로 즉시 로컬 브라우저에서 화면 확인.
2. `frontend/src/components/` 내 컴포넌트 구조 파악.
3. Tailwind CSS 클래스 및 Pretendard 글꼴 스타일 수정 후 화면 실시간 피드백 확인.
4. 주요 과제:
   - 미디어 업로드 프로그레스 바 인터랙션 개선
   - AI 명판 검수 에디터 테이블 반응형 디자인
   - 마스터 엑셀 웹 미리보기 컴포넌트의 시각적 가독성 제고

### 💻 개발자 온보딩
1. 저장소 Clone 후 `pip install -r backend/requirements.txt` 및 `cd frontend && npm install`.
2. `.env.example`을 참고하여 `.env`에 Gemini API Key 입력.
3. `python run_server.py` 또는 `uvicorn main:app --reload`로 디버깅 환경 구동.
4. 주요 과제:
   - 비전 AI 프롬프트 지능형 스냅 성능 튜닝
   - 엑셀 엔진(`backend/services/excel_engine.py`) 생성 속도 최적화
   - 대용량 파일 청크 업로드 안정성 확보

---

## 4. Git 협업 규칙
- `main` 브랜치는 항상 프로덕션 빌드가 완료된 정상 동작 상태를 유지.
- 기능별 작업 브랜치(`feat/`, `fix/`, `design/`) 생성 후 Pull Request(PR)를 통한 코드 리뷰 및 병합 권장.
