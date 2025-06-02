import nltk
import pandas as pd
import PyPDF2
from flask import request
from typing import Tuple
from models import User, Sorted_Tfidf, LoginMetric
from config import ALLOWED_EXTENSIONS, logger
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from authentication import hash_password
from docx import Document
from sqlalchemy.exc import SQLAlchemyError


def check_extension_file(filename: str) -> bool: # Функция для проверки расширения
    try:
        return (
            "." in filename and
            filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        )
    except Exception as e:
        logger.error(f"Ошибка обработки названия файла: {filename}")
        return e


def get_user(email: str) -> User:
    try:
        user = (
            request.db_session.query(User).filter(User.email == email).first()
        )
        if user is None:
            return False

        return user

    except SQLAlchemyError as e:
        logger.error(f"Ошибка получения юзера из БД по email: {email}")
        return e


def add_data_tf_idf(name_file: str, text: str, user_id: int) -> Sorted_Tfidf:
    try:
        tf_idf_data = Sorted_Tfidf(
            name_file=name_file,
            data=text,
            user_id=user_id
        )
        request.db_session.add(tf_idf_data)
        request.db_session.commit()

        return tf_idf_data
    except SQLAlchemyError as e:
        logger.error(f"Ошибка добавления файла в БД: {name_file}")
        return e


def add_user(email: str, password: str) -> User:
    try:
        hash_pwd = hash_password(password=password)
        user = User(email=email, password=hash_pwd)
        request.db_session.add(user)
        request.db_session.commit()

        return user
    except SQLAlchemyError as e:
        logger.error(f"Ошибка добавления юзера в БД по email: {email}")
        return e


def get_file(file_id: int) -> Sorted_Tfidf:
    try:
        file = request.db_session.get(Sorted_Tfidf, file_id)
        if file is None:
            return False

        return file
    except SQLAlchemyError as e:
        logger.error(f"Ошибка получения файла из БД по id: {file_id}")
        return e


def pagination(
        data_frame: pd.DataFrame, page: int
) -> Tuple[pd.DataFrame, int]:
    per_page = 20
    total_items = len(data_frame)
    total_pages = (total_items + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    current_items = data_frame[start:end]

    return current_items, total_pages


def process_text(text: str) -> pd.DataFrame:

    nltk.download("punkt")
    nltk.download("stopwords")
    nltk.download("punkt_tab")

    # Токенизация и удаление стоп-слов
    word_tokens = word_tokenize(text)
    stop_words = set(stopwords.words("russian"))
    filtered_tokens = [word for word in word_tokens if word not in stop_words]

    # Получение слов и их TF-IDF значения
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([", ".join(filtered_tokens)])
    tfidf_scores = tfidf_matrix.toarray()[0]
    feature_names = vectorizer.get_feature_names_out()

    # Создание DataFrame для отображения
    df = pd.DataFrame(
        {
            "word": feature_names,
            "tf": [filtered_tokens.count(word) for word in feature_names],
            "idf": tfidf_scores,
        }
    )
    df_sorted = df.sort_values(by="idf", ascending=False)

    return df_sorted


def reading_file(file):
    file_extension = file.filename.rsplit(".", 1)[1].lower()
    try:
        if file_extension == "docx":
            doc = Document(file)
            text = [para.text for para in doc.paragraphs]
            return text

        elif file_extension == "txt":
            text = file.read().decode("utf-8")
            return text

        elif file_extension == "pdf":
            reader = PyPDF2.PdfReader(file)
            text = [page.extract_text() for page in reader.pages]
            return text
    except Exception as e:
        logger.error(f"Ошибка {e}")

def add_login_metric(user_id: int):
    try:
        login_metric = LoginMetric(user_id=user_id)
        request.db_session.add(login_metric)
        request.db_session.commit()
    except SQLAlchemyError as e:
        logger.error(f"Ошибка добавления метрики входа: {e}")
