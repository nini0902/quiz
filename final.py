import serial
from pynput.keyboard import Controller, Key
import pygetwindow as gw
import cv2
import mediapipe as mp
import math
import time

# --------------------------
#        SERIAL SETUP
# --------------------------
port = "COM3"  # Replace with your Arduino serial port (e.g., COM3, /dev/ttyACM0)
baud_rate = 9600

# Initialize keyboard controller
keyboard = Controller()
total_line = 1
current_line = 1

def focus_window(window_title):
    """Focus a window by its title."""
    windows = gw.getWindowsWithTitle(window_title)
    if windows:
        windows[0].activate()
        print(f"Focused on window: {window_title}")
    else:
        print(f"Window with title '{window_title}' not found.")

# Try focusing on Notepad++ at the start (adjust the title if needed).
focus_window("Notepad++")

# --------------------------
#   MEDIAPIPE SETUP
# --------------------------
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Open webcam
cap = cv2.VideoCapture(0)

# Quiz options
options = ["A", "B", "C", "D"]
current_selection = 2  # Initial selection: C
last_move_time = time.time()
move_delay = 0.8  # Delay for left/right head movements

# Track whether we have already typed after tilting head down
is_head_down = False
# Track when head-down first detected
head_down_start_time = None

# Track face direction
face_direction = "center"

try:
    # Open the serial port for Arduino
    ser = serial.Serial(port, baud_rate)
    print(f"Connected to {port}")
    print("Waiting for data...")

    # Initialize Mediapipe Face Mesh
    with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # ----------------------------------------------------
            # 1. CHECK ARDUINO INPUT (non-blocking)
            # ----------------------------------------------------
            if ser.in_waiting > 0:
                data = ser.readline().decode().strip()
                if data == "L":   # Move cursor up
                    if current_line > 1:
                        current_line -= 1
                        keyboard.press(Key.up)
                        keyboard.release(Key.up)
                    print(f"Movement: L -> current_line={current_line}, total_line={total_line}")

                elif data == "R":  # Move cursor down (and possibly create new line)
                    if current_line == total_line:
                        total_line += 1
                        # Press Enter
                        keyboard.press(Key.enter)
                        keyboard.release(Key.enter)
                        # Press Ctrl+S (save)
                        keyboard.press(Key.ctrl)
                        keyboard.press('s')
                        keyboard.release('s')
                        keyboard.release(Key.ctrl)
                    else:
                        keyboard.press(Key.down)
                        keyboard.release(Key.down)
                    current_line += 1
                    print(f"Movement: R -> current_line={current_line}, total_line={total_line}")

                else:
                    print(f"Unknown signal: {data}")

            # ----------------------------------------------------
            # 2. MEDIAPIPE FACE DETECTION & HEAD ORIENTATION
            # ----------------------------------------------------
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    # Draw face mesh on the frame
                    mp_drawing.draw_landmarks(
                        frame,
                        face_landmarks,
                        mp_face_mesh.FACEMESH_CONTOURS
                    )

                    # Key landmarks
                    left_eye = face_landmarks.landmark[33]    # Left eye center
                    right_eye = face_landmarks.landmark[263]  # Right eye center
                    nose_tip = face_landmarks.landmark[1]     # Nose tip
                    chin = face_landmarks.landmark[152]       # Chin

                    # Calculate angle for left/right tilt
                    eye_midpoint_x = (left_eye.x + right_eye.x) / 2
                    eye_midpoint_y = (left_eye.y + right_eye.y) / 2
                    dx = nose_tip.x - eye_midpoint_x
                    dy = nose_tip.y - eye_midpoint_y
                    angle = math.degrees(math.atan2(dy, dx))

                    # Decide face direction (left/right)
                    if angle > 103:
                        face_direction = "left"
                    elif angle < 73:
                        face_direction = "right"
                    else:
                        face_direction = "center"

                    # Move selection left/right with delay
                    if face_direction == "left" and time.time() - last_move_time > move_delay:
                        if current_selection > 0:
                            current_selection -= 1
                            last_move_time = time.time()

                    elif face_direction == "right" and time.time() - last_move_time > move_delay:
                        if current_selection < len(options) - 1:
                            current_selection += 1
                            last_move_time = time.time()

                    # Calculate vertical angle (nose_tip -> chin)
                    dx_chin = nose_tip.x - chin.x
                    dy_chin = nose_tip.y - chin.y
                    dz_chin = nose_tip.z - chin.z
                    vertical_angle = math.degrees(
                        math.atan2(dy_chin, math.sqrt(dx_chin**2 + dz_chin**2))
                    )

                    # If head is tilted down for >1s, type the selected option
                    if vertical_angle > -60:
                        if head_down_start_time is None:
                            head_down_start_time = time.time()

                        if not is_head_down and (time.time() - head_down_start_time > 1.0):
                            # Type the option at the current cursor position
                            keyboard.type(options[current_selection])
                            is_head_down = True
                    else:
                        head_down_start_time = None
                        is_head_down = False

                    # Show vertical angle on the frame
                    cv2.putText(
                        frame,
                        f"Vertical Angle: {vertical_angle:.2f} deg",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )

            # ----------------------------------------------------
            # 3. DRAW THE ABCD BOXES
            # ----------------------------------------------------
            height, width, _ = frame.shape
            box_width = width // 4

            for i, option in enumerate(options):
                x1 = i * box_width
                x2 = (i + 1) * box_width
                color = (255, 255, 255)
                
                # Draw each rectangle
                cv2.rectangle(frame, (x1, 0), (x2, height), color, 2)
                
                # Draw option text
                text_color = (0, 0, 255) if i == current_selection else (255, 255, 255)
                cv2.putText(
                    frame,
                    option,
                    (x1 + box_width // 2 - 20, height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    text_color,
                    2
                )

            # Highlight the currently selected box
            x1 = current_selection * box_width
            x2 = (current_selection + 1) * box_width
            cv2.rectangle(frame, (x1, 0), (x2, height), (0, 0, 255), 6)

            # ----------------------------------------------------
            # 4. SHOW THE FRAME
            # ----------------------------------------------------
            cv2.imshow("Quiz System with Head Detection", frame)

            # Press ESC to exit
            if cv2.waitKey(5) & 0xFF == 27:
                break

except Exception as e:
    print(f"Error: {e}")

finally:
    # Clean up
    if 'ser' in locals() and ser.is_open:
        ser.close()
    cap.release()
    cv2.destroyAllWindows()

