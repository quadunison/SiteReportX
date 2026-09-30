import os
import sys
import webbrowser
import threading
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import uvicorn

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    print("=" * 60)
    print(" [SiteReportX] 건설 현장 배관 검사 보고서 자동화 웹앱")
    print("=" * 60)
    print(" 서버 주소: http://localhost:8000")
    print(" 브라우저가 자동으로 실행됩니다. (종료하려면 Ctrl+C를 누르세요)")
    print("=" * 60)
    
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("main:app", app_dir=str(BACKEND_DIR), host="0.0.0.0", port=8000, reload=False)
