import os

from dotenv import load_dotenv

load_dotenv()

# .env constants
ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", default="")
ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", default="")
SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", default="")
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", default="")
TELEGRAM_GROUP_ID: str = os.getenv("TELEGRAM_GROUP_ID", default="")

# common constants
PROJECT_MANAGEMENT_SYSTEM_API: str = "Project management system API"
