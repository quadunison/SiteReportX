import os
import re
from datetime import datetime, timedelta
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)

class VideoEngine:
    """영상 초반 0~10초 명판 프레임 스마트 선명도 추출 및 타임스탬프 기반 미디어 매핑 엔진"""

    @staticmethod
    def calculate_sharpness(image: np.ndarray) -> float:
        """Laplacian 분산 기반 블러 검출 및 선명도 계산"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return float(cv2.Laplacian(gray, cv2.CV_64F).var())
        except Exception:
            return 0.0

    @classmethod
    def parse_datetime_from_filename(cls, filepath: str) -> datetime:
        """
        파일명(예: 20240626142030, 20240626_142030, 2024-06-26_14-20-30 등) 또는 파일 메타데이터에서 datetime 추출
        """
        filename = os.path.basename(filepath)
        
        # 1. 14자리 연속 숫자 (YYYYMMDDHHMMSS)
        m1 = re.search(r'(20\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])([01]\d|2[0-3])([0-5]\d)([0-5]\d)', filename)
        if m1:
            try:
                return datetime(
                    int(m1.group(1)), int(m1.group(2)), int(m1.group(3)),
                    int(m1.group(4)), int(m1.group(5)), int(m1.group(6))
                )
            except Exception:
                pass

        # 2. YYYYMMDD_HHMMSS 또는 YYYY-MM-DD_HH-MM-SS 형식
        m2 = re.search(r'(20\d{2})[-_]?(0[1-9]|1[0-2])[-_]?(0[1-9]|[12]\d|3[01])[-_ ]([01]\d|2[0-3])[-_:]?([0-5]\d)[-_:]?([0-5]\d)', filename)
        if m2:
            try:
                return datetime(
                    int(m2.group(1)), int(m2.group(2)), int(m2.group(3)),
                    int(m2.group(4)), int(m2.group(5)), int(m2.group(6))
                )
            except Exception:
                pass

        # 3. 정규식 실패 시 파일 수정 시각(mtime) 사용
        try:
            mtime = os.path.getmtime(filepath)
            return datetime.fromtimestamp(mtime)
        except Exception:
            return datetime.now()

    @classmethod
    def parse_defect_and_position_from_filename(cls, filename: str) -> Tuple[Optional[str], Optional[str]]:
        """
        파일명(예: 20260825115800_이물질_입구.jpg, 20240626_142215_배관파손_1.5m.jpg)에서 
        작업자가 수기 입력한 (이상소견, 이상위치)를 추출
        """
        base_name = os.path.splitext(os.path.basename(filename))[0]
        # 언더스코어(_)로 분리
        parts = base_name.split("_")
        
        defect = None
        position = None

        if len(parts) >= 3:
            # 예: 20260825115800 _ 이물질 _ 입구
            defect = parts[1].strip()
            position = parts[2].strip()
        elif len(parts) == 2:
            # 예: 20260825115800 _ 이물질
            defect = parts[1].strip()

        return defect, position

    @classmethod
    def get_video_duration(cls, video_path: str) -> float:
        """동영상 재생 길이(초) 반환"""
        if not os.path.exists(video_path):
            return 0.0
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return 0.0
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        return round(total_frames / fps, 2) if fps > 0 else 0.0

    @classmethod
    def extract_best_nameplate_frame(
        cls, 
        video_path: str, 
        output_image_path: str, 
        search_duration_sec: float = 10.0,
        fps_sample: float = 2.5
    ) -> Dict[str, Any]:
        """
        영상 0 ~ search_duration_sec 구간을 샘플링하여 가장 선명한 명판 프레임 1장을 추출
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"비디오 파일을 찾을 수 없습니다: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"비디오를 열 수 없습니다: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps

        max_search_frames = min(int(search_duration_sec * fps), total_frames)
        step = max(1, int(fps / fps_sample))

        best_frame = None
        best_sharpness = -1.0
        best_timestamp = 0.0

        current_frame = 0
        while current_frame < max_search_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
            ret, frame = cap.read()
            if not ret:
                break

            sharpness = cls.calculate_sharpness(frame)
            if sharpness > best_sharpness:
                best_sharpness = sharpness
                best_frame = frame.copy()
                best_timestamp = current_frame / fps

            current_frame += step

        # 만약 0~10초 구간에서 못 찾은 경우 첫 프레임이라도 확보
        if best_frame is None and total_frames > 0:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if ret:
                best_frame = frame
                best_sharpness = cls.calculate_sharpness(frame)
                best_timestamp = 0.0

        cap.release()

        if best_frame is None:
            raise RuntimeError(f"프레임 추출 실패: {video_path}")

        os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
        cv2.imwrite(output_image_path, best_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])

        return {
            "success": True,
            "extracted_frame_path": output_image_path,
            "timestamp": round(best_timestamp, 2),
            "sharpness": round(best_sharpness, 2),
            "total_duration": round(duration, 2)
        }

    @classmethod
    def pair_videos_and_defect_images(
        cls, 
        items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        비디오 항목들과 스틸컷(JPG) 항목들의 촬영 시각을 분석하여
        비디오의 녹화 시간 구간 내에 발생한 사진들을 비디오와 자동 페어링
        
        Returns:
            Dict: {"paired": Dict[video_item_id, List[image_item]], "unpaired_images": List[image_item]}
        """
        video_items = [it for it in items if it.get("is_video")]
        image_items = [it for it in items if not it.get("is_video")]

        # 비디오들을 시작 시각 순으로 정렬
        video_with_time = []
        for v in video_items:
            v_path = v.get("original_file_path", "")
            start_dt = cls.parse_datetime_from_filename(v_path)
            duration = cls.get_video_duration(v_path)
            video_with_time.append({
                "video": v,
                "start_dt": start_dt,
                "duration": duration
            })
        video_with_time.sort(key=lambda x: x["start_dt"])

        # 각 비디오의 구간 산출 (다음 비디오 시작 전 또는 duration 기반)
        video_intervals: List[Dict[str, Any]] = []
        for i, v_info in enumerate(video_with_time):
            start_dt = v_info["start_dt"]
            duration = v_info["duration"]
            
            if duration > 1.0:
                end_dt = start_dt + timedelta(seconds=duration + 10.0)
            else:
                # duration을 측정할 수 없는 경우 다음 비디오 시작 시각 또는 최대 15분 후로 설정
                if i + 1 < len(video_with_time):
                    end_dt = video_with_time[i+1]["start_dt"]
                else:
                    end_dt = start_dt + timedelta(minutes=15)

            video_intervals.append({
                "video": v_info["video"],
                "start_dt": start_dt - timedelta(seconds=3.0),
                "end_dt": end_dt
            })

        pair_map: Dict[str, List[Dict[str, Any]]] = {v["id"]: [] for v in video_items}
        unpaired_images = []

        for img in image_items:
            img_path = img.get("original_file_path", "")
            img_dt = cls.parse_datetime_from_filename(img_path)
            
            matched_video_id = None
            for v_info in video_intervals:
                if v_info["start_dt"] <= img_dt <= v_info["end_dt"]:
                    matched_video_id = v_info["video"]["id"]
                    break

            if matched_video_id:
                pair_map[matched_video_id].append(img)
            else:
                unpaired_images.append(img)

        return {
            "paired": pair_map,
            "unpaired_images": unpaired_images
        }
