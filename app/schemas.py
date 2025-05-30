from pydantic import BaseModel, field_validator, ValidationError
from config import logger


class UserSchema(BaseModel):
    email: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, password):
        if not password or len(password) < 8:
            raise ValueError("Пароль менее 8 символов или не введен")
        return password


def validate(schema_cls: type, email: str, password: str):
    try:
        check_validate = schema_cls(email=email, password=password)
        return check_validate
    except ValidationError as e:
        errors = e.errors()
        logger.error(f"Ошибка валидации данных: {errors}")
        return errors
