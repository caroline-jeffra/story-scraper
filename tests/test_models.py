"""Tests for the ORM models."""

from sqlalchemy import create_engine, inspect

from story_scraper.db.models import Base


def test_create_all_creates_all_tables() -> None:
    """Base.metadata knows about all of the tables and can emit its DDL."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    tables = set(inspect(engine).get_table_names())
    assert tables == {"authors", "issues", "stories", "story_authors"}

    pk = inspect(engine).get_pk_constraint("story_authors")
    assert pk["constrained_columns"] == ["story_id", "author_id"]
