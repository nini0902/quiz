import serial
import pyautogui

# 設定 Arduino 的序列埠
arduino_port = "COM3"  # 請根據實際的 Arduino COM 埠進行修改
baud_rate = 9600       # 與 Arduino 的 Serial.begin 設定一致

try:
    # 連接 Arduino
    ser = serial.Serial(arduino_port, baud_rate)
    print(f"Connected to Arduino on {arduino_port}")

    while True:
        # 從序列埠讀取訊息
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()  # 讀取並清除換行符號
            print(f"Received: {line}")

            # 根據訊號執行對應操作
            if line == "left_on":
                print("Left pedal pressed. Moving up.")
                pyautogui.press('up')  # 模擬向上鍵
            elif line == "right_on":
                print("Right pedal pressed. Moving down.")
                pyautogui.press('down')  # 模擬向下鍵
except serial.SerialException as e:
    print(f"Error connecting to Arduino: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
