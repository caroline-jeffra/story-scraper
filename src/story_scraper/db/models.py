"""SQLAlchemy declarative base and ORM models."""

from datetime import datetime

from sqlalchemy import MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Declarative base carrying the shared naming convention."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Author(Base):
    """A story author, identified by their profile URL."""

    __tablename__ = "authors_TEMP"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str]
    name: Mapped[str]
    url: Mapped[str] = mapped_column(unique=True)
    slug: Mapped[str]
    bio_html: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
