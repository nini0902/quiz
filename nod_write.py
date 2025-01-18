import cv2
import mediapipe as mp
import math
import time
import subprocess

# 初始化 Mediapipe 的 Face Mesh 模組
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# 初始化鏡頭
cap = cv2.VideoCapture(0)

# 設定選項
options = ["A", "B", "C", "D"]
current_selection = 2  # 初始選項 C
last_move_time = time.time()
move_delay = 0.8  # 停頓時間 (秒)

# 記錄低頭的狀態
start_selection_time = None
selection_logged = False
last_logged_selection = None

# 預設臉部方向
face_direction = "center"

# 定義使用 Notepad++ 打開文件的函數
def reopen_notepad(file_path):
    subprocess.Popen(["C:\\Program Files\\Notepad++\\notepad++.exe", file_path])

# 初始化 Mediapipe Face Mesh
with mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 翻轉畫面讓操作更直覺
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 偵測人臉
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # 繪製人臉網格
                mp_drawing.draw_landmarks(frame, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS)

                # 取得關鍵點位置
                left_eye = face_landmarks.landmark[33]  # 左眼中心
                right_eye = face_landmarks.landmark[263]  # 右眼中心
                nose_tip = face_landmarks.landmark[1]  # 鼻尖
                chin = face_landmarks.landmark[152]  # 下巴

                # 計算臉部偏轉角度
                eye_midpoint_x = (left_eye.x + right_eye.x) / 2
                eye_midpoint_y = (left_eye.y + right_eye.y) / 2

                dx = nose_tip.x - eye_midpoint_x
                dy = nose_tip.y - eye_midpoint_y

                angle = math.degrees(math.atan2(dy, dx))

                # 判斷臉的方向
                if angle > 103:
                    face_direction = "left"
                elif angle < 73:
                    face_direction = "right"
                else:
                    face_direction = "center"

                # 根據方向和時間控制選擇
                if face_direction == "left" and time.time() - last_move_time > move_delay:
                    if current_selection > 0:  # 往左移動但不超出 A
                        current_selection -= 1
                        last_move_time = time.time()

                elif face_direction == "right" and time.time() - last_move_time > move_delay:
                    if current_selection < len(options) - 1:  # 往右移動但不超出 D
                        current_selection += 1
                        last_move_time = time.time()

                # 計算鼻尖與下巴的垂直角度
                dx_chin = nose_tip.x - chin.x
                dy_chin = nose_tip.y - chin.y
                dz_chin = nose_tip.z - chin.z  # 深度座標
                vertical_angle = math.degrees(math.atan2(dy_chin, math.sqrt(dx_chin**2 + dz_chin**2)))

                # 判斷是否為低頭 ( > -50 視為低頭 )
                if vertical_angle > -53:
                    if start_selection_time is None:
                        start_selection_time = time.time()
                        selection_logged = False
                    elif time.time() - start_selection_time > 1 and not selection_logged:
                        if last_logged_selection != current_selection:
                            with open("selection_results.txt", "a") as file:
                                file.write(f"{options[current_selection]}")  # 不換行寫入
                                file.flush()
                            reopen_notepad("selection_results.txt")
                            last_logged_selection = current_selection
                            selection_logged = True
                else:
                    start_selection_time = None
                    selection_logged = False

                # 顯示垂直角度
                cv2.putText(frame, f"Vertical Angle: {vertical_angle:.2f} degrees", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 在畫面中繪製 ABCD 四個格子
        height, width, _ = frame.shape
        box_width = width // 4

        for i, option in enumerate(options):
            x1 = i * box_width
            x2 = (i + 1) * box_width
            color = (255, 255, 255)  # 預設白色

            # 畫出選項格子的框線
            cv2.rectangle(frame, (x1, 0), (x2, height), color, 2)
            # 顯示選項文字
            text_color = (0, 0, 255) if i == current_selection else (255, 255, 255)
            cv2.putText(frame, option, (x1 + box_width // 2 - 20, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)

        # 高亮目前選擇的框框
        x1 = current_selection * box_width
        x2 = (current_selection + 1) * box_width
        cv2.rectangle(frame, (x1, 0), (x2, height), (0, 0, 255), 6)  # 粗框表示選擇

        # 顯示畫面
        cv2.imshow('Quiz System with Head Detection', frame)

        if cv2.waitKey(5) & 0xFF == 27:  # 按下 Esc 離開
            break

cap.release()
cv2.destroyAllWindows()

