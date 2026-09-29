import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from config import settings

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(settings.DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. 프로젝트 테이블
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        status TEXT DEFAULT 'draft',
        naming_template TEXT DEFAULT '{dong}동 {ho}호 {pipe_type} {pipe_name}_{defect}_{position}',
        field_settings TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. 검사 항목 테이블
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inspection_items (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        original_filename TEXT NOT NULL,
        original_file_path TEXT NOT NULL,
        frame_image_path TEXT,
        is_video INTEGER DEFAULT 1,
        dong TEXT DEFAULT '',
        ho TEXT DEFAULT '',
        pipe_type TEXT DEFAULT '',
        pipe_name TEXT DEFAULT '',
        defect TEXT DEFAULT '정상',
        position TEXT DEFAULT '입구',
        standard_filename TEXT DEFAULT '',
        status TEXT DEFAULT 'uploaded',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully.")
