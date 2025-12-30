import json
import os
from typing import Optional, Dict

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Store user_tokens.json in telegram_bot directory
STORAGE_FILE = os.path.join(BASE_DIR, 'user_tokens.json')

def load_storage() -> Dict[str, Dict]:
    """Load token storage from file"""
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_storage(data: Dict[str, Dict]):
    """Save token storage to file"""
    try:
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"Error saving storage: {e}")
        return False

def get_user_id_by_token(token: str) -> Optional[int]:
    """Get user ID by token"""
    storage = load_storage()
    if token in storage:
        return storage[token].get('user_id')
    return None

def set_user_token(user_id: int, token: str) -> bool:
    """Set token for a user"""
    storage = load_storage()
    storage[token] = {
        'user_id': user_id,
        'created_at': None  # Can add timestamp if needed
    }
    return save_storage(storage)

def get_token_by_user_id(user_id: int) -> Optional[str]:
    """Get token for a user ID"""
    storage = load_storage()
    for token, data in storage.items():
        if data.get('user_id') == user_id:
            return token
    return None

def remove_token(token: str) -> bool:
    """Remove a token"""
    storage = load_storage()
    if token in storage:
        del storage[token]
        return save_storage(storage)
    return False

def generate_token_for_user(user_id: int) -> str:
    """Generate a new token for a user"""
    import secrets
    import string
    
    # Generate a random token (16 characters)
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(16))
    
    # Save token for user
    set_user_token(user_id, token)
    return token

