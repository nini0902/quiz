import cv2
import mediapipe as mp
import math

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

with mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # 獲取鼻尖與下巴的 Landmark
                nose_tip = face_landmarks.landmark[1]  # 鼻尖
                chin = face_landmarks.landmark[152]  # 下巴

                # 計算鼻尖與下巴之間的垂直角度
                dx = nose_tip.x - chin.x
                dy = nose_tip.y - chin.y
                dz = nose_tip.z - chin.z  # 深度座標
                vertical_angle = math.degrees(math.atan2(dy, math.sqrt(dx**2 + dz**2)))

                # 判斷是否為低頭
                if vertical_angle > -50: #調整低頭的參數
                    cv2.putText(frame, "Head Down Detected", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # 顯示垂直角度
                cv2.putText(frame, f"Vertical Angle: {vertical_angle:.2f} degrees", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow('Head Down Detection', frame)

        if cv2.waitKey(5) & 0xFF == 27:  # 按下 Esc 鍵退出
            break

cap.release()
cv2.destroyAllWindows()

