import os
import uuid
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from config import settings, UPLOAD_DIR, OUTPUT_DIR, ROOT_DIR
from core.database import init_database
from core.project_manager import ProjectManager
from services.video_engine import VideoEngine
from services.vision_engine import VisionEngine
from services.excel_engine import ExcelReportEngine

# DB 초기화
init_database()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="건설 현장 배관내시경 증빙 보고서 자동화 웹 플랫폼"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 분석 진행률 및 실시간 로그 인메모리 관리
analysis_progress: Dict[str, Dict[str, Any]] = {}
project_logs: Dict[str, List[Dict[str, Any]]] = {}
custom_api_keys: Dict[str, str] = {}

def add_project_log(project_id: str, message: str, level: str = "info"):
    """프로젝트별 실시간 작업 로그 기록 (최대 300줄)"""
    if project_id not in project_logs:
        project_logs[project_id] = []
    
    from datetime import datetime
    now_str = datetime.now().strftime("%H:%M:%S")
    entry = {
        "time": now_str,
        "message": message,
        "level": level  # 'info', 'success', 'warning', 'error', 'header'
    }
    project_logs[project_id].append(entry)
    if len(project_logs[project_id]) > 300:
        project_logs[project_id] = project_logs[project_id][-300:]

class CreateProjectModel(BaseModel):
    name: str
    field_settings: Optional[Dict[str, Any]] = None

class UpdateSettingsModel(BaseModel):
    field_settings: Dict[str, Any]

class UpdateItemModel(BaseModel):
    dong: Optional[str] = None
    ho: Optional[str] = None
    pipe_type: Optional[str] = None
    pipe_name: Optional[str] = None
    defect: Optional[str] = None
    position: Optional[str] = None
    standard_filename: Optional[str] = None

class ApiKeyModel(BaseModel):
    gemini: Optional[str] = None
    openai: Optional[str] = None

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME, "version": settings.VERSION}

@app.get("/api/keys")
async def get_keys_status():
    detected = settings.get_api_keys()
    if custom_api_keys.get("gemini"):
        detected["gemini"] = custom_api_keys["gemini"]
    if custom_api_keys.get("openai"):
        detected["openai"] = custom_api_keys["openai"]

    return {
        "gemini_configured": bool(detected.get("gemini")),
        "openai_configured": bool(detected.get("openai")),
        "google_vision_configured": bool(detected.get("google_vision"))
    }

@app.post("/api/keys")
async def update_keys(payload: ApiKeyModel):
    if payload.gemini:
        custom_api_keys["gemini"] = payload.gemini
    if payload.openai:
        custom_api_keys["openai"] = payload.openai
    return {"status": "success", "message": "API 키가 갱신되었습니다."}

# ==================== 프로젝트 관리 API ====================

@app.get("/api/projects")
async def list_projects():
    return ProjectManager.list_projects()

@app.post("/api/projects")
async def create_project(payload: CreateProjectModel):
    project = ProjectManager.create_project(name=payload.name, field_settings=payload.field_settings)
    return project

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    project = ProjectManager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="현장 프로젝트를 찾을 수 없습니다.")
    return project

@app.put("/api/projects/{project_id}/settings")
async def update_project_settings(project_id: str, payload: UpdateSettingsModel):
    success = ProjectManager.update_project_settings(project_id, payload.field_settings)
    if not success:
        raise HTTPException(status_code=404, detail="설정 업데이트 실패")
    return {"status": "success", "message": "현장 설정이 업데이트되었습니다."}

# ==================== 미디어 업로드 및 AI 분석 API ====================

@app.post("/api/projects/{project_id}/upload")
async def upload_project_media(
    project_id: str,
    files: List[UploadFile] = File(...)
):
    """스트리밍 방식으로 대용량 미디어 파일 안전 업로드"""
    project = ProjectManager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="현장 프로젝트를 찾을 수 없습니다.")

    proj_upload_dir = UPLOAD_DIR / project_id
    proj_upload_dir.mkdir(parents=True, exist_ok=True)

    added_items = []
    for file in files:
        item_id = str(uuid.uuid4())[:8]
        file_ext = os.path.splitext(file.filename)[1].lower()
        saved_path = proj_upload_dir / f"{item_id}_{file.filename}"

        # 디스크 스트리밍 복사 (메모리 절약)
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        is_video = file_ext in [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"]
        
        item_id = ProjectManager.add_inspection_item(project_id, {
            "id": item_id,
            "original_filename": file.filename,
            "original_file_path": str(saved_path),
            "frame_image_path": str(saved_path) if not is_video else None,
            "is_video": is_video,
            "status": "uploaded"
        })
        added_items.append(item_id)

    return {
        "status": "success",
        "uploaded_count": len(added_items),
        "item_ids": added_items
    }

def run_batch_analysis_task(project_id: str):
    """백그라운드 AI 명판 분석 워커 (타임스탬프 기반 동영상-결함사진 페어링 및 상속 지원)"""
    project = ProjectManager.get_project(project_id)
    if not project:
        return

    field_settings = project["field_settings"]
    all_items = project["items"]
    
    # 1. 신규 업로드된 항목만 선별 (기존 검수/완료 데이터 보존)
    target_items = [it for it in all_items if it.get("status") == "uploaded"]
    if not target_items:
        target_items = all_items  # 신규 항목이 없으면 전체 항목 대상

    total = len(target_items)
    add_project_log(project_id, f"🚀 AI 명판 일괄 분석 시작 (대상 {total}건)...", "header")

    api_keys = settings.get_api_keys()
    if custom_api_keys.get("gemini"):
        api_keys["gemini"] = custom_api_keys["gemini"]
    if custom_api_keys.get("openai"):
        api_keys["openai"] = custom_api_keys["openai"]

    proj_upload_dir = UPLOAD_DIR / project_id

    # 2. 타임스탬프 기반 동영상-사진 자동 페어링 분석
    pair_result = VideoEngine.pair_videos_and_defect_images(target_items)
    paired_map = pair_result["paired"] # video_id -> List[image_item]
    unpaired_images = pair_result["unpaired_images"]

    video_count = sum(1 for it in target_items if it.get("is_video"))
    image_count = len(target_items) - video_count
    add_project_log(project_id, f"🔗 타임스탬프 분석: 동영상 {video_count}건, 캡처사진 {image_count}건 매핑 준비 완료", "info")

    processed_count = 0

    # 3. 비디오 항목 분석 및 하위 결함 사진으로 메타데이터 자동 상속
    for item in target_items:
        if not item.get("is_video"):
            continue

        processed_count += 1
        analysis_progress[project_id] = {
            "current": processed_count,
            "total": total,
            "percentage": int((processed_count / max(total, 1)) * 100),
            "current_file": item["original_filename"],
            "status": "processing"
        }

        try:
            # 3-1. 비디오 0~10초 명판 프레임 스마트 추출
            out_frame_name = f"frame_{item['id']}.jpg"
            out_frame_path = str(proj_upload_dir / out_frame_name)
            VideoEngine.extract_best_nameplate_frame(
                video_path=item["original_file_path"],
                output_image_path=out_frame_path,
                search_duration_sec=10.0
            )
            frame_path = out_frame_path

            # 3-2. 비디오 명판 비전 AI 분석
            parsed = VisionEngine.analyze_nameplate(
                image_path=frame_path,
                field_settings=field_settings,
                api_keys=api_keys
            )

            # 비디오 항목 업데이트
            ProjectManager.update_inspection_item(project_id, item["id"], {
                "dong": parsed.get("dong", ""),
                "ho": parsed.get("ho", ""),
                "pipe_type": parsed.get("pipe_type", ""),
                "pipe_name": parsed.get("pipe_name", ""),
                "defect": parsed.get("defect", "정상"),
                "position": parsed.get("position", "입구"),
                "standard_filename": parsed.get("standard_filename", ""),
                "frame_image_path": frame_path,
                "status": "analyzed"
            })

            add_project_log(project_id, f"✓ [{item['original_filename']}] 명판 분석 성공 ➔ {parsed.get('standard_filename')}", "success")

            # 3-3. 해당 비디오의 녹화 시간대 내에 캡처된 결함 사진들에게 메타데이터 상속 및 수기 파일명 파싱
            child_images = paired_map.get(item["id"], [])
            for c_idx, child in enumerate(child_images, start=1):
                processed_count += 1
                child_dong = parsed.get("dong", "")
                child_ho = parsed.get("ho", "")
                child_pt = parsed.get("pipe_type", "")
                child_pn = parsed.get("pipe_name", "")

                # 작업자가 수기 입력한 파일명 뒤의 _이상소견_이상위치 파싱
                manual_defect, manual_pos = VideoEngine.parse_defect_and_position_from_filename(child["original_filename"])
                
                raw_defect = manual_defect or ("물고임" if c_idx == 1 else "이상소견")
                raw_pos = manual_pos or ("입구" if c_idx == 1 else f"{c_idx*0.5:.1f}m")

                # 현장 설정 기준 지능형 스냅
                child_parsed = VisionEngine._normalize_to_field_settings({
                    "dong": child_dong,
                    "ho": child_ho,
                    "pipe_type": child_pt,
                    "pipe_name": child_pn,
                    "defect": raw_defect,
                    "position": raw_pos
                }, field_settings)

                ProjectManager.update_inspection_item(project_id, child["id"], {
                    "dong": child_parsed.get("dong", ""),
                    "ho": child_parsed.get("ho", ""),
                    "pipe_type": child_parsed.get("pipe_type", ""),
                    "pipe_name": child_parsed.get("pipe_name", ""),
                    "defect": child_parsed.get("defect", "정상"),
                    "position": child_parsed.get("position", "입구"),
                    "standard_filename": child_parsed.get("standard_filename", ""),
                    "frame_image_path": child["original_file_path"],
                    "status": "analyzed"
                })

                log_suffix = " (수기 이상소견 스냅 반영)" if manual_defect else ""
                add_project_log(project_id, f"  └ 📸 결함사진 [{child['original_filename']}] 상속 완료 ➔ {child_parsed.get('standard_filename')}{log_suffix}", "info")

        except Exception as e:
            logger.error(f"비디오 항목 분석 오류 ({item['original_filename']}): {e}")
            ProjectManager.update_inspection_item(project_id, item["id"], {"status": "error"})
            add_project_log(project_id, f"❌ [{item['original_filename']}] 분석 실패: {str(e)}", "error")

    # 4. 페어링되지 않은 독립 사진 항목 분석
    for item in unpaired_images:
        processed_count += 1
        analysis_progress[project_id] = {
            "current": processed_count,
            "total": total,
            "percentage": int((processed_count / max(total, 1)) * 100),
            "current_file": item["original_filename"],
            "status": "processing"
        }

        try:
            manual_defect, manual_pos = VideoEngine.parse_defect_and_position_from_filename(item["original_filename"])

            parsed = VisionEngine.analyze_nameplate(
                image_path=item["original_file_path"],
                field_settings=field_settings,
                api_keys=api_keys
            )
            
            if manual_defect:
                parsed["defect"] = manual_defect
            if manual_pos:
                parsed["position"] = manual_pos

            parsed = VisionEngine._normalize_to_field_settings(parsed, field_settings)

            ProjectManager.update_inspection_item(project_id, item["id"], {
                "dong": parsed.get("dong", ""),
                "ho": parsed.get("ho", ""),
                "pipe_type": parsed.get("pipe_type", ""),
                "pipe_name": parsed.get("pipe_name", ""),
                "defect": parsed.get("defect", "정상"),
                "position": parsed.get("position", "입구"),
                "standard_filename": parsed.get("standard_filename", ""),
                "frame_image_path": item["original_file_path"],
                "status": "analyzed"
            })
            add_project_log(project_id, f"✓ [독립사진: {item['original_filename']}] 분석 완료 ➔ {parsed.get('standard_filename')}", "success")
        except Exception as e:
            logger.error(f"사진 항목 분석 오류 ({item['original_filename']}): {e}")
            ProjectManager.update_inspection_item(project_id, item["id"], {"status": "error"})
            add_project_log(project_id, f"❌ [{item['original_filename']}] 분석 실패: {str(e)}", "error")

    analysis_progress[project_id] = {
        "current": total,
        "total": total,
        "percentage": 100,
        "status": "completed"
    }
    add_project_log(project_id, f"🎉 총 {total}건의 명판 분석 및 표준 파일명 부여가 완료되었습니다.", "header")

@app.post("/api/projects/{project_id}/analyze")
async def start_analysis(project_id: str, background_tasks: BackgroundTasks):
    project = ProjectManager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    analysis_progress[project_id] = {
        "current": 0,
        "total": len(project["items"]),
        "percentage": 0,
        "status": "started"
    }
    background_tasks.add_task(run_batch_analysis_task, project_id)
    return {"status": "started", "message": "배치 AI 분석이 시작되었습니다."}

@app.get("/api/projects/{project_id}/analyze-progress")
async def get_analysis_progress(project_id: str):
    progress = analysis_progress.get(project_id, {"status": "idle", "percentage": 0})
    return progress

# ==================== 실시간 로그 API ====================

@app.get("/api/projects/{project_id}/logs")
async def get_project_logs(project_id: str):
    logs = project_logs.get(project_id, [])
    return {"status": "success", "logs": logs}

@app.delete("/api/projects/{project_id}/logs")
async def clear_project_logs(project_id: str):
    project_logs[project_id] = []
    return {"status": "success", "message": "로그가 초기화되었습니다."}

# ==================== 마스터 엑셀 템플릿 관리 API ====================

@app.post("/api/projects/{project_id}/template")
async def upload_project_template(project_id: str, file: UploadFile = File(...)):
    """현장별 커스텀 마스터 엑셀 템플릿 업로드"""
    project = ProjectManager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    if not file.filename.lower().endswith((".xlsx", ".xlsm")):
        raise HTTPException(status_code=400, detail="엑셀 파일(.xlsx, .xlsm)만 업로드 가능합니다.")

    tpl_dir = UPLOAD_DIR / project_id / "templates"
    tpl_dir.mkdir(parents=True, exist_ok=True)
    custom_tpl_path = tpl_dir / f"master_template_{file.filename}"

    with open(custom_tpl_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    add_project_log(project_id, f"📁 신규 마스터 엑셀 템플릿 등록 완료: {file.filename}", "success")

    return {
        "status": "success",
        "filename": file.filename,
        "template_path": str(custom_tpl_path)
    }

@app.get("/api/projects/{project_id}/template/info")
async def get_project_template_info(project_id: str):
    """현재 적용 중인 마스터 템플릿 정보 반환"""
    tpl_dir = UPLOAD_DIR / project_id / "templates"
    custom_tpls = list(tpl_dir.glob("master_template_*")) if tpl_dir.exists() else []

    if custom_tpls:
        latest = sorted(custom_tpls, key=lambda p: p.stat().st_mtime, reverse=True)[0]
        return {
            "is_custom": True,
            "filename": latest.name.replace("master_template_", ""),
            "size": latest.stat().st_size
        }
    else:
        default_tpl = ExcelReportEngine.get_template_path()
        return {
            "is_custom": False,
            "filename": "master_sample_0416.xlsx (기본 제공 마스터 서식)",
            "size": os.path.getsize(default_tpl) if default_tpl else 0
        }

@app.post("/api/projects/{project_id}/template/reset")
async def reset_project_template(project_id: str):
    """기본 마스터 템플릿으로 복원"""
    tpl_dir = UPLOAD_DIR / project_id / "templates"
    if tpl_dir.exists():
        shutil.rmtree(tpl_dir)
    add_project_log(project_id, "↺ 기본 마스터 템플릿으로 복원되었습니다.", "info")
    return {"status": "success", "message": "기본 템플릿으로 복원되었습니다."}

# ==================== 검수 에디터 실시간 자동저장 API ====================

@app.patch("/api/projects/{project_id}/items/{item_id}")
async def update_inspection_item(project_id: str, item_id: str, payload: UpdateItemModel):
    updates = payload.dict(exclude_unset=True)
    success = ProjectManager.update_inspection_item(project_id, item_id, updates)
    if not success:
        raise HTTPException(status_code=404, detail="항목 업데이트 실패")
    return {"status": "success", "item_id": item_id}

# ==================== 보고서 생성 및 다운로드 API ====================

@app.post("/api/projects/{project_id}/generate-report")
async def generate_project_report(project_id: str):
    project = ProjectManager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    items = project["items"]
    safe_name = "".join(c for c in project["name"] if c not in r'\/:*?"<>|').strip() or "SiteReport"

    out_excel_name = f"배관검사보고서_{safe_name}_{project_id}.xlsx"
    out_excel_path = str(OUTPUT_DIR / out_excel_name)

    add_project_log(project_id, f"📊 엑셀 마스터 보고서({out_excel_name}) 생성 시작...", "info")

    # 커스텀 템플릿 확인
    tpl_dir = UPLOAD_DIR / project_id / "templates"
    custom_tpls = list(tpl_dir.glob("master_template_*")) if tpl_dir.exists() else []
    custom_tpl_path = str(sorted(custom_tpls, key=lambda p: p.stat().st_mtime, reverse=True)[0]) if custom_tpls else None

    # 1. 엑셀 생성
    ExcelReportEngine.generate_pipe_report(
        project_name=project["name"],
        items=items,
        output_excel_path=out_excel_path,
        custom_template_path=custom_tpl_path
    )
    add_project_log(project_id, f"✓ 엑셀 시트 데이터 및 사진 정밀 주입 완료", "success")

    # 2. ZIP 압축 생성
    out_zip_name = f"표준미디어묶음_{safe_name}_{project_id}.zip"
    out_zip_path = str(OUTPUT_DIR / out_zip_name)
    ExcelReportEngine.create_renamed_zip_package(
        items=items,
        output_zip_path=out_zip_path,
        excel_path=out_excel_path
    )
    add_project_log(project_id, f"✓ 표준 미디어 파일 ZIP 압축 패키징 완료", "success")

    return {
        "status": "success",
        "excel_download_url": f"/api/download/{out_excel_name}",
        "zip_download_url": f"/api/download/{out_zip_name}",
        "excel_filename": out_excel_name,
        "zip_filename": out_zip_name
    }

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/octet-stream"
    )

@app.get("/api/media/{project_id}/{filename}")
async def get_project_media(project_id: str, filename: str):
    file_path = UPLOAD_DIR / project_id / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="미디어를 찾을 수 없습니다.")
    return FileResponse(path=str(file_path))

# 프론트엔드 정적 빌드 서빙
FRONTEND_DIST = ROOT_DIR / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
