import logging
import dotenv
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALLOWED_EXTENSIONS = ["txt", "pdf", "docx"]
APP_VERSION = "1.2.0"
