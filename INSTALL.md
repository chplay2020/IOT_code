# Hướng dẫn cài đặt

## Sửa lỗi "Cannot import 'setuptools.build_meta'"

Nếu gặp lỗi này khi cài đặt dependencies, làm theo các bước sau:

### Bước 1: Cập nhật pip, setuptools và wheel

```bash
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools wheel
```

### Bước 2: Cài đặt dependencies cho Telegram Bot

```bash
cd telegram_bot
pip install -r requirements.txt
```

### Bước 3: Cài đặt dependencies cho IoT System

```bash
cd ../IOT_code
pip install -r requirements.txt
```

## Cài đặt từng phần (nếu vẫn gặp lỗi)

### Telegram Bot

```bash
cd telegram_bot
pip install setuptools wheel
pip install python-telegram-bot flask python-dotenv
```

### IoT System

```bash
cd IOT_code
pip install setuptools wheel
pip install opencv-python opencv-contrib-python
pip install pyserial numpy python-dotenv requests
```

## Lưu ý với Python 3.14

Nếu bạn đang dùng Python 3.14 (phiên bản mới), một số package có thể chưa hỗ trợ đầy đủ. Có thể cần:

1. Sử dụng Python 3.11 hoặc 3.12 (khuyến nghị)
2. Hoặc cài đặt từng package và bỏ qua version cụ thể:

```bash
pip install python-telegram-bot flask python-dotenv --no-deps
pip install opencv-python opencv-contrib-python --no-deps
```

## Kiểm tra cài đặt

```bash
python -c "import telegram; print('Telegram OK')"
python -c "import cv2; print('OpenCV OK')"
python -c "import flask; print('Flask OK')"
```

