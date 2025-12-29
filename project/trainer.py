import cv2
import os
import numpy as np
from PIL import Image, ImageEnhance
import sys

# Cấu hình encoding cho Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Khởi tạo LBPH Face Recognizer với tham số tối ưu
# radius=2, neighbors=8, grid_x=8, grid_y=8 cho độ chính xác cao hơn
recognizer = cv2.face.LBPHFaceRecognizer_create(radius=2, neighbors=8, grid_x=8, grid_y=8)

# Load Haar Cascade để phát hiện khuôn mặt
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Đường dẫn đến thư mục dataset
dataset_path = 'dataset'

def augment_image(img_numpy):
    """
    Tăng cường dữ liệu bằng cách tạo các biến thể của ảnh
    """
    augmented = [img_numpy]  # Ảnh gốc
    
    # Lật ngang (mirror)
    flipped = cv2.flip(img_numpy, 1)
    augmented.append(flipped)
    
    # Điều chỉnh độ sáng
    bright = cv2.convertScaleAbs(img_numpy, alpha=1.1, beta=10)
    dark = cv2.convertScaleAbs(img_numpy, alpha=0.9, beta=-10)
    augmented.append(bright)
    augmented.append(dark)
    
    return augmented

def preprocess_face(face_img, target_size=(200, 200)):
    """
    Tiền xử lý khuôn mặt: resize, histogram equalization
    """
    # Resize về kích thước chuẩn
    face_resized = cv2.resize(face_img, target_size)
    
    # Histogram Equalization để cân bằng độ sáng
    face_equalized = cv2.equalizeHist(face_resized)
    
    # Gaussian blur nhẹ để giảm noise
    face_blurred = cv2.GaussianBlur(face_equalized, (5, 5), 0)
    
    return face_blurred

def get_images_and_labels(path):
    """
    Đọc tất cả ảnh từ dataset và trích xuất khuôn mặt
    
    Args:
        path: Đường dẫn đến thư mục dataset
        
    Returns:
        faces: Danh sách các ảnh khuôn mặt
        labels: Danh sách các label tương ứng
    """
    image_paths = []
    faces = []
    labels = []
    
    # Lấy danh sách các thư mục người (person_1, person_2, ...)
    person_dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    
    print(f"Tìm thấy {len(person_dirs)} người trong dataset")
    
    # Duyệt qua từng thư mục người
    for person_dir in person_dirs:
        # Lấy ID từ tên thư mục (person_1 -> 1, person_2 -> 2, ...)
        try:
            person_id = int(person_dir.split('_')[1])
        except:
            print(f"Bỏ qua thư mục: {person_dir}")
            continue
        
        person_path = os.path.join(path, person_dir)
        
        # Lấy tất cả file ảnh trong thư mục
        image_files = [f for f in os.listdir(person_path) if f.endswith(('.jpg', '.jpeg', '.png'))]
        print(f"Person {person_id}: {len(image_files)} ảnh")
        
        # Duyệt qua từng ảnh
        for image_file in image_files:
            image_path = os.path.join(person_path, image_file)
            
            try:
                # Đọc ảnh và chuyển sang grayscale
                pil_image = Image.open(image_path).convert('L')  # L = grayscale
                img_numpy = np.array(pil_image, 'uint8')
                
                # Phát hiện khuôn mặt với nhiều scale khác nhau
                detected_faces = face_cascade.detectMultiScale(
                    img_numpy, 
                    scaleFactor=1.1,  # Tăng độ nhạy
                    minNeighbors=4,    # Giảm để detect tốt hơn
                    minSize=(50, 50)   # Kích thước tối thiểu
                )
                
                # Lấy khuôn mặt đầu tiên (nếu có)
                for (x, y, w, h) in detected_faces:
                    # Trích xuất khuôn mặt
                    face_roi = img_numpy[y:y+h, x:x+w]
                    
                    # Tiền xử lý khuôn mặt
                    face_processed = preprocess_face(face_roi)
                    
                    # Thêm ảnh gốc đã xử lý
                    faces.append(face_processed)
                    labels.append(person_id)
                    
                    # Data augmentation - tạo thêm các biến thể
                    augmented_faces = augment_image(face_processed)
                    for aug_face in augmented_faces[1:]:  # Bỏ ảnh gốc (đã thêm rồi)
                        faces.append(aug_face)
                        labels.append(person_id)
                    
                    break  # Chỉ lấy khuôn mặt đầu tiên
                    
            except Exception as e:
                print(f"Lỗi khi xử lý ảnh {image_path}: {str(e)}")
                continue
    
    print(f"\nTổng cộng: {len(faces)} khuôn mặt được trích xuất (bao gồm augmentation)")
    print(f"Số ảnh gốc trung bình mỗi người: ~{len(faces) // (len(set(labels)) * 4) if len(set(labels)) > 0 else 0}")
    return faces, labels

# Main training process
if __name__ == "__main__":
    print("=" * 50)
    print("BẮT ĐẦU HUẤN LUYỆN MÔ HÌNH NHẬN DIỆN KHUÔN MẶT")
    print("=" * 50)
    print()
    
    # Kiểm tra thư mục dataset có tồn tại không
    if not os.path.exists(dataset_path):
        print(f"Lỗi: Không tìm thấy thư mục {dataset_path}")
        exit()
    
    # Lấy dữ liệu huấn luyện
    print("Đang đọc và xử lý ảnh từ dataset...")
    faces, labels = get_images_and_labels(dataset_path)
    
    if len(faces) == 0:
        print("Lỗi: Không tìm thấy khuôn mặt nào trong dataset")
        exit()
    
    # Huấn luyện model
    print("\nĐang huấn luyện mô hình...")
    recognizer.train(faces, np.array(labels))
    
    # Lưu model vào file trainer.yml
    output_file = 'trainer.yml'
    recognizer.save(output_file)
    
    print(f"\n✓ Hoàn thành! Mô hình đã được lưu vào: {output_file}")
    print(f"✓ Số lượng khuôn mặt đã huấn luyện: {len(faces)}")
    print(f"✓ Số lượng người: {len(set(labels))}")
    print("=" * 50)
