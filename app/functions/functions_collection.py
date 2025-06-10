from ..models import Collection, DocumentCollectionAssociation
from ..config import logger
from flask import request
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


def get_collection_user_by_id(user_id: int, collection_id: int) -> Collection | None:
    """
    Функция для получения коллекции по id у пользователя
    """
    try:
        collection = request.db_session.query(Collection).filter(
            Collection.id == collection_id,
            Collection.user_id == user_id
        ).first()
        if collection is None:
            return None

        return collection

    except SQLAlchemyError as e:
        logger.error(f"Ошибка получения коллекции: {e}")
        raise e

def add_document_to_collection(collection_id: int, document_id: int) -> None:
    """
    Функция для добавления документа в коллекцию
    """
    try:
        document_collection = DocumentCollectionAssociation(
            collection_id=collection_id,
            document_id=document_id
        )

        request.db_session.add(document_collection)
        request.db_session.commit()

    except SQLAlchemyError as e:
        request.db_session.rollback()
        logger.error(f"Ошибка добавления документа в коллекцию: {e}")
        raise e

def add_collection(user_id: int, collection_id: int) -> Collection:
    """
    Функция для добавления коллекции в БД
    """
    try:
        collection = Collection(
            user_id=user_id,
            collection_id=collection_id
        )
        request.db_session.add(collection)
        request.db_session.commit()

        return collection

    except IntegrityError as e:
        request.db_session.rollback()
        logger.error(f"Коллекция с именем {collection_id} уже существует")
        raise e
    except SQLAlchemyError as e:
        request.db_session.rollback()
        logger.error(f"Ошибка добавления коллекции в БД: {collection_id}")
        raise e

def delete_document_from_collection(collection_id: int, document_id: int) -> bool:
    """
    Функция для удаления документа из коллекции
    """
    try:
        document_collection = DocumentCollectionAssociation(
            collection_id=collection_id,
            document_id=document_id
        )

        request.db_session.delete(document_collection)
        request.db_session.commit()

        return True

    except SQLAlchemyError as e:
        request.db_session.rollback()
        logger.error(f"Ошибка удаления документа из коллекции: {e}")
        raise e

def delete_collection(user_id: int, collection_id: int) -> bool:
    """
    Функция для удаления коллекции
    """
    try:
        collection = get_collection_user_by_id(user_id=user_id, collection_id=collection_id)
        if collection is None:
            return None

        request.db_session.delete(collection)
        request.db_session.commit()

        return True

    except SQLAlchemyError as e:
        request.db_session.rollback()
        logger.error(f"Ошибка удаления коллекции: {e}")
        raise e