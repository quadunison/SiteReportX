import os
from pathlib import Path
from typing import Dict, Optional

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
TASKIEX_DIR = ROOT_DIR.parent
DATA_DIR = ROOT_DIR / "data"
UPLOAD_DIR = ROOT_DIR / "uploads"
OUTPUT_DIR = ROOT_DIR / "outputs"
TEMPLATE_DIR = BASE_DIR / "templates"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

class Settings:
    PROJECT_NAME: str = "SiteReportX"
    VERSION: str = "1.1.0"
    DB_PATH: Path = DATA_DIR / "sitereportx.db"
    
    @staticmethod
    def get_api_keys() -> Dict[str, Optional[str]]:
        """환경변수 및 상위 TaskieX API 키 폴더에서 키 자동 감지"""
        keys = {
            "gemini": os.getenv("GEMINI_API_KEY"),
            "openai": os.getenv("OPENAI_API_KEY"),
            "google_vision": os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        }
        
        # 1. Gemini API 키
        gemini_file = TASKIEX_DIR / "gemini-api-key" / "gemini-api-key.txt"
        if not keys["gemini"] and gemini_file.exists():
            try:
                with open(gemini_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        keys["gemini"] = content
            except Exception:
                pass

        # 2. OpenAI API 키
        openai_file = TASKIEX_DIR / "chatgpt-api-key" / "chatgpt_api_key.txt"
        if not keys["openai"] and openai_file.exists():
            try:
                with open(openai_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        keys["openai"] = content
            except Exception:
                pass

        # 3. Google Cloud Vision API 키 (JSON)
        vision_dir = TASKIEX_DIR / "vision-api-key"
        if not keys["google_vision"] and vision_dir.exists():
            json_files = list(vision_dir.glob("*.json"))
            if json_files:
                keys["google_vision"] = str(json_files[0])

        return keys

settings = Settings()
