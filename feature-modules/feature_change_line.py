import serial
from pynput.keyboard import Controller, Key
import pygetwindow as gw
import time

# 初始化序列埠
port = "COM3"  # 替換為你的 Arduino 序列埠名稱
baud_rate = 9600

# 初始化鍵盤控制器
keyboard = Controller()
total_line = 1
current_line = 1

def focus_window(window_title):
    """聚焦窗口"""
    windows = gw.getWindowsWithTitle(window_title)
    if windows:
        windows[0].activate()
        print(f"Focused on window: {window_title}")
    else:
        print(f"Window with title '{window_title}' not found.")

# 聚焦目標應用程式（如 Notepad++）
focus_window("Notepad++")

try:
    ser = serial.Serial(port, baud_rate)
    print(f"Connected to {port}")
    print("Waiting for data...")

    while True:
        if ser.in_waiting > 0:
            # 讀取資料並移除空白與換行符號
            data = ser.readline().decode().strip()

            if data == "L":  # 向上移動
                if(current_line > 1):
                    current_line -= 1
                    keyboard.press(Key.up)
                    keyboard.release(Key.up)
            elif data == "R":  # 向下移動
                if(current_line == total_line):
                    total_line += 1
                    keyboard.press(Key.enter)
                    keyboard.release(Key.enter)
                else:
                    keyboard.press(Key.down)
                    keyboard.release(Key.down)
                current_line += 1
            else:
                print(f"Unknown signal: {data}")

except Exception as e:
    print(f"Error: {e}")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()

