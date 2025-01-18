import cv2
import mediapipe as mp
import math
import time
import subprocess

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# 設定選項
options = ["A", "B", "C", "D"]
current_selection = 2  # 初始選項 C

angle_threshold = 93  # 判斷選擇的角度閾值
selection_duration = 1  # 持續時間閾值 (秒)
move_delay = 0.8  # 左右選擇的停頓時間 (秒)

start_selection_time = None  # 初始化選擇計時器
last_move_time = time.time()  # 初始化移動計時器
selection_logged = False  # 控制低頭選項僅輸出一次

thickness = 6  # 框線的預設厚度

# 定義使用 Notepad++ 打開文件的函數
def reopen_notepad(file_path):
    # 使用 Notepad++ 打開文件
    subprocess.Popen(["C:\\Program Files\\Notepad++\\notepad++.exe", file_path])

# 設定全螢幕顯示
cap.set(cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

with mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        angle_status = "No"
        vertical_angle = None  # 初始化角度為 None
        face_direction = "center"  # 初始化方向

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(frame, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS)

                nose_tip = face_landmarks.landmark[1]
                left_eye = face_landmarks.landmark[33]
                right_eye = face_landmarks.landmark[263]

                # 計算角度
                eye_center_x = (left_eye.x + right_eye.x) / 2
                eye_center_y = (left_eye.y + right_eye.y) / 2
                dx = nose_tip.x - eye_center_x
                dy = nose_tip.y - eye_center_y
                vertical_angle = math.degrees(math.atan2(dy, dx))

                # 判斷臉的方向
                if vertical_angle > 103:
                    face_direction = "left"
                elif vertical_angle < 73:
                    face_direction = "right"
                else:
                    face_direction = "center"

                # 左右選項移動判斷
                if face_direction == "left" and time.time() - last_move_time > move_delay:
                    if current_selection > 0:  # 往左移動但不超出 A
                        current_selection -= 1
                        last_move_time = time.time()

                elif face_direction == "right" and time.time() - last_move_time > move_delay:
                    if current_selection < len(options) - 1:  # 往右移動但不超出 D
                        current_selection += 1
                        last_move_time = time.time()

                # 判斷是否角度小於閾值並持續足夠時間
                if vertical_angle is not None and vertical_angle < angle_threshold:
                    if start_selection_time is None:
                        start_selection_time = time.time()  # 開始計時
                        selection_logged = False  # 重置輸出狀態
                    elif time.time() - start_selection_time > selection_duration and not selection_logged:
                        # 記錄選擇到記事本
                        with open("selection_results.txt", "a") as file:
                            file.write(f"{options[current_selection]}\n")
                            file.flush()  # 強制刷新緩存
                        reopen_notepad("selection_results.txt")  # 使用 Notepad++ 重新打開
                        selection_logged = True  # 確保只輸出一次
                else:
                    start_selection_time = None  # 重置計時器
                    selection_logged = False  # 重置輸出狀態

        # 在畫面中劃分四個橫向區域並顯示 ABCD
        height, width, _ = frame.shape
        box_width = width // 4

        for i, option in enumerate(options):
            x1 = i * box_width
            x2 = (i + 1) * box_width
            color = (255, 255, 255)  # 預設白色

            if i == current_selection:
                color = (0, 0, 255)  # 當前選擇變為紅色

            # 畫出選項格子的框線
            cv2.rectangle(frame, (x1, 0), (x2, height), color, 2)
            # 顯示所有選項文字
            cv2.putText(frame, option, (x1 + box_width // 2 - 20, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 3)

        # 高亮目前選擇的框框
        x1 = current_selection * box_width
        x2 = (current_selection + 1) * box_width
        cv2.rectangle(frame, (x1, 0), (x2, height), (0, 0, 255), thickness)  # 粗框表示選擇

        # 在右上角顯示角度與狀態
        if vertical_angle is not None:
            cv2.putText(frame, f"Vertical Angle: {vertical_angle:.2f} degrees", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Angle Status: {'Yes' if start_selection_time else 'No'}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(frame, f"Face Direction: {face_direction}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow('Angle Based Selection', frame)

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
