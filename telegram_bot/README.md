# Telegram Intruder Alert Bot

Bot Telegram để nhận thông báo cảnh báo đột nhập từ hệ thống IoT Face Recognition.

## Tính năng

- 🚨 Gửi thông báo cảnh báo đột nhập qua Telegram
- 📸 Gửi kèm ảnh (từ URL hoặc file upload)
- 🔑 Hệ thống token tự động - người dùng lấy token qua lệnh `/gettoken`
- 🤖 Bot tự động lưu thông tin người dùng khi họ nhắn tin
- 🔗 Webhook endpoint để tích hợp với hệ thống bảo mật

## Cài đặt

### 1. Cập nhật pip và build tools (quan trọng!)

```bash
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools wheel
```

### 2. Cài đặt dependencies

```bash
cd telegram_bot
pip install -r requirements.txt
```

**Lưu ý:** Nếu gặp lỗi "Cannot import 'setuptools.build_meta'", xem file `INSTALL.md` ở thư mục gốc.

### 2. Cấu hình

Đảm bảo file `IOT_code/.env` đã được cấu hình với:

```env
BOT_TOKEN=your_bot_token_here
PORT=5000
```

### 3. Chạy bot

Từ thư mục gốc của project:

```bash
python run_bot.py
```

Hoặc từ thư mục telegram_bot:

```bash
cd telegram_bot
python bot.py
```

## Sử dụng Bot

### Các lệnh

- `/start` - Bắt đầu sử dụng bot
- `/gettoken` - Lấy mã token để nhận thông báo
- `/mytoken` - Xem mã token hiện tại của bạn
- `/help` - Xem hướng dẫn chi tiết

### Cách lấy token

1. Mở Telegram và tìm bot của bạn
2. Gửi lệnh `/start` để bắt đầu
3. Gửi lệnh `/gettoken` để lấy mã token
4. Copy mã token và sử dụng trong hệ thống IoT

**Xem hướng dẫn chi tiết trong file `HUONG_DAN_SU_DUNG_BOT.md` ở thư mục gốc.**

## Webhook API

### Endpoint: `/alert`

Gửi thông báo đột nhập đến user có token tương ứng.

**POST Request với JSON:**
```json
{
    "token": "user_token_here",
    "image_url": "https://example.com/image.jpg"
}
```

**POST Request với Form Data:**
```
token: user_token_here
image: [file upload]
```

**Response:**
```json
{
    "status": "success",
    "message": "Alert sent successfully",
    "timestamp": "2024-01-01T12:00:00"
}
```

## License

MIT

