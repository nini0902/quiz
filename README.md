# 頭部偵測互動系統
使用者可透過點頭或抬頭來選擇或刪除選項。結果會即時儲存於文字檔中並使用 Notepad++ 開啟顯示。

---

## 功能簡介

- **頭部偵測**：使用 Mediapipe 偵測臉部動作。
- **選項選擇**：透過「低頭」記錄選項，並將結果加到文字檔中。
- **結果即時顯示**：以 Notepad++ 開啟文字檔，讓結果即時呈現。
- **單選題**：同一行，使用者更改答案會直接覆蓋(沒有抬頭刪除的功能)。
- **多選題**：當使用者抬頭時，從文字檔中刪除同一行。

---

## 使用指南
1. 安裝 Python 套件：
```bash
pip install opencv-python mediapipe
```
2. Notepad++：
從 [Notepad++ 官網](https://notepad-plus-plus.org/downloads/) 下載並安裝應用程式。

## 參數調整
1. ```feature_choose``` 調整左右參數
```python
# 判斷臉的方向
if angle > 103: #向左的參數
  face_direction = "left"
elif angle < 73: #向右的參數
  face_direction = "right"
else:
  face_direction = "center"
```
2. ```feature_nod_detection``` 調整低頭參數
```python
 # 判斷是否為低頭 ( > -53 視為低頭 )
if vertical_angle > -53: #低頭參數
  if start_selection_time is None:
    start_selection_time = time.time()
    selection_logged = False
  elif time.time() - start_selection_time > 1 and not selection_logged:
    if last_logged_selection != current_selection:
      with open("selection_results.txt", "w") as file:  # 清空並覆蓋寫入
        file.write(f"{options[current_selection]}")  # 不換行寫入
        file.flush()
      reopen_notepad("selection_results.txt")
      last_logged_selection = current_selection
      selection_logged = True
else:
   start_selection_time = None
   selection_logged = False
```
## 示範：單選題
![頭部控制系統示範](quiz/gif/test01.gif)
