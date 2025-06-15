import pandas as pd
import heapq
from collections import Counter, deque

from config import logger
from models import Document

from flask import request
from werkzeug.datastructures import FileStorage

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from docx import Document as Docx
from PyPDF2 import PdfReader


class Node:
    """
    Класс для представления узла дерева Хаффмана
    """
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        """
        Переопределение оператора < для сравнения узлов по частоте
        """
        return self.freq < other.freq


def huffman_tree(text: str) -> Node:
    """
    Функция для создания дерева Хаффмана
    """

    # Подсчет частоты символов и создание приоритетной очереди
    priority_queue = [Node(char, freq) for char, freq in Counter(text).items()]
    heapq.heapify(priority_queue)

    while len(priority_queue) > 1:
        left = heapq.heappop(priority_queue)
        right = heapq.heappop(priority_queue)

        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right

        heapq.heappush(priority_queue, merged)

    return priority_queue[0]


def huffman_code_table(huffman_tree: Node) -> dict[str, str]:
    """
    Функция для создания таблицы кодов Хаффмана

    Args:
        huffman_tree: Дерево Хаффмана

    Returns:
        dict[str, str]: Таблица кодов Хаффмана
    """

    code_table = {}
    queue = deque([(huffman_tree, "")])

    while queue:
        node, code = queue.popleft()

        if node.char is not None:
            code_table[node.char] = code
            continue

        if node.left:
            queue.append((node.left, code + "0"))
        if node.right:
            queue.append((node.right, code + "1"))

    return code_table


def huffman_encode(text: str) -> tuple[str, dict[str, str]]:
    """
    Функция для кодирования текста с помощью таблицы Хаффмана

    Args:
        text: Текст для кодирования

    Returns:
        tuple[str, dict[str, str]]:
        Кодированная строка и таблица кодов Хаффмана
    """
    tree = huffman_tree(text)
    code_table = huffman_code_table(tree)
    result = "".join(code_table[char] for char in text)
    return result, code_table


def process_text(text: str) -> pd.DataFrame:
    """
    Функция для обработки текста и вычисления TF-IDF
    """

    # Токенизация и удаление стоп-слов
    stop_words = set(stopwords.words("russian"))
    word_tokens = word_tokenize(text)
    filtered_tokens = ' '.join([
        word.lower() for word in word_tokens if (
            word.lower() not in stop_words and word.isalnum()
        )
    ])

    # Получение слов и их TF-IDF значения
    vectorizer = TfidfVectorizer()
    vectorizer.fit_transform([filtered_tokens])

    idf_values = vectorizer.idf_

    count_vectorizer = CountVectorizer()
    count_matrix = count_vectorizer.fit_transform([filtered_tokens])

    tf_scores = count_matrix.toarray()[0]
    feature_names = vectorizer.get_feature_names_out()

    # Создание DataFrame для отображения
    df = pd.DataFrame(
        {
            "word": feature_names,
            "tf": tf_scores,
            "idf": idf_values,
        }
    )
    df_sorted = df.sort_values(by="idf", ascending=False)

    return df_sorted


def calculate_tf_idf_for_document(
    document: str,
    collection: list[str]
) -> pd.DataFrame:
    """
    Вычисляет TF для документа и IDF
    для объединенного корпуса текстов из коллекции.

    Args:
        document: Текст документа (строка).
        collection: Список текстов в коллекции.

    Returns:
        DataFrame с 50 наибольшими TF и IDF или None,
        если входные данные некорректны.
    """
    stop_words = set(stopwords.words("russian"))

    # Предобработка документа
    processed_document = ' '.join([
        word.lower() for word in word_tokenize(document)
        if word.lower() not in stop_words and word.isalnum()
    ])

    if not processed_document:
        return None

    # Предобработка всех документов в коллекции
    processed_all_documents = [
        ' '.join([
            word.lower() for word in word_tokenize(text)
            if word.lower() not in stop_words and word.isalnum()
        ]) for text in collection
    ]

    if not processed_all_documents:
        return None

    vectorizer = TfidfVectorizer()

    # Вычисляем IDF для всех документов в коллекции
    vectorizer.fit(processed_all_documents)

    # Получаем IDF значения и названия признаков
    idf_values = vectorizer.idf_
    feature_names = vectorizer.get_feature_names_out()

    # Вычисляем TF для целевого документа
    tf_matrix = vectorizer.transform([processed_document])
    tf_scores = tf_matrix.toarray()[0]

    # Создаем DataFrame. Заполняем пропущенные значения TF нулями.
    result_df = pd.DataFrame({
        "word": feature_names,
        "idf": idf_values,
    })

    tf_series = pd.Series(tf_scores, index=feature_names)
    result_df['tf'] = result_df['word'].map(tf_series).fillna(0)

    # Фильтруем DataFrame, оставляя только слова из целевого документа
    filtered_df = result_df[result_df['tf'] > 0]

    # Сортируем DataFrame по IDF в порядке убывания
    filtered_df = filtered_df.sort_values(by="idf", ascending=False)

    # Возвращаем топ 50 слов
    return filtered_df.reset_index(drop=True).head(50)


def reading_file(file: FileStorage) -> str:
    """
    Функция для чтения файла
    """
    file_extension = file.filename.rsplit(".", 1)[1].lower()
    try:
        if file_extension == "docx":
            doc = Docx(file)
            text = [para.text for para in doc.paragraphs]
            return " ".join(text)

        elif file_extension == "txt":
            text = file.read().decode("utf-8")
            return text

        elif file_extension == "pdf":
            reader = PdfReader(file)
            text = [page.extract_text() for page in reader.pages]
            return " ".join(text)
    except Exception as e:
        logger.error(f"Ошибка чтения файла {file.filename}: {e}")
        raise e


def add_document(name_file: str, text: str, user_id: int) -> Document:
    """
    Функция для добавления документа в БД
    """
    try:
        document = Document(
            name_file=name_file,
            data=text,
            user_id=user_id
        )
        request.db_session.add(document)
        request.db_session.commit()

        return document

    except IntegrityError as e:
        request.db_session.rollback()
        logger.error(f"Файл уже существует: {name_file}")
        raise e
    except SQLAlchemyError as e:
        request.db_session.rollback()
        logger.error(f"Ошибка добавления файла в БД: {name_file}")
        raise e


def get_document_user_by_id(user_id: int, document_id: int) -> Document | None:
    """
    Функция для получения данных документа по id у пользователя
    """
    try:
        document = request.db_session.query(Document).filter(
            Document.id == document_id,
            Document.user_id == user_id
        ).first()
        if document is None:
            return None

        return document

    except SQLAlchemyError as e:
        logger.error(f"Ошибка получения документа: {e}")
        raise e


def update_document(
        user_id: int,
        document_id: int,
        name_file=None,
        new_text=None
) -> Document:
    """
    Функция для обновления данных документа
    """
    try:
        document = get_document_user_by_id(
            user_id=user_id,
            document_id=document_id
        )
        if document is None:
            return None

        document.name_file = name_file if name_file else document.name_file
        document.data = new_text if new_text else document.data

        request.db_session.add(document)
        request.db_session.commit()

        return document

    except SQLAlchemyError as e:
        request.db_session.rollback()
        logger.error(f"Ошибка обновления документа: {e}")
        raise e


def delete_document(user_id: int, document_id: int) -> None | bool:
    """
    Функция для удаления документа
    """
    try:
        document = get_document_user_by_id(
            user_id=user_id,
            document_id=document_id
        )
        if document is None:
            return None

        request.db_session.delete(document)
        request.db_session.commit()

        return True

    except SQLAlchemyError as e:
        request.db_session.rollback()
        logger.error(f"Ошибка удаления документа: {e}")
        raise e
