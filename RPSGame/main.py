import cv2 as cv
import mediapipe as mp
import math
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from visualization import draw_manual, print_RSP_result

# 1. 두 점 사이의 거리를 계산하는 함수
def get_distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

# 2. 가위바위보 판별 로직 (0: Rock, 1: Paper, 2: Scissors)
def identify_rps(hand_landmarks):
    wrist = hand_landmarks[0] # 손목 좌표
    
    # 체크할 손가락 (끝점, 중간마디): 엄지 제외 검지~소지만 사용
    finger_indices = [(8, 6), (12, 10), (16, 14), (20, 18)]
    opened_fingers = 0
    
    for tip_idx, pip_idx in finger_indices:
        dist_tip = get_distance(hand_landmarks[tip_idx], wrist)
        dist_pip = get_distance(hand_landmarks[pip_idx], wrist)
        
        if dist_tip > dist_pip:
            opened_fingers += 1
            
    # 펴진 손가락 개수에 따른 결과 반환
    if opened_fingers == 0:
        return 0  # Rock
    elif opened_fingers == 2:
        return 2  # Scissors (검지, 중지)
    elif opened_fingers >= 4:
        return 1  # Paper
    else:
        return None

def main():
    # MediaPipe Hand Landmarker 초기 세팅
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        running_mode=vision.RunningMode.IMAGE
    )
    detector = vision.HandLandmarker.create_from_options(options)

    # 캠 열기
    cap = cv.VideoCapture(0)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # MediaPipe용 이미지 변환
        image_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        
        # 랜드마크 검출
        detection_result = detector.detect(mp_image)

        if detection_result.hand_landmarks:
            # 첫 번째 감지된 손 사용
            hand_landmarks = detection_result.hand_landmarks[0]
            
            # 1) 가위바위보 판별
            rps_result = identify_rps(hand_landmarks)
            
            # 2) 제공된 함수로 시각화 (선/점 그리기)
            frame = draw_manual(frame, detection_result)
            
            # 3) 제공된 함수로 결과 텍스트 출력
            frame = print_RSP_result(frame, rps_result)

        # 화면 출력
        cv.imshow('Piro24 RPS Game', frame)

        # 'q' 누르면 종료
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()
    detector.close()

if __name__ == "__main__":
    main()