
#include <Servo.h>

int relayPin = 7;  // Relay điều khiển khóa từ

void setup() {
  Serial.begin(9600);
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);  // Khóa đóng ban đầu
  Serial.println("Arduino ready");
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    if (command == '0') { // Người quen - MỞ KHÓA
      digitalWrite(relayPin, HIGH);
      Serial.println("UNLOCKED");
      
    } else if (command == '1') { // Xâm nhập - ĐÓNG KHÓA
      digitalWrite(relayPin, LOW);
      Serial.println("LOCKED");
    }
  }
}