# Hướng dẫn sử dụng Telegram Bot

## Bước 1: Tìm và bắt đầu với Bot

1. Mở ứng dụng **Telegram** trên điện thoại hoặc máy tính
2. Tìm kiếm bot của bạn bằng cách:
   - Tìm theo tên bot bạn đã đặt khi tạo bot
   - Hoặc tìm theo username bot (ví dụ: `@your_bot_name`)
3. Nhấn vào bot để mở chat

## Bước 2: Bắt đầu sử dụng

Gửi lệnh sau để bắt đầu:

```
/start
```

Bot sẽ chào bạn và hiển thị hướng dẫn sử dụng.

## Bước 3: Lấy mã token để nhận thông báo

### Cách 1: Lấy token tự động (Khuyến nghị)

Gửi lệnh:

```
/gettoken
```

Bot sẽ tự động tạo và gửi cho bạn một mã token duy nhất (16 ký tự).

**Ví dụ token bạn nhận được:**
```
aB3cD5eF7gH9iJ1k
```

### Cách 2: Xem token hiện tại

Nếu bạn đã có token, gửi lệnh:

```
/mytoken
```

Bot sẽ hiển thị lại token hiện tại của bạn.

## Bước 4: Sử dụng token trong hệ thống IoT

1. **Copy mã token** mà bot vừa gửi cho bạn
2. **Mở file** `IOT_code/.env`
3. **Tìm dòng** `ALERT_TOKEN=`
4. **Điền token** vào sau dấu `=`:

```env
ALERT_TOKEN=aB3cD5eF7gH9iJ1k
```

5. **Lưu file** `.env`

## Bước 5: Xem hướng dẫn chi tiết

Nếu cần xem lại hướng dẫn, gửi lệnh:

```
/help
```

## Các lệnh Bot

| Lệnh | Mô tả |
|------|-------|
| `/start` | Bắt đầu sử dụng bot và xem hướng dẫn |
| `/gettoken` | Lấy mã token mới để nhận thông báo |
| `/mytoken` | Xem mã token hiện tại của bạn |
| `/help` | Xem hướng dẫn chi tiết |

## Cách hoạt động

1. ✅ Bạn lấy token từ bot bằng lệnh `/gettoken`
2. ✅ Cấu hình token vào file `IOT_code/.env`
3. ✅ Khi hệ thống IoT phát hiện đột nhập:
   - Hệ thống sẽ tự động gửi thông báo đến bot
   - Bot sẽ gửi thông báo kèm ảnh cho bạn qua Telegram
   - Bạn sẽ nhận được tin nhắn cảnh báo ngay lập tức

## Ví dụ tin nhắn cảnh báo

Khi có đột nhập, bạn sẽ nhận được tin nhắn như sau:

```
🚨 CẢNH BÁO ĐỘT NHẬP 🚨

Phát hiện có người đột nhập vào nhà!
Thời gian: 2024-12-30 14:30:25
Vui lòng kiểm tra ngay lập tức!
```

Kèm theo ảnh chụp được từ camera với khung đỏ đánh dấu khuôn mặt người đột nhập.

## Lưu ý quan trọng

⚠️ **Giữ bí mật token của bạn!**
- Token là thông tin nhạy cảm
- Không chia sẻ token với người khác
- Mỗi người dùng chỉ có một token duy nhất

⚠️ **Đảm bảo bot đang chạy**
- Bot phải đang chạy để nhận và gửi thông báo
- Kiểm tra bot có đang chạy bằng cách gửi tin nhắn bất kỳ

⚠️ **Token chỉ hoạt động khi:**
- Bot đang chạy
- Bạn đã gửi ít nhất một tin nhắn cho bot (để bot lưu thông tin của bạn)
- Token đã được cấu hình đúng trong file `.env`

## Xử lý sự cố

### Bot không trả lời

1. Kiểm tra bot có đang chạy không:
   ```bash
   # Kiểm tra health endpoint
   curl http://localhost:5000/health
   ```

2. Kiểm tra BOT_TOKEN trong file `IOT_code/.env` có đúng không

3. Khởi động lại bot nếu cần:
   ```bash
   python run_bot.py
   ```

### Không nhận được token

- Đảm bảo bạn đã gửi lệnh `/start` trước
- Kiểm tra bot có đang chạy không
- Thử gửi lại lệnh `/gettoken`

### Không nhận được thông báo đột nhập

1. Kiểm tra token trong `.env` có đúng với token bot gửi không
2. Kiểm tra hệ thống IoT có đang chạy không
3. Kiểm tra webhook URL có đúng không (mặc định: `http://localhost:5000/alert`)
4. Xem log của bot để biết lỗi cụ thể

## Test thủ công

Bạn có thể test tính năng gửi thông báo bằng script test:

```bash
cd IOT_code
python test_alert.py --token your_token_here
```

Hoặc test với ảnh:

```bash
python test_alert.py --token your_token_here --image path/to/image.jpg
```

## Liên hệ hỗ trợ

Nếu gặp vấn đề, kiểm tra:
- File `telegram_bot/README.md` - Hướng dẫn kỹ thuật
- File `IOT_code/README.md` - Hướng dẫn hệ thống IoT
- File `INSTALL.md` - Hướng dẫn cài đặt và xử lý lỗi

