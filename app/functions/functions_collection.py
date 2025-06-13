from models import Collection, DocumentCollectionAssociation
from config import logger
from flask import request
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import insert, delete
from sqlalchemy.orm.exc import NoResultFound


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
        doc_in_collection = insert(DocumentCollectionAssociation).values(
            collection_id=collection_id,
            document_id=document_id
        )
        
        # Выполняем вставку
        request.db_session.execute(doc_in_collection)
        request.db_session.commit()

    except SQLAlchemyError as e:
        request.db_session.rollback()
        logger.error(f"Ошибка добавления документа в коллекцию: {e}")
        raise e

def add_collection(user_id: int, name: str) -> Collection:
    """
    Функция для добавления коллекции в БД
    """
    try:
        collection = Collection(
            user_id=user_id,
            name_collection=name
        )
        request.db_session.add(collection)
        request.db_session.commit()

        return collection

    except IntegrityError as e:
        request.db_session.rollback()
        logger.error(f"Коллекция с именем {name_collection} уже существует")
        raise e
    except SQLAlchemyError as e:
        request.db_session.rollback()
        logger.error(f"Ошибка добавления коллекции в БД: {name_collection}")
        raise e

def delete_document_from_collection(collection_id: int, document_id: int) -> bool:
    """
    Функция для удаления документа из коллекции
    """
    try:
        document_collection = delete(DocumentCollectionAssociation).where(
            DocumentCollectionAssociation.c.collection_id == collection_id,
            DocumentCollectionAssociation.c.document_id == document_id
        )

        request.db_session.execute(document_collection)
        request.db_session.commit()

        return True

    except NoResultFound as e:
        request.db_session.rollback()
        logger.error(f"Ошибка удаления документа из коллекции: {e}")
        raise e

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