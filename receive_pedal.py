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

            if line == "left_on":
                # 處理左踏板訊號，向上移動
                print("Left pedal pressed. Moving up.")
                pyautogui.press('up')  # 模擬向上鍵

            elif line == "right_on":
                # 處理右踏板訊號，檢查是否有下一行
                print("Right pedal pressed. Moving down or adding a new line.")

                # 模擬 Shift+End 選中當前行以判斷是否為最後一行
                pyautogui.hotkey('shift', 'end')  # 選中當前行
                pyautogui.hotkey('ctrl', 'c')    # 嘗試複製選中的內容

                # 根據複製結果判斷是否有下一行
                clipboard_content = pyautogui.paste()
                if clipboard_content.strip():  # 若複製內容非空，則移動到下一行
                    pyautogui.press('down')
                else:  # 若複製內容為空，則新增一行
                    pyautogui.press('enter')
                    print("Added a new line.")

except serial.SerialException as e:
    print(f"Error connecting to Arduino: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
