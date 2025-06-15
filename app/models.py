from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Table, Column
from flask_login import UserMixin
from datetime import datetime


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        index=True
    )


DocumentCollectionAssociation = Table(
    "DocumentCollectionAssociation",
    Base.metadata,
    Column(
        "document_id",
        ForeignKey("Documents.id", ondelete="SET_NULL"),
        primary_key=True
    ),
    Column(
        "collection_id",
        ForeignKey("Collections.id", ondelete="CASCADE"),
        primary_key=True
    )
)


class User(Base, UserMixin):
    __tablename__ = "Users"

    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    admin: Mapped[bool] = mapped_column(default=False)
    login_metrics: Mapped[list["LoginMetric"]] = relationship(
        "LoginMetric",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    collections: Mapped[list["Collection"]] = relationship(
        "Collection",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    @property
    def is_admin(self):
        return self.admin

    def __repr__(self):
        return (
            f"User("
            f"id={self.id},"
            f"email={self.email},"
            f"admin={self.admin})"
        )

    def __str__(self):
        return (
            f"User(id={self.id},"
            f"email={self.email},"
            f"admin={self.admin})"
        )


class Document(Base):
    __tablename__ = "Documents"

    name_file: Mapped[str] = mapped_column(unique=True, nullable=False)
    data: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("Users.id", ondelete="CASCADE"),
        index=True
    )
    user: Mapped[User] = relationship(
        "User",
        back_populates="documents"
    )
    collections: Mapped[list["Collection"]] = relationship(
        "Collection",
        secondary="DocumentCollectionAssociation",
        back_populates="documents",
        cascade="save-update",
        single_parent=True
    )

    def __str__(self):
        return (
            f"Name_file: {self.name_file},"
            f"Data: {self.data},"
            f"User_id: {self.user_id}"
        )


class Collection(Base):
    __tablename__ = "Collections"

    name_collection: Mapped[str] = mapped_column(unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        secondary="DocumentCollectionAssociation",
        back_populates="collections",
        cascade="save-update",
        single_parent=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("Users.id", ondelete="CASCADE"),
        index=True
    )
    user: Mapped[User] = relationship(
        "User",
        back_populates="collections"
    )

    def __str__(self):
        return (
            f"Name_collection: {self.name_collection},"
            f"User_id: {self.user_id}"
        )

    def __repr__(self):
        return (
            f"Collection("
            f"id={self.id},"
            f"name_collection={self.name_collection},"
            f"user_id={self.user_id}"
        )


class LoginMetric(Base):
    __tablename__ = "Login_metrics"

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("Users.id", ondelete="CASCADE"),
        index=True
    )
    user: Mapped[User] = relationship(
        "User",
        back_populates="login_metrics"
    )

    def __repr__(self):
        return (
            f"LoginMetric("
            f"id={self.id},"
            f"user_id={self.user_id})"
        )
