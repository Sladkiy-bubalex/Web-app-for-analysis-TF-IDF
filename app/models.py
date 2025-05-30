from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey
from flask_login import UserMixin


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class User(Base, UserMixin):
    __tablename__ = "Users"

    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    admin: Mapped[bool] = mapped_column(default=False)

    @property
    def is_admin(self):
        return self.admin

    def __repr__(self):
        return f"User(id={self.id}, email={self.email})"

    def __str__(self):
        return self.email


class Sorted_Tfidf(Base):
    __tablename__ = "Sorted_tfidf"

    name_file: Mapped[str] = mapped_column(nullable=False)
    data: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))

    def __str__(self):
        return f"Name_file: {self.name_file}, Data: {self.data}"
