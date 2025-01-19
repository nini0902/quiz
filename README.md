# 頭部偵測互動系統
使用者可透過點頭或抬頭來選擇或刪除選項。結果會即時儲存於文字檔中並使用 Notepad++ 開啟顯示。

---

## 功能簡介

- **頭部偵測**：使用 Mediapipe 偵測臉部動作。
- **選項選擇**：透過「低頭」記錄選項，並將結果加到文字檔中。
- **抬頭刪除**：當使用者抬頭時，從文字檔中刪除同一行(多選題)。
- **結果即時顯示**：以 Notepad++ 開啟文字檔，讓結果即時呈現。

---

## 安裝
1. 安裝 Python 套件：
```bash
pip install opencv-python mediapipe
```
2. Notepad++：
從 [Notepad++ 官網](https://notepad-plus-plus.org/downloads/) 下載並安裝應用程式。
