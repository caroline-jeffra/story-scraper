"""Tests for the cli entry point"""

from importlib.metadata import version

from click.testing import CliRunner

from story_scraper.cli import cli


def test_version_flag_reports_installed_version() -> None:
    """`--version` exists cleanly and reports the installed package version."""
    runner = CliRunner()

    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert version("story-scraper") in result.output
