# 🎨 SiteReportX UI/UX 모던화 및 산업용 디자인 개편 계획서

> **작성 일시**: 2026-09-30  
> **목적**: 기존 AI 데모 느낌의 과도한 초록색(#03C75A)을 탈피하고, Mobbin 레퍼런스 기반의 정제된 산업용(Industrial) 엔지니어링 B2B SaaS 디자인 시스템 구축  
> **핵심 키워드**: 산업용 신뢰감, 산뜻함, 정밀한 가독성, Mobbin 디자인 패턴, 세그먼티드 컨트롤  

---

## 1. 기존 UI 문제점 진단
1. **과도한 네온/네이버 초록색 남발**:
   - 로고, 버튼, 뱃지, 테이블 하이라이트, 업로드 드롭존까지 온통 `#03C75A`로 칠해져 "AI 프로토타입/데모 툴" 느낌이 강함.
2. **색상 파편화**:
   - 3개 모드 탭에 각각 파랑, 초록, 보라 등 원색이 무분별하게 적용되어 시각적 산만함 유발.
3. **타이포그래피 및 가독성 부족**:
   - 숫자(동, 호, 검사항목 수)에 고정폭(tabular-nums)이 없어 정렬이 어색함.
   - 자간(letter-spacing) 및 행간(line-height)이 정밀하지 못해 산업용 소프트웨어다운 단단함이 부족.
4. **컴포넌트 조형미 부재**:
   - 플랫하고 밋밋한 1px 보더와 거친 그림자 패턴.

---

## 2. 디자인 개편 전략 (Mobbin B2B SaaS 표준)

### 🎨 컬러 팔레트 (Industrial Modern Navy & Slate)
- **Primary**: 정밀하고 신뢰감을 주는 `Electric Indigo / Deep Cobalt` (`#2563EB`, Hover: `#1D4ED8`, Light: `#EFF6FF`)
- **Neutral (Surface & Border)**:
  - Background Main: `#F8FAFC` (산뜻하고 피로도 낮은 쿨 오프화이트)
  - Card & Surface: `#FFFFFF`
  - Border Subtle: `#E2E8F0` (모던 1px 정밀 보더)
  - Border Strong: `#CBD5E1`
  - Text Primary: `#0F172A` (고대비 슬레이트)
  - Text Secondary: `#475569`
  - Text Muted: `#64748B`
- **Semantic Colors (절제된 톤)**:
  - Success (정상/완료): 세이지 에메랄드 (`#059669`, Soft BG: `#ECFDF5`)
  - Warning/Defect (이상/결함): 웜 앰버 (`#D97706`, Soft BG: `#FFFBEB`, Border: `#FDE68A`)
  - Danger (오류): 로즈 크림슨 (`#E11D48`, Soft BG: `#FFF1F2`)

### 🔤 타이포그래피 & 수치 가독성
- **Font Stack**: Pretendard, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto
- **Font Smoothing**: `-webkit-font-smoothing: antialiased`
- **Tabular Figures**: 통계 숫자, 검사항목, 동/호수 등에 `font-variant-numeric: tabular-nums` 적용
- **Tighter Tracking**: 헤딩 및 뱃지 자간 `-0.02em`으로 단단하고 세련된 인상 형성

### 🧩 핵심 컴포넌트 리파인
1. **Header**: 정갈한 미니멀 인더스트리얼 엠블럼 + 글래스모피즘 보더
2. **Segmented Mode Switcher**: iOS/macOS/Mobbin 스타일의 세련된 일체형 탭
3. **Project Dashboard Cards**: KPI 뱃지, 호버 시 미세한 엘리베이션 및 인디고 테두리
4. **Inspection Table**: 엑셀 엔지니어링 시인성을 극대화한 클린 그리드, 결함 행의 따뜻한 앰버 하이라이트
5. **Upload Dropzone**: 점선 드래그존의 세련된 라운디드 카드화

---

## 3. 작업 파일 범위
- `frontend/src/index.css`: 전역 테마 변수, 유틸리티, 타이포그래피, 버튼, 테이블, 모달 스타일 전면 개편
- `frontend/src/components/Header.jsx`: 로고 및 헤더 액션 디자인 고도화
- `frontend/src/components/InspectionWorkspace.jsx`: 3대 모드 세그먼티드 컨트롤 및 상단 바 리파인
- `frontend/src/components/ProjectDashboard.jsx`: 프로젝트 카드 및 빈 상태 뷰 모던화
- `frontend/src/components/ReportPreview.jsx`: 엑셀 웹 미리보기 컴포넌트 톤앤매너 정렬
