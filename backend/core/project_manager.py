import uuid
import json
import sqlite3
from typing import Dict, Any, List, Optional
from core.database import get_db_connection

DEFAULT_FIELD_SETTINGS = {
    "dong_options": ["101", "102", "103", "104", "105", "106", "107", "108", "109", "110", "A동", "B동", "상가동"],
    "ho_options": ["101", "102", "201", "202", "203", "204", "205", "301", "302", "303", "304", "305", "지하1층", "피트실", "옥상"],
    "pipe_types": [
        "세대매립관", "입상관", "세대PD", "세대층상배관", 
        "오수관", "배수관", "통기관", "우수관", "급수관", "소방배관"
    ],
    "pipe_names": [
        "앞발코니배수", "주방오수", "세탁배수", "안방욕실배수", 
        "공용욕실배수", "싱크배수", "에어컨드레인", "PIT배관", "횡주관", "입상관"
    ],
    "defect_options": [
        "정상", "물고임", "구배불량", "토사/이물질", 
        "파손/크랙", "조인트이탈", "백화", "단차발생"
    ],
    "position_options": [
        "입구", "0.5m", "1.0m", "1.5m", "2.0m", "2.5m", "3.0m", "엘보구간", "출구"
    ]
}

class ProjectManager:
    @staticmethod
    def create_project(name: str, field_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        project_id = str(uuid.uuid4())[:8]
        settings_json = json.dumps(field_settings or DEFAULT_FIELD_SETTINGS, ensure_ascii=False)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO projects (id, name, field_settings) VALUES (?, ?, ?)",
            (project_id, name, settings_json)
        )
        conn.commit()
        conn.close()
        return ProjectManager.get_project(project_id)

    @staticmethod
    def list_projects() -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, 
                   COUNT(i.id) as total_items,
                   SUM(CASE WHEN i.defect != '정상' AND i.defect != '' THEN 1 ELSE 0 END) as defect_count
            FROM projects p
            LEFT JOIN inspection_items i ON p.id = i.project_id
            GROUP BY p.id
            ORDER BY p.created_at DESC
        """)
        rows = cursor.fetchall()
        projects = []
        for r in rows:
            projects.append({
                "id": r["id"],
                "name": r["name"],
                "status": r["status"],
                "naming_template": r["naming_template"],
                "field_settings": json.loads(r["field_settings"]),
                "total_items": r["total_items"] or 0,
                "defect_count": r["defect_count"] or 0,
                "created_at": r["created_at"],
                "updated_at": r["updated_at"]
            })
        conn.close()
        return projects

    @staticmethod
    def get_project(project_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        p_row = cursor.fetchone()
        if not p_row:
            conn.close()
            return None

        cursor.execute("SELECT * FROM inspection_items WHERE project_id = ? ORDER BY created_at ASC", (project_id,))
        item_rows = cursor.fetchall()
        
        items = []
        for ir in item_rows:
            items.append({
                "id": ir["id"],
                "project_id": ir["project_id"],
                "original_filename": ir["original_filename"],
                "original_file_path": ir["original_file_path"],
                "frame_image_path": ir["frame_image_path"],
                "is_video": bool(ir["is_video"]),
                "dong": ir["dong"],
                "ho": ir["ho"],
                "pipe_type": ir["pipe_type"],
                "pipe_name": ir["pipe_name"],
                "defect": ir["defect"],
                "position": ir["position"],
                "standard_filename": ir["standard_filename"],
                "status": ir["status"],
                "created_at": ir["created_at"]
            })

        project_data = {
            "id": p_row["id"],
            "name": p_row["name"],
            "status": p_row["status"],
            "naming_template": p_row["naming_template"],
            "field_settings": json.loads(p_row["field_settings"]),
            "created_at": p_row["created_at"],
            "updated_at": p_row["updated_at"],
            "items": items
        }
        conn.close()
        return project_data

    @staticmethod
    def update_project_settings(project_id: str, field_settings: Dict[str, Any]) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        settings_json = json.dumps(field_settings, ensure_ascii=False)
        cursor.execute(
            "UPDATE projects SET field_settings = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (settings_json, project_id)
        )
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def add_inspection_item(project_id: str, item_data: Dict[str, Any]) -> str:
        item_id = item_data.get("id") or str(uuid.uuid4())[:8]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO inspection_items (
                id, project_id, original_filename, original_file_path, frame_image_path,
                is_video, dong, ho, pipe_type, pipe_name, defect, position, standard_filename, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id,
            project_id,
            item_data["original_filename"],
            item_data["original_file_path"],
            item_data.get("frame_image_path"),
            1 if item_data.get("is_video", True) else 0,
            item_data.get("dong", ""),
            item_data.get("ho", ""),
            item_data.get("pipe_type", ""),
            item_data.get("pipe_name", ""),
            item_data.get("defect", "정상"),
            item_data.get("position", "입구"),
            item_data.get("standard_filename", ""),
            item_data.get("status", "uploaded")
        ))
        conn.commit()
        conn.close()
        return item_id

    @staticmethod
    def update_inspection_item(project_id: str, item_id: str, updates: Dict[str, Any]) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 허용된 컬럼만 업데이트
        allowed_keys = ["dong", "ho", "pipe_type", "pipe_name", "defect", "position", "standard_filename", "frame_image_path", "status"]
        set_clauses = []
        values = []
        for k, v in updates.items():
            if k in allowed_keys:
                set_clauses.append(f"{k} = ?")
                values.append(v)

        if not set_clauses:
            conn.close()
            return False

        values.extend([item_id, project_id])
        query = f"UPDATE inspection_items SET {', '.join(set_clauses)} WHERE id = ? AND project_id = ?"
        cursor.execute(query, tuple(values))
        
        # 프로젝트 updated_at 갱신
        cursor.execute("UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (project_id,))
        conn.commit()
        conn.close()
        return True
