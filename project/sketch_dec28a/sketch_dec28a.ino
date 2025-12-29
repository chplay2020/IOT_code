#include <Servo.h>

Servo panServo; // Nếu dùng tracking
Servo tiltServo;
int buzzerPin = 8;
int ledPin = 13;

void setup() {
  Serial.begin(9600);
  pinMode(buzzerPin, OUTPUT);
  pinMode(ledPin, OUTPUT);
  panServo.attach(9);
  tiltServo.attach(10);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
      if (command == '1') { // Cảnh báo xâm nhập
        digitalWrite(buzzerPin, HIGH);
        digitalWrite(ledPin, HIGH);
        delay(1000); // Báo động 1 giây
        digitalWrite(buzzerPin, LOW);
        digitalWrite(ledPin, LOW);
      } else if (command == '+') { // Tracking ví dụ: pan right
        panServo.write(panServo.read() + 1);
      } // Thêm lệnh khác cho tracking
    }
}