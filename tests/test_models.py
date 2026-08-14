"""Tests for the ORM models."""

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from story_scraper.db.models import Base, Story
from story_scraper.db.session import create_db_engine


def test_create_all_creates_all_tables() -> None:
    """Base.metadata knows about all of the tables and can emit its DDL."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    tables = set(inspect(engine).get_table_names())
    assert tables == {"authors", "issues", "stories", "story_authors"}

    pk = inspect(engine).get_pk_constraint("story_authors")
    assert pk["constrained_columns"] == ["story_id", "author_id"]


def test_foreign_keys_pragma_is_on() -> None:
    """The connect listener successfully sets foreign_keys."""
    engine = create_db_engine("sqlite+pysqlite:///:memory:")

    with engine.connect() as connection:
        result = connection.exec_driver_sql("PRAGMA foreign_keys").scalar()

    assert result == 1


def test_story_with_unknown_issue_id_is_rejected() -> None:
    """A nonexistent issue_id raises IntegrityError to demonstrate FK is enforced."""
    engine = create_db_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    story = Story(
        source="bcs",
        issue_id=9999,
        url="https://example.com/story/1",
        title="A Story",
        content_html="<p>Text.</p>",
        word_count=2,
        content_hash="abc123",
    )

    with Session(engine) as session, pytest.raises(IntegrityError):
        session.add(story)
        session.commit()
