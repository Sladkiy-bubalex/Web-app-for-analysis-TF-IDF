from models import User
from config import logger
from authentication import hash_password

from flask import request

from sqlalchemy.exc import SQLAlchemyError


def get_user_by_email(email: str) -> User | bool:
    """
    Функция для получения юзера из БД по email
    """
    try:
        user = (
            request.db_session.query(User).filter(User.email == email).first()
        )
        if user is None:
            return False

        return user

    except SQLAlchemyError as e:
        logger.error(f"Ошибка получения юзера из БД по email: {email}")
        raise e

def get_user_by_id(user_id: int) -> User | bool:
    """
    Функция для получения юзера из БД по id
    """
    try:
        user = request.db_session.get(User, user_id)
        if user is None:
            return False

        return user
    except SQLAlchemyError as e:
        logger.error(f"Ошибка получения юзера из БД по id: {user_id}")
        raise e

def update_user(user_id: int, email=None, password=None) -> User | bool:
    """
    Функция для обновления юзера в БД
    """
    try:
        user = get_user_by_id(user_id=user_id)
        if user is False:
            return False

        if email is not None:
            user.email = email
        if password is not None:
            user.password = hash_password(password=password)

        request.db_session.add(user)
        request.db_session.commit()

        return user
    except SQLAlchemyError as e:
        request.db_session.rollback()
        logger.error(f"Ошибка обновления юзера в БД по id: {user_id}")
        raise e

def add_user(email: str, password: str) -> User:
    """
    Функция для добавления юзера в БД
    """
    try:
        hash_pwd = hash_password(password=password)
        user = User(email=email, password=hash_pwd)
        request.db_session.add(user)
        request.db_session.commit()

        return user
    except SQLAlchemyError as e:
        request.db_session.rollback()
        logger.error(f"Ошибка добавления юзера в БД по email: {email}")
        raise e