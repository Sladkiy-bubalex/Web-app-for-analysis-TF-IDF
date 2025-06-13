import logging
import dotenv
import os
import nltk

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALLOWED_EXTENSIONS = ["txt", "pdf", "docx"]
APP_VERSION = "1.4.0"

# Скачать необходимые данные для работы с NLTK
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("punkt_tab")