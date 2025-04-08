import secrets
import logging


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

SECRET_KEY = secrets.token_hex(32)
ALLOWED_EXTENSIONS = ["txt", "pdf", "docx"]
