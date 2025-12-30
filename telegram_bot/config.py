import os
from dotenv import load_dotenv

# Load environment variables from .env file
# telegram_bot/config.py -> project root = 1 level up
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'IOT_code', '.env')
load_dotenv(env_path)

class Config:
    """Configuration class for Telegram Bot"""
    
    # Telegram Bot Token from @BotFather
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Webhook server port (default: 5000)
    PORT = int(os.getenv('PORT', 5000))
    
    @staticmethod
    def validate():
        """Validate that all required configuration values are present"""
        if not Config.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required. Please set it in IOT_code/.env file or environment variables.")

