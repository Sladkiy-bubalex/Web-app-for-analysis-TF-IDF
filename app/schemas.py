from pydantic import BaseModel, field_validator, ValidationError, EmailStr
from config import logger
from typing import List


def validate(schema_cls: type, **kwargs):
    try:
        check_validate = schema_cls(**kwargs)
        return check_validate
    except ValidationError as e:
        logger.error(f"Ошибка валидации данных: {e}")
        return e.errors()


class Base(BaseModel):
    """Базовая схема"""

    id: int


class UserSchema(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, password):
        if not password or len(password) < 8:
            raise ValueError("Пароль менее 8 символов или не введен")
        return password


class UserGetSchemaResponse(BaseModel):
    id: int
    email: EmailStr
    admin: bool


class UpdateUserSchema(BaseModel):
    email: EmailStr | None = None
    password: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, password):
        if password is not None and len(password) < 8:
            raise ValueError("Пароль менее 8 символов или не введен")
        return password


class DocumentSchemaResponse(Base):
    """Схема получения списка документов"""

    name_file: str


class UpdateDocumentSchemaRequest(BaseModel):
    name_file: str | None = None
    new_text: str | None = None


class CollectionListSchemaResponse(Base):
    """Схема получения списка коллекций"""

    files: List[DocumentSchemaResponse]


class CollectionGetSchemaResponse(BaseModel):
    """Схема получения коллекции"""

    documents_id: List[int]


class CollectionCreateSchemaRequest(BaseModel):
    """Схема создания коллекции"""

    name_collection: str


class DocumentCollectionCreateSchemaRequest(BaseModel):
    """Схема создания документа в коллекции"""

    collection_id: int
    document_id: int
