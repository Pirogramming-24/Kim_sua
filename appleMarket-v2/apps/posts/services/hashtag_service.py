from ultralytics import YOLO
from PIL import Image

# 모델 로드는 함수 밖에서 한 번만
model = YOLO('yolov8n.pt')

def generate_hashtags(photo_field):
    # .path 대신 .file을 사용하여 이미지 데이터를 직접 엽니다.
    # 이렇게 하면 파일이 아직 디스크에 저장 완료되지 않았어도 처리가 가능합니다.
    img = Image.open(photo_field.file)
    results = model(img)
    
    hashtags = []
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            label = model.names[class_id]
            hashtags.append(f"#{label}")
            
    return list(set(hashtags))