import serial
import pyautogui
import time

# Arduino 序列埠設定
SERIAL_PORT = "COM3"  # 替換為你的 Arduino 連接埠
BAUD_RATE = 9600      # 與 Arduino 設定一致

# 去抖延遲
DEBOUNCE_DELAY = 0.2  # 200 毫秒

# 上次觸發的時間
last_trigger_time = 0

# 處理 Arduino 訊息
def process_message(message):
    global last_trigger_time
    current_time = time.time()

    # 防止抖動
    if current_time - last_trigger_time < DEBOUNCE_DELAY:
        return

    if message == "left_on":
        pyautogui.press("up")  # 向上移動一行
        print("向上一行")
    elif message == "right_on":
        if has_next_line():
            pyautogui.press("down")  # 向下移動一行
            print("向下一行")
        else:
            pyautogui.press("enter")  # 新增一行
            print("新增一行並移動")
    last_trigger_time = current_time

# 檢查是否有下一行（模擬方法，可擴展為檔案檢查邏輯）
def has_next_line():
    # TODO: 根據實際需求檢查 Notepad++ 是否有下一行
    # 暫時假設永遠可以新增行
    return False

def main():
    print(f"連接到 Arduino: {SERIAL_PORT}")

    # 初始化串列連接
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        while True:
            # 檢查是否有訊息
            if ser.in_waiting > 0:
                message = ser.readline().decode("utf-8").strip()  # 讀取 Arduino 訊息
                print(f"接收到訊息: {message}")
                process_message(message)

            time.sleep(0.1)  # 減少 CPU 負擔

if __name__ == "__main__":
    main()
