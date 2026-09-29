# 🌐 SiteReportX 원격 테스트 및 외부 접속 가이드

> **작성 일시**: 2026-08-25  
> **프로젝트**: SiteReportX (배관내시경 검사 보고서 자동화 웹 플랫폼)  
> **서버 주소**: `http://localhost:8000` (FastAPI + React 빌드 통합 구동)

---

## 1. 원격 테스트 방법 비교 요약

| 방식 | 추천 상황 | 외부 접속 링크 | 장점 |
| :--- | :--- | :--- | :--- |
| **1. Cloudflare Tunnel (가장 간편)** | 1회성/임시 원격 테스트 | `https://xxxx.trycloudflare.com` | **회원가입/로그인 불필요, 1초 만에 무료 HTTPS 생성** |
| **2. Ngrok** | 모바일/외부 안정적 테스트 | `https://xxxx.ngrok-free.app` | 안정적인 터널링, 대중적 |
| **3. 동일 Wi-Fi 로컬 IP 접속** | 사내망 / 같은 사무실 내 폰 테스트 | `http://192.168.X.X:8000` | 외부 툴 설치 불필요 (방화벽 허용 필요) |
| **4. Cloud Run / 클라우드 배포** | 24시간 상시 운영 및 팀 공유 | `https://sitereportx-xxxx.a.run.app` | 영구 도메인, 다수 작업자 실운영 |

---

## 2. 방법별 상세 실행 절차

### 방법 1: Cloudflare Tunnel (회원가입 없이 즉시 실행, 추천 ⭐⭐⭐)

1. **설치 (winget)**
   ```powershell
   winget install Cloudflare.cloudflared
   ```
2. **원격 터널 실행** (SiteReportX 서버가 켜진 상태에서 새 터널 터미널 실행)
   ```powershell
   cloudflared tunnel --url http://localhost:8000
   ```
3. 콘솔에 출력되는 **`https://xxxx.trycloudflare.com`** 링크를 복사하여 모바일이나 외부 PC 브라우저에서 바로 접속합니다.

---

### 방법 2: Ngrok (무료 HTTPS 터널링 ⭐⭐⭐)

1. **설치**
   ```powershell
   winget install ngrok
   ```
2. **토큰 등록 (최초 1회)**
   - [ngrok.com](https://ngrok.com) 가입 후 발급받은 authtoken 등록
   ```powershell
   ngrok config add-authtoken YOUR_AUTHTOKEN
   ```
3. **터널 실행**
   ```powershell
   ngrok http 8000
   ```
4. 생성된 **`https://xxxx.ngrok-free.app`** URL로 어디서나 원격 접속 가능

---

### 방법 3: 동일 Wi-Fi 환경 내 모바일/노트북 접속

현재 SiteReportX 서버는 `0.0.0.0:8000`으로 바인딩되어 있으므로, 같은 공유기(Wi-Fi)에 연결된 기기에서 바로 접속할 수 있습니다.

1. **현재 PC의 IP 주소 확인**
   - 명령 프롬프트(CMD) 또는 PowerShell에서 실행:
     ```powershell
     ipconfig
     ```
   - `IPv4 주소` 확인 (예: `192.168.0.25`)
2. **모바일 브라우저 접속**
   - `http://192.168.0.25:8000` 입력
   - *(접속이 안 될 경우 윈도우 방화벽에서 8000 포트 인바운드 허용 필요)*

---

## 3. 원격 환경에서 테스트할 핵심 시나리오

1. **모바일 현장 업로드 테스트**:
   - 스마트폰으로 촬영한 동영상/사진을 모바일 웹 브라우저에서 직접 업로드
2. **실시간 검수 에디터 테스트**:
   - 원격 PC/태블릿에서 명판 뷰어 및 드롭다운 검수 테이블 조작
3. **보고서 출력 및 다운로드**:
   - 원격 브라우저에서 원클릭으로 마스터 엑셀(`master_sample_0416.xlsx`) 및 표준 미디어 ZIP 파일 다운로드 확인
