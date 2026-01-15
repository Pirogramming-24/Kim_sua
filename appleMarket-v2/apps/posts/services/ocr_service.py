import os
import cv2
import numpy as np
import re
import easyocr

# 전역 변수로 리더 설정 (속도 향상을 위해 한 번만 로드)
_reader = None

def get_reader():
    global _reader
    if _reader is None:
        try:
            # gpu=False로 설정하여 CPU만 사용 (가장 안전함)
            _reader = easyocr.Reader(['ko', 'en'], gpu=False)
            print("--- [SUCCESS] EasyOCR 리더 로드 완료 ---")
        except Exception as e:
            print(f"--- [ERROR] 리더 로드 실패: {e} ---")
    return _reader

def extract_nutrition_text(image_file):
    reader = get_reader()
    if reader is None:
        return {}

    try:
        # 1. 이미지 로드
        image_file.seek(0)
        file_bytes = np.frombuffer(image_file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if img is None:
            print("[ERROR] 이미지를 읽을 수 없습니다.")
            return {}

        # 2. 이미지 전처리 (회색조 변환 및 확대)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_resized = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

        # 3. OCR 실행
        # paragraph=True로 설정하면 문장 단위로 묶어서 읽어줍니다.
        result = reader.readtext(img_resized, detail=0)
        
        print(f"\n--- [OCR 인식 결과] ---\n{result}\n-----------------------\n")
        
        if not result:
            return {}

        return parse_nutrition_info(result)

    except Exception as e:
        print(f"--- [OCR 실행 에러]: {e} ---")
        return {}

def parse_nutrition_info(texts):
    full_text = "".join(texts).replace(" ", "")
    # [DEBUG] 로그는 그대로 유지해서 터미널로 확인하세요.
    print(f"[DEBUG] 분석 대상: {full_text}")
    
    data = {"calories": 0, "carbs": 0.0, "protein": 0.0, "fat": 0.0}
    
    # 패턴 최적화 (g 앞의 숫자만 정확히 가져오도록 수정)
    patterns = {
        "carbs": r"탄수화물.*?(\d+(?:\.\d+)?)g?",
        "protein": r"단백질.*?(\d+(?:\.\d+)?)g?",
        "fat": r"(?:지방|지질).*?(\d+(?:\.\d+)?)g?",
        "calories": r"(\d+(?:\.\d+)?)(?:kcal|열량|칼로리)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, full_text)
        if match:
            val = float(match.group(1))
            # 지방이나 단백질이 너무 큰 숫자로 잡히는 현상 방지 (보통 100g 안팎이므로)
            if key in ["fat", "protein", "carbs"] and val > 500:
                # 159처럼 g가 9로 읽힌 경우 앞의 숫자만 취함
                val = float(str(int(val))[:2]) 
            data[key] = val
            
    return data