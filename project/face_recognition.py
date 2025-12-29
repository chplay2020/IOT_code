import cv2
import serial # Để gửi lệnh đến Arduino
import time
import sys
import numpy as np

# Cấu hình encoding cho Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Tham số nhận diện
CONFIDENCE_THRESHOLD = 85  # Ngưỡng confidence (càng thấp càng chặt) - Tăng lên để dễ nhận hơn
FACE_SIZE = (200, 200)     # Kích thước chuẩn hóa khuôn mặt
DEBUG_MODE = True          # Hiển thị tất cả confidence để debug

def preprocess_face(face_img, target_size=FACE_SIZE):
    """Tiền xử lý khuôn mặt giống như khi training"""
    face_resized = cv2.resize(face_img, target_size)
    face_equalized = cv2.equalizeHist(face_resized)
    face_blurred = cv2.GaussianBlur(face_equalized, (5, 5), 0)
    return face_blurred

recognizer = cv2.face.LBPHFaceRecognizer_create(radius=2, neighbors=8, grid_x=8, grid_y=8)
recognizer.read('trainer.yml') # Model đã train
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Kết nối Arduino - thay COM3 bằng port Arduino của bạn
try:
    ser = serial.Serial('COM3', 9600, timeout=1)
    time.sleep(2) # Chờ Arduino khởi động
    print("Đã kết nối với Arduino trên COM3")
except:
    print("CẢNH BÁO: Không thể kết nối Arduino. Kiểm tra port COM!")
    ser = None

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
        
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces với nhiều scale
    faces = face_cascade.detectMultiScale(
        gray, 
        scaleFactor=1.1, 
        minNeighbors=5,
        minSize=(50, 50)
    )
    
    for (x, y, w, h) in faces:
        # Trích xuất và tiền xử lý khuôn mặt
        face_roi = gray[y:y+h, x:x+w]
        face_processed = preprocess_face(face_roi)
        
        # Nhận diện
        id, confidence = recognizer.predict(face_processed)
        
        # DEBUG: Luôn hiển thị confidence
        if DEBUG_MODE:
            print(f"Detected: Person {id}, Confidence: {confidence:.2f}")
        
        # Hiển thị hình chữ nhật và thông tin
        if confidence < CONFIDENCE_THRESHOLD: # Nhận diện được (người quen)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            text = f"Person {id}"
            conf_text = f"Conf: {confidence:.1f}"
            cv2.putText(frame, text, (x, y-30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, conf_text, (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            print(f"✓ Authorized - Person {id} (confidence: {confidence:.2f})")
            if ser:
                ser.write(b'0') # Mở khóa
        else: # Không nhận diện (xâm nhập)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            text = "INTRUDER!"
            conf_text = f"Conf: {confidence:.1f}"
            cv2.putText(frame, text, (x, y-30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.putText(frame, conf_text, (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            print(f"✗ INTRUDER! (confidence: {confidence:.2f})")
            if ser:
                ser.write(b'1') # Đóng khóa + cảnh báo

    cv2.imshow('Face Recognition', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
if ser:
    ser.close()