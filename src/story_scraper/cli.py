import click

@click.group(name="story-scraper")
@click.version_option(package_name="story-scraper")
def cli() -> None:
    """Scrape short fiction collections and build EPUB digests of it."""
