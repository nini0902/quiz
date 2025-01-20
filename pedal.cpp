const int leftPedal = 2;  // 左踏板接數位腳位 2
const int rightPedal = 3; // 右踏板接數位腳位 3

void setup() {
  pinMode(leftPedal, INPUT_PULLUP);  // 使用內部上拉電阻
  pinMode(rightPedal, INPUT_PULLUP);
  Serial.begin(9600);  // 初始化序列通訊，波特率設為 9600
}

void loop() {
  if (digitalRead(leftPedal) == LOW) {
    Serial.println("left_on");
    delay(200); // 防止按鍵彈跳
  }

  if (digitalRead(rightPedal) == LOW) {
    Serial.println("right_on");
    delay(200); // 防止按鍵彈跳
  }
}
