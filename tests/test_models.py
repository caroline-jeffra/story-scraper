"""Tests for the ORM models."""

from sqlalchemy import create_engine, inspect

from story_scraper.db.models import Base


def test_create_all_creates_authors_table() -> None:
    """Base.metadata knows about the authors table and can emit its DDL."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    assert "authors" in inspect(engine).get_table_names()
