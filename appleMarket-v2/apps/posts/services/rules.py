import re

def parse_nutrition_data(text_list):
    data = {
        'calories': 0, 
        'carbs': 0.0, 
        'protein': 0.0, 
        'fat': 0.0
    }
    
    # 1. 리스트를 문자열로 합침 (공백 유지)
    full_text = " ".join(text_list)
    
    # 2. '포화지방', '트랜스지방' 제거
    full_text = re.sub(r"(포화|트랜스)\s*지방", "", full_text)
    
    # 3. 모든 공백 제거 (OCR 공백 오류 무시를 위해)
    # 이제 "탄 수 화 물" 같은 띄어쓰기 변수를 통제합니다.
    clean_text = full_text.replace(" ", "")
    
    # 4. 정규표현식 패턴
    # (?:\.\d+)? : 소수점이 있을 수도 있고 없을 수도 있음
    patterns = {
        # 칼로리는 'kcal' 앞의 숫자 혹은 '열량' 뒤의 숫자
        'calories': r'(?:열량|칼로리|kcal).*?(\d+)', 
        'carbs': r'탄수화물.*?(\d+(?:\.\d+)?)',
        'protein': r'단백질.*?(\d+(?:\.\d+)?)',
        'fat': r'지방.*?(\d+(?:\.\d+)?)',
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, clean_text, re.IGNORECASE)
        if match:
            try:
                # 일단 float으로 변환
                val = float(match.group(1))
                
                # 칼로리는 정수, 나머지는 소수점 1자리
                if key == 'calories':
                    data[key] = int(val)
                else:
                    data[key] = round(val, 1)
            except ValueError:
                continue
                
    return data
