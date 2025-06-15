import os
import dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


dotenv.load_dotenv()  # Загрузка переменных окружения

DSN = (
    f"postgresql://{os.getenv("POSTGRES_USER")}:"
    f"{os.getenv("POSTGRES_PASSWORD")}"
    f"@postgres:5432/{os.getenv("POSTGRES_DB")}"
)
engine = create_engine(DSN)
Session = sessionmaker(bind=engine)
