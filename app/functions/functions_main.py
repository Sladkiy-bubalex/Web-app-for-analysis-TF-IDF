import pandas as pd
from typing import Tuple
from config import ALLOWED_EXTENSIONS, logger


def check_extension_file(filename: str) -> bool: 
    """
    Функция для проверки расширения
    """
    try:
        return (
            "." in filename and
            filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        )
    except Exception as e:
        logger.error(f"Ошибка обработки названия файла: {filename}")
        raise e

def pagination(
        data_frame: pd.DataFrame, page: int
) -> Tuple[pd.DataFrame, int]:
    """
    Функция для пагинации
    """
    per_page = 20
    total_items = len(data_frame)
    total_pages = (total_items + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    current_items = data_frame[start:end]

    return current_items, total_pages
