const int nextButtonPin = A4;  // 下一題按鈕接到 A4
const int prevButtonPin = A5;  // 上一題按鈕接到 A5
int questionNumber = 1;        // 初始題號

void setup() {
  pinMode(nextButtonPin, INPUT_PULLUP); // 啟用內建上拉電阻
  pinMode(prevButtonPin, INPUT_PULLUP); // 啟用內建上拉電阻
  Serial.begin(9600);                  // 啟動序列監控
  //Serial.println("Start Quiz System");
  //displayQuestion();
}

void loop() {
  // 檢測下一題按鈕
  if (digitalRead(nextButtonPin) == LOW) {
    delay(1000); // 防止彈跳
    Serial.println("R");
    questionNumber++;          // 題號加 1
    //displayQuestion();         // 顯示新題號
  }

  // 檢測上一題按鈕
  if (digitalRead(prevButtonPin) == LOW) {
    delay(1000); // 防止彈跳
    if (questionNumber > 1) {  // 防止題號小於 1
      Serial.println("L");
      questionNumber--;
      //displayQuestion();       // 顯示新題號
    }
  }
}

// 顯示題號
void displayQuestion() {
  Serial.print("Current Question: ");
  Serial.println(questionNumber);
}
