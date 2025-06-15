from models import LoginMetric
from config import logger

from flask import request

from sqlalchemy.exc import SQLAlchemyError


def add_login_metric(user_id: int):
    """
    Функция для добавления метрики входа
    """
    try:
        login_metric = LoginMetric(user_id=user_id)
        request.db_session.add(login_metric)
        request.db_session.commit()
    except SQLAlchemyError as e:
        request.db_session.rollback()
        logger.error(f"Ошибка добавления метрики входа: {e}")
