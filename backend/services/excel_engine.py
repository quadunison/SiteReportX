import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as OpenpyxlImage
from PIL import Image as PILImage
import logging

logger = logging.getLogger(__name__)

# 마스터 템플릿 기본 경로
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "templates", "master_sample_0416.xlsx")
FALLBACK_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "master_sample_0416.xlsx")

class ExcelReportEngine:
    """실무 규격 엑셀 보고서 생성 및 미디어 패키징 엔진 (master_sample_0416.xlsx 100% 매핑)"""

    @classmethod
    def get_template_path(cls) -> Optional[str]:
        if os.path.exists(TEMPLATE_PATH):
            return os.path.abspath(TEMPLATE_PATH)
        if os.path.exists(FALLBACK_TEMPLATE_PATH):
            return os.path.abspath(FALLBACK_TEMPLATE_PATH)
        return None

    @classmethod
    def generate_pipe_report(
        cls, 
        project_name: str,
        items: List[Dict[str, Any]], 
        output_excel_path: str,
        custom_template_path: Optional[str] = None
    ) -> str:
        """
        마스터 템플릿(master_sample_0416.xlsx 또는 사용자 지정 템플릿) 기반 실무 엑셀 보고서 생성
        (템플릿이 없을 경우 표준 간이 리포트로 안전하게 자동 생성)
        """
        tpl_path = custom_template_path if (custom_template_path and os.path.exists(custom_template_path)) else cls.get_template_path()
        if tpl_path:
            try:
                return cls.generate_master_pipe_report(tpl_path, project_name, items, output_excel_path)
            except Exception as e:
                logger.error(f"마스터 템플릿 주입 실패, 기본 양식으로 폴백: {e}", exc_info=True)

        return cls.generate_basic_pipe_report(project_name, items, output_excel_path)

    @classmethod
    def generate_master_pipe_report(
        cls,
        template_path: str,
        project_name: str,
        items: List[Dict[str, Any]],
        output_excel_path: str
    ) -> str:
        """
        master_sample_0416.xlsx 서식에 검수 항목들을 배관종류별로 분기하여 사진과 함께 정밀 주입
        """
        wb = openpyxl.load_workbook(template_path)
        today_str = datetime.now().strftime("%Y.%m.%d")

        # 1. 표지 시트 업데이트
        if "표지" in wb.sheetnames:
            cover = wb["표지"]
            cover["C4"] = f"배관내시경 점검 이상배관 보고 - {project_name}"

        # 2. 입력창 시트 업데이트 (모든 하위 시트 수식 =입력창!B4 연동)
        if "입력창" in wb.sheetnames:
            inp = wb["입력창"]
            inp["B4"] = f"<현장명 : {project_name}>"

        # 3. 공통 스타일 정의
        data_font = Font(name="맑은 고딕", size=10, color="000000")
        warn_font = Font(name="맑은 고딕", size=10, bold=True, color="DC2626")
        defect_fill = PatternFill(start_color="FEF08A", end_color="FEF08A", fill_type="solid") # Warning Yellow
        center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        # 4. 배관종류별 시트 매핑
        sheet_mapping = {
            "입상관": "3.이상배관LIST_입상관",
            "세대매립관": "3.이상배관LIST_세대매립관",
            "세대PD": "3.이상배관LIST_세대PD",
            "세대층상배관": "3.이상배관LIST_세대층상배관"
        }

        # 배관종류별로 데이터 분류
        categorized_items: Dict[str, List[Dict[str, Any]]] = {
            "입상관": [],
            "세대매립관": [],
            "세대PD": [],
            "세대층상배관": []
        }

        for it in items:
            pt = str(it.get("pipe_type", "")).replace(" ", "")
            matched_cat = None
            for cat_key in categorized_items.keys():
                if cat_key in pt or pt in cat_key:
                    matched_cat = cat_key
                    break
            if not matched_cat:
                matched_cat = "입상관" if "입상" in pt else "세대매립관"
            
            categorized_items[matched_cat].append(it)

        # 5. 각 배관종류별 이상배관LIST 시트에 데이터 및 사진 주입
        for cat_name, cat_items in categorized_items.items():
            sname = sheet_mapping.get(cat_name)
            if not sname or sname not in wb.sheetnames or not cat_items:
                continue

            ws = wb[sname]
            current_row = 4  # 4행부터 데이터 시작

            for idx, item in enumerate(cat_items, start=1):
                dong = str(item.get("dong", "")).replace("동", "").strip()
                ho = str(item.get("ho", "")).replace("호", "").strip()
                dong_val = f"{dong}동" if dong else ""
                ho_val = f"{ho}호" if ho else ""
                pipe_name = item.get("pipe_name", "-")
                defect = item.get("defect", "정상")
                position = item.get("position", "입구")
                is_defect = defect not in ["정상", "-", "양호", "이상없음", ""]

                ws.row_dimensions[current_row].height = 120

                # 셀 값 채우기
                ws.cell(row=current_row, column=1, value=idx)                # A: NO
                ws.cell(row=current_row, column=2, value=today_str)           # B: 점검일
                ws.cell(row=current_row, column=3, value=dong_val)            # C: 동명
                ws.cell(row=current_row, column=4, value=ho_val)              # D: 호수(라인)
                ws.cell(row=current_row, column=5, value=pipe_name)          # E: 배관명
                ws.cell(row=current_row, column=7, value=position)           # G: 이상위치
                ws.cell(row=current_row, column=8, value=defect)             # H: 이상소견
                ws.cell(row=current_row, column=9, value=today_str)          # I: 보고일

                # 셀 서식 및 테두리 설정
                for c in range(1, 10):
                    cell = ws.cell(row=current_row, column=c)
                    cell.alignment = center_align
                    cell.border = thin_border
                    cell.font = data_font
                    if c == 8 and is_defect:
                        cell.font = warn_font
                        cell.fill = defect_fill

                # F열: 사진을 셀 크기에 맞추어 1픽셀 여백으로 가득 채움 (템플릿 기준: 너비 199px, 높이 158px)
                img_path = item.get("frame_image_path") or item.get("original_file_path")
                if img_path and os.path.exists(img_path) and not img_path.lower().endswith(('.mp4', '.avi', '.mov')):
                    try:
                        # 템플릿의 F열 셀 크기(너비 200px, 높이 159px)에서 1픽셀 작은 크기로 꽉 채움
                        target_width = 199
                        target_height = 158

                        img = OpenpyxlImage(img_path)
                        img.width = target_width
                        img.height = target_height
                        ws.add_image(img, f"F{current_row}")
                    except Exception as img_err:
                        logger.warning(f"이미지 삽입 실패 ({img_path}): {img_err}")

                current_row += 1

        os.makedirs(os.path.dirname(output_excel_path), exist_ok=True)
        wb.save(output_excel_path)
        logger.info(f"마스터 템플릿 보고서 생성 완료: {output_excel_path}")
        return output_excel_path

    @classmethod
    def generate_basic_pipe_report(
        cls, 
        project_name: str,
        items: List[Dict[str, Any]], 
        output_excel_path: str
    ) -> str:
        """기본 단일 시트 간이 리포트 생성 (폴백 모드)"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "배관검사보고서"
        ws.views.sheetView[0].showGridLines = True

        title_font = Font(name="맑은 고딕", size=16, bold=True, color="0F172A")
        header_font = Font(name="맑은 고딕", size=10, bold=True, color="FFFFFF")
        data_font = Font(name="맑은 고딕", size=10, color="0F172A")
        warn_font = Font(name="맑은 고딕", size=10, bold=True, color="DC2626")

        header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        defect_fill = PatternFill(start_color="FEF08A", end_color="FEF08A", fill_type="solid")
        zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )
        center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)

        ws.merge_cells("A1:G2")
        title_cell = ws["A1"]
        title_cell.value = f"📋 [{project_name}] 배관내시경 이상유무 검사 보고서"
        title_cell.font = title_font
        title_cell.alignment = center_align

        headers = ["연번", "위치(동/호)", "배관종류", "배관명", "이상소견", "이상위치", "현장 검사 사진 (명판 / 결함부)"]
        ws.row_dimensions[4].height = 28

        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=4, column=col_idx, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align
            cell.border = thin_border

        col_widths = {1: 8, 2: 16, 3: 16, 4: 20, 5: 14, 6: 14, 7: 35}
        for col_idx, width in col_widths.items():
            ws.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = width

        current_row = 5
        for idx, item in enumerate(items, start=1):
            dong = item.get("dong", "")
            ho = item.get("ho", "")
            location_str = f"{dong}동 {ho}호" if (dong or ho) else "-"
            pipe_type = item.get("pipe_type", "-")
            pipe_name = item.get("pipe_name", "-")
            defect = item.get("defect", "정상")
            position = item.get("position", "입구")

            ws.row_dimensions[current_row].height = 110
            is_defect = defect not in ["정상", "-", "양호", "이상없음", ""]
            row_data = [idx, location_str, pipe_type, pipe_name, defect, position, ""]

            for col_idx, val in enumerate(row_data, start=1):
                cell = ws.cell(row=current_row, column=col_idx, value=val)
                cell.font = warn_font if (col_idx == 5 and is_defect) else data_font
                cell.alignment = center_align
                cell.border = thin_border
                
                if col_idx == 5 and is_defect:
                    cell.fill = defect_fill
                elif idx % 2 == 0:
                    cell.fill = zebra_fill

            img_path = item.get("frame_image_path") or item.get("original_file_path")
            if img_path and os.path.exists(img_path) and not img_path.lower().endswith(('.mp4', '.avi', '.mov')):
                try:
                    with PILImage.open(img_path) as pil_img:
                        w, h = pil_img.size
                        aspect = w / h
                        target_h = 130
                        target_w = int(target_h * aspect)
                        if target_w > 240:
                            target_w = 240
                            target_h = int(target_w / aspect)

                    img = OpenpyxlImage(img_path)
                    img.width = target_w
                    img.height = target_h
                    ws.add_image(img, f"G{current_row}")
                except Exception as e:
                    logger.error(f"엑셀 사진 삽입 실패: {e}")

            current_row += 1

        os.makedirs(os.path.dirname(output_excel_path), exist_ok=True)
        wb.save(output_excel_path)
        return output_excel_path

    @classmethod
    def create_renamed_zip_package(
        cls, 
        items: List[Dict[str, Any]], 
        output_zip_path: str,
        excel_path: Optional[str] = None
    ) -> str:
        """표준 명명 규칙으로 이름을 변경한 미디어 파일들과 엑셀 보고서를 하나의 ZIP으로 압축"""
        os.makedirs(os.path.dirname(output_zip_path), exist_ok=True)

        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if excel_path and os.path.exists(excel_path):
                zipf.write(excel_path, arcname=os.path.basename(excel_path))

            for idx, item in enumerate(items, start=1):
                raw_path = item.get("original_file_path")
                if raw_path and os.path.exists(raw_path):
                    ext = os.path.splitext(raw_path)[1]
                    std_name = item.get("standard_filename")
                    if not std_name:
                        std_name = f"PipeInspection_{idx:03d}"

                    safe_name = "".join(c for c in std_name if c not in r'\/:*?"<>|').strip()
                    arc_name = f"media/{safe_name}{ext}"
                    zipf.write(raw_path, arcname=arc_name)

        return output_zip_path
