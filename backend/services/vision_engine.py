import os
import json
import base64
import re
import requests
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class VisionEngine:
    """TaskieX 호환 다중 AI 비전 파이프라인 (Google Vision OCR, Gemini Flash, OpenAI GPT-4o-mini)"""

    @staticmethod
    def encode_image_base64(image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    @classmethod
    def analyze_nameplate(
        cls, 
        image_path: str, 
        field_settings: Dict[str, Any],
        api_keys: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        명판 이미지를 다중 AI 엔진으로 분석하고 현장 설정에 맞추어 정규화된 데이터 반환
        """
        api_keys = api_keys or {}
        gemini_key = api_keys.get("gemini")
        openai_key = api_keys.get("openai")
        vision_key = api_keys.get("google_vision")

        # 1. Google Gemini (최신 안정화 엔드포인트: gemini-flash-latest) 시도
        if gemini_key:
            try:
                res = cls._analyze_with_gemini(image_path, field_settings, gemini_key)
                if res and res.get("dong"):
                    logger.info(f"Gemini 비전 분석 성공: {res}")
                    return cls._normalize_to_field_settings(res, field_settings)
            except Exception as e:
                logger.warning(f"Gemini API 호출 실패: {e}")

        # 2. OpenAI GPT-4o-mini Vision 시도
        if openai_key:
            try:
                res = cls._analyze_with_openai(image_path, field_settings, openai_key)
                if res and res.get("dong"):
                    logger.info(f"OpenAI 비전 분석 성공: {res}")
                    return cls._normalize_to_field_settings(res, field_settings)
            except Exception as e:
                logger.warning(f"OpenAI API 호출 실패: {e}")

        # 3. Google Cloud Vision OCR 시도
        if vision_key and os.path.exists(vision_key):
            try:
                res = cls._analyze_with_google_vision(image_path, field_settings, vision_key)
                if res and res.get("dong"):
                    logger.info(f"Google Vision OCR 분석 성공: {res}")
                    return cls._normalize_to_field_settings(res, field_settings)
            except Exception as e:
                logger.warning(f"Google Cloud Vision OCR 호출 실패: {e}")

        # 4. 폴백: 규칙 기반 추론
        fallback_res = cls._fallback_parsing(image_path)
        return cls._normalize_to_field_settings(fallback_res, field_settings)

    @classmethod
    def _build_dynamic_prompt(cls, field_settings: Dict[str, Any]) -> str:
        pipe_types_str = ", ".join(f"'{pt}'" for pt in field_settings.get("pipe_types", []))
        pipe_names_str = ", ".join(f"'{pn}'" for pn in field_settings.get("pipe_names", []))
        defect_options_str = ", ".join(f"'{df}'" for df in field_settings.get("defect_options", []))

        return f"""
당신은 건설/설비 배관내시경 검사 명판(소판, 화이트보드, 화면 자막) 전문 AI 분석가입니다.
이미지 속 명판의 글씨(손글씨, 스티커, 인쇄글씨)를 정확하게 읽고, 다음 JSON 형식으로만 응답하세요:

[추출 규칙]
1. dong: '위치' 또는 '동' 앞뒤의 동 번호 (예: '103', '101', 'A')
2. ho: '호' 앞의 호수 번호 (예: '1', '205', '1801')
3. pipe_type: 배관종류. 다음 목록 중 가장 가까운 것 선택: [{pipe_types_str}] (예: '입상관', '세대매립관')
4. pipe_name: 배관명. 명판에 적힌 배관 부위 (예: '부부욕실 오수', '앞발코니배수', '주방오수', '공용욕실', '세탁배수' 등)
5. defect: 이상소견 ('정상', '물고임', '구배불량', '토사/이물질', '파손/크랙' 중 선택, 기본값 '정상')
6. position: 결함 위치 ('입구', '0.5m', '1.0m', '엘보구간', '출구' 등, 기본값 '입구')

반드시 다음과 같은 순수 JSON으로만 응답하세요:
{{
  "dong": "103",
  "ho": "1",
  "pipe_type": "입상관",
  "pipe_name": "부부욕실오수",
  "defect": "정상",
  "position": "입구"
}}
"""

    @classmethod
    def _analyze_with_gemini(cls, image_path: str, field_settings: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
        base64_data = cls.encode_image_base64(image_path)
        mime_type = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"
        prompt = cls._build_dynamic_prompt(field_settings)

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": mime_type, "data": base64_data}}
                ]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        }

        resp = requests.post(url, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(raw_text)
        parsed["success"] = True
        return parsed

    @classmethod
    def _analyze_with_openai(cls, image_path: str, field_settings: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        url = "https://api.openai.com/v1/chat/completions"
        base64_data = cls.encode_image_base64(image_path)
        mime_type = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"
        prompt = cls._build_dynamic_prompt(field_settings)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_data}"}}
                ]
            }],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
        raw_text = resp.json()["choices"][0]["message"]["content"]
        parsed = json.loads(raw_text)
        parsed["success"] = True
        return parsed

    @classmethod
    def _analyze_with_google_vision(cls, image_path: str, field_settings: Dict[str, Any], credentials_path: str) -> Dict[str, Any]:
        from google.cloud import vision
        from google.oauth2 import service_account

        creds = service_account.Credentials.from_service_account_file(credentials_path)
        client = vision.ImageAnnotatorClient(credentials=creds)

        with open(image_path, "rb") as f:
            content = f.read()

        image = vision.Image(content=content)
        resp = client.text_detection(image=image)
        if not resp.text_annotations:
            raise ValueError("Google Vision OCR에서 텍스트를 검출하지 못했습니다.")

        full_text = resp.text_annotations[0].description
        
        # 정규식 패턴 파싱
        dong_m = re.search(r'(\d{3,4})\s*동', full_text)
        ho_m = re.search(r'(\d{1,4})\s*호', full_text)
        
        dong = dong_m.group(1) if dong_m else "101"
        ho = ho_m.group(1) if ho_m else "1"

        # 배관종류 매칭
        pipe_type = "세대매립관"
        for pt in ["입상관", "세대매립관", "세대PD", "세대층상배관", "오수관", "배수관", "통기관"]:
            if pt in full_text:
                pipe_type = pt
                break

        # 배관명 매칭
        pipe_name = "앞발코니배수"
        for pn in ["부부욕실오수", "부부욕실", "앞발코니배수", "앞발코니", "주방오수", "주방", "세탁배수", "공용욕실"]:
            if pn in full_text.replace(" ", ""):
                pipe_name = pn
                break

        return {
            "success": True,
            "dong": dong,
            "ho": ho,
            "pipe_type": pipe_type,
            "pipe_name": pipe_name,
            "defect": "정상",
            "position": "입구",
            "raw_text": full_text
        }

    @classmethod
    def _fallback_parsing(cls, image_path: str) -> Dict[str, Any]:
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        dong_m = re.search(r'(\d{3,4})동', base_name)
        ho_m = re.search(r'(\d{1,4})호', base_name)
        return {
            "success": True,
            "dong": dong_m.group(1) if dong_m else "101",
            "ho": ho_m.group(1) if ho_m else "1",
            "pipe_type": "세대매립관",
            "pipe_name": "앞발코니배수",
            "defect": "정상",
            "position": "입구",
            "raw_text": base_name
        }

    @classmethod
    def _normalize_to_field_settings(cls, parsed: Dict[str, Any], field_settings: Dict[str, Any]) -> Dict[str, Any]:
        dong_options = field_settings.get("dong_options", [])
        ho_options = field_settings.get("ho_options", [])
        pipe_types = field_settings.get("pipe_types", [])
        pipe_names = field_settings.get("pipe_names", [])
        defects = field_settings.get("defect_options", [])
        positions = field_settings.get("position_options", [])

        # 1. 동(Dong) 지능형 스냅
        raw_dong = str(parsed.get("dong", "")).replace("동", "").strip()
        matched_dong = raw_dong
        if dong_options:
            clean_opts = [str(opt).replace("동", "").strip() for opt in dong_options]
            if raw_dong in clean_opts:
                idx = clean_opts.index(raw_dong)
                matched_dong = str(dong_options[idx]).replace("동", "").strip()
            else:
                for idx, opt_clean in enumerate(clean_opts):
                    if opt_clean == raw_dong or opt_clean in raw_dong or raw_dong in opt_clean:
                        matched_dong = str(dong_options[idx]).replace("동", "").strip()
                        break
                else:
                    matched_dong = str(dong_options[0]).replace("동", "").strip()
        parsed["dong"] = matched_dong

        # 2. 호(Ho) 지능형 스냅
        raw_ho = str(parsed.get("ho", "")).replace("호", "").strip()
        matched_ho = raw_ho
        if ho_options:
            clean_ho_opts = [str(opt).replace("호", "").strip() for opt in ho_options]
            if raw_ho in clean_ho_opts:
                idx = clean_ho_opts.index(raw_ho)
                matched_ho = str(ho_options[idx]).replace("호", "").strip()
            else:
                for idx, opt_clean in enumerate(clean_ho_opts):
                    if opt_clean == raw_ho or opt_clean in raw_ho or raw_ho in opt_clean:
                        matched_ho = str(ho_options[idx]).replace("호", "").strip()
                        break
                else:
                    matched_ho = str(ho_options[0]).replace("호", "").strip()
        parsed["ho"] = matched_ho

        # 3. 배관종류(Pipe Type) 지능형 스냅
        raw_pt = str(parsed.get("pipe_type", "")).replace(" ", "")
        matched_pt = parsed.get("pipe_type", "")
        if pipe_types:
            for pt in pipe_types:
                pt_clean = str(pt).replace(" ", "")
                if pt_clean == raw_pt or pt_clean in raw_pt or raw_pt in pt_clean:
                    matched_pt = pt
                    break
            else:
                matched_pt = pipe_types[0]
        parsed["pipe_type"] = matched_pt

        # 4. 배관명(Pipe Name) 지능형 스냅
        raw_pn = str(parsed.get("pipe_name", "")).replace(" ", "")
        matched_pn = parsed.get("pipe_name", "")
        if pipe_names:
            # 1단계: 정확 일치 (공백 무시)
            for pn in pipe_names:
                if str(pn).replace(" ", "") == raw_pn:
                    matched_pn = pn
                    break
            else:
                # 2단계: 부분 일치 및 키워드 매칭
                best_match = None
                max_common = 0
                for pn in pipe_names:
                    pn_clean = str(pn).replace(" ", "")
                    # 공통 글자 수 계산
                    common_count = sum(1 for ch in raw_pn if ch in pn_clean)
                    if common_count > max_common:
                        max_common = common_count
                        best_match = pn
                if best_match and max_common >= 2:
                    matched_pn = best_match
                else:
                    matched_pn = pipe_names[0]
        parsed["pipe_name"] = matched_pn

        # 5. 이상소견(Defect) 지능형 스냅
        raw_df = str(parsed.get("defect", "정상")).replace(" ", "")
        matched_df = "정상"
        if defects:
            for df in defects:
                df_clean = str(df).replace(" ", "")
                if df_clean == raw_df or df_clean in raw_df or raw_df in df_clean:
                    matched_df = df
                    break
            else:
                matched_df = "정상"
        parsed["defect"] = matched_df

        # 6. 위치(Position) 지능형 스냅
        raw_pos = str(parsed.get("position", "입구")).replace(" ", "")
        matched_pos = "입구"
        if positions:
            for pos in positions:
                pos_clean = str(pos).replace(" ", "")
                if pos_clean == raw_pos or pos_clean in raw_pos or raw_pos in pos_clean:
                    matched_pos = pos
                    break
        parsed["position"] = matched_pos

        dong_str = f"{parsed['dong']}동" if parsed["dong"] else ""
        ho_str = f"{parsed['ho']}호" if parsed["ho"] else ""
        parsed["standard_filename"] = f"{dong_str} {ho_str} {parsed['pipe_type']} {parsed['pipe_name']}_{parsed['defect']}_{parsed['position']}".strip()
        return parsed
