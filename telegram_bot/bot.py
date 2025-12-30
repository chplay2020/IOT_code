import logging
import asyncio
from datetime import datetime
from io import BytesIO
from flask import Flask, request, jsonify
from telegram import Bot
from telegram.error import TelegramError
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from threading import Thread
from telegram_bot import config
from telegram_bot import storage

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Validate configuration
try:
    config.Config.validate()
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    exit(1)

# Initialize Flask app
app = Flask(__name__)

# Global bot instance (will be initialized in async context)
bot_instance = None
application = None

def init_telegram_bot():
    """Initialize Telegram bot application"""
    global bot_instance, application
    bot_instance = Bot(token=config.Config.BOT_TOKEN)
    application = Application.builder().token(config.Config.BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("gettoken", get_token_command))
    application.add_handler(CommandHandler("mytoken", my_token_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Telegram bot handlers initialized")

async def start_command(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    
    welcome_message = f"""Xin chào {username}! 👋

Tôi là bot cảnh báo đột nhập. Tôi sẽ gửi thông báo cho bạn khi phát hiện có người đột nhập.

📋 Các lệnh có sẵn:
/gettoken - Lấy mã token để nhận thông báo
/mytoken - Xem mã token hiện tại của bạn
/help - Xem hướng dẫn chi tiết

💡 Cách sử dụng:
1. Sử dụng lệnh /gettoken để lấy mã token của bạn
2. Sử dụng mã token này trong hệ thống bảo mật của bạn
3. Khi có đột nhập, hệ thống sẽ gửi thông báo đến bot và bot sẽ thông báo cho bạn"""
    
    await update.message.reply_text(welcome_message)
    logger.info(f"User {user_id} ({username}) started the bot")

async def get_token_command(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gettoken command - Generate new token for user"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    
    # Check if user already has a token
    existing_token = storage.get_token_by_user_id(user_id)
    
    if existing_token:
        await update.message.reply_text(
            f"📝 Bạn đã có mã token:\n\n"
            f"`{existing_token}`\n\n"
            f"💡 Sử dụng mã token này trong hệ thống bảo mật của bạn.\n\n"
            f"🔄 Nếu muốn tạo token mới, vui lòng liên hệ admin.",
            parse_mode='Markdown'
        )
        logger.info(f"User {user_id} ({username}) requested token (already exists): {existing_token}")
    else:
        # Generate new token
        new_token = storage.generate_token_for_user(user_id)
        await update.message.reply_text(
            f"✅ Đã tạo mã token thành công!\n\n"
            f"📝 Mã token của bạn:\n"
            f"`{new_token}`\n\n"
            f"💡 Sử dụng mã token này trong hệ thống bảo mật của bạn để nhận thông báo.\n\n"
            f"⚠️ Lưu ý: Giữ bí mật mã token này!",
            parse_mode='Markdown'
        )
        logger.info(f"User {user_id} ({username}) generated new token: {new_token}")

async def my_token_command(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mytoken command"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    
    token = storage.get_token_by_user_id(user_id)
    
    if token:
        await update.message.reply_text(
            f"📝 Mã token hiện tại của bạn:\n\n"
            f"`{token}`\n\n"
            f"💡 Sử dụng mã token này trong hệ thống bảo mật của bạn.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ Bạn chưa có mã token.\n\n"
            "Sử dụng lệnh /gettoken để lấy mã token của bạn."
        )

async def help_command(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """📖 HƯỚNG DẪN SỬ DỤNG BOT

🤖 Bot cảnh báo đột nhập sẽ gửi thông báo cho bạn khi phát hiện có người đột nhập.

📋 Các lệnh:
/gettoken - Lấy mã token để nhận thông báo
/mytoken - Xem mã token hiện tại của bạn
/help - Hiển thị hướng dẫn này

💡 Cách sử dụng:
1. Gửi lệnh /gettoken để lấy mã token
2. Copy mã token và cấu hình vào hệ thống bảo mật
3. Khi có đột nhập, bạn sẽ nhận được thông báo kèm ảnh

⚠️ Lưu ý:
- Giữ bí mật mã token của bạn
- Mỗi người dùng chỉ có một mã token
- Thông báo sẽ được gửi kèm ảnh khi phát hiện đột nhập"""
    
    await update.message.reply_text(help_text)

async def handle_message(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    message_text = update.message.text
    
    # Just acknowledge the message
    await update.message.reply_text(
        f"Xin chào {username}! 👋\n\n"
        f"Tôi đã nhận tin nhắn của bạn. Sử dụng /help để xem hướng dẫn."
    )
    logger.info(f"Received message from user {user_id} ({username}): {message_text}")

def send_intruder_alert(token: str, image_url: str = None, image_file=None):
    """Send intruder alert message and image to user by token"""
    try:
        # Get user ID by token
        user_id = storage.get_user_id_by_token(token)
        
        if not user_id:
            logger.warning(f"Token not found: {token}")
            return False, f"Token không hợp lệ hoặc chưa được đăng ký"
        
        # Format current timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create alert message
        message = f"""🚨 CẢNH BÁO ĐỘT NHẬP 🚨

Phát hiện có người đột nhập vào nhà!
Thời gian: {current_time}
Vui lòng kiểm tra ngay lập tức!"""
        
        # Send message and image using asyncio.run for proper event loop handling
        try:
            async def send_message_async():
                if image_file:
                    # Send photo from file
                    image_file.seek(0)  # Reset file pointer
                    image_bytes = BytesIO(image_file.read())
                    image_bytes.name = image_file.filename or 'image.jpg'
                    await bot_instance.send_photo(
                        chat_id=user_id,
                        photo=image_bytes,
                        caption=message
                    )
                elif image_url:
                    # Send photo with caption from URL
                    await bot_instance.send_photo(
                        chat_id=user_id,
                        photo=image_url,
                        caption=message
                    )
                else:
                    # Send text message only
                    await bot_instance.send_message(
                        chat_id=user_id,
                        text=message
                    )
            
            # Use asyncio.run for proper event loop management
            asyncio.run(send_message_async())
            
            logger.info(f"Intruder alert sent successfully to user {user_id} with token {token}")
            return True, "Alert sent successfully"
        except RuntimeError as e:
            # If event loop is already running, use a different approach
            if "Event loop is running" in str(e) or "Event loop is closed" in str(e):
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    if image_file:
                        image_file.seek(0)
                        image_bytes = BytesIO(image_file.read())
                        image_bytes.name = image_file.filename or 'image.jpg'
                        loop.run_until_complete(
                            bot_instance.send_photo(chat_id=user_id, photo=image_bytes, caption=message)
                        )
                    elif image_url:
                        loop.run_until_complete(
                            bot_instance.send_photo(chat_id=user_id, photo=image_url, caption=message)
                        )
                    else:
                        loop.run_until_complete(
                            bot_instance.send_message(chat_id=user_id, text=message)
                        )
                    logger.info(f"Intruder alert sent successfully to user {user_id} with token {token}")
                    return True, "Alert sent successfully"
                except Exception as inner_e:
                    error_msg = f"Failed to send alert: {str(inner_e)}"
                    logger.error(error_msg)
                    return False, error_msg
            else:
                raise
        
    except TelegramError as e:
        error_msg = f"Failed to send alert: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

@app.route('/alert', methods=['POST'])
def alert_endpoint():
    """Webhook endpoint to trigger intruder alert"""
    try:
        # Check if request has files (multipart/form-data)
        image_file = None
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename == '':
                image_file = None
        
        # Get token and image_url from JSON or form data
        if request.is_json:
            data = request.get_json()
            token = data.get('token')
            image_url = data.get('image_url')
        else:
            token = request.form.get('token')
            image_url = request.form.get('image_url')
        
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Token is required',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        success, message = send_intruder_alert(token, image_url, image_file)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': message,
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': message,
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"Error in alert endpoint: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"Internal server error: {str(e)}",
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Telegram Intruder Alert Bot',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        'service': 'Telegram Intruder Alert Bot',
        'endpoints': {
            'POST /alert': 'Trigger intruder alert notification (requires: token, optional: image_url)',
            'GET /health': 'Health check endpoint'
        },
        'example_request_json': {
            'token': 'your_token_here',
            'image_url': 'https://example.com/image.jpg'
        },
        'example_request_form': {
            'token': 'your_token_here',
            'image': 'file upload (multipart/form-data)'
        }
    }), 200

def run_telegram_bot():
    """Run Telegram bot in async context"""
    init_telegram_bot()
    try:
        application.run_polling(allowed_updates=["message", "callback_query"], drop_pending_updates=True)
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        raise

def main():
    """Main function to run the bot"""
    logger.info("Starting Telegram Intruder Alert Bot...")
    logger.info(f"Webhook server running on port: {config.Config.PORT}")
    
    # Start Telegram bot in separate thread
    bot_thread = Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    
    # Run Flask webhook server
    app.run(
        host='0.0.0.0',
        port=config.Config.PORT,
        debug=False
    )

if __name__ == '__main__':
    main()

