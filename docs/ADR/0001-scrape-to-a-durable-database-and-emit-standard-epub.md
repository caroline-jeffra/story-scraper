# ADR 0001 — Scrape to a durable local database and emit standard EPUB 3

- **Status:** Accepted
- **Date:** 2026-08-06
- **Supersedes:** the archived Laravel prototype (`prototype-archive/`)

## Context

The goal is a CLI that produces well-formatted EPUBs from short fiction published on specific
websites, each site supported by its own parser. *Beneath Ceaseless Skies* (BCS) is the first target.

Two capabilities define the product:

1. **Scrape** — retrieve stories from a supported site and persist them to a dedicated database.
2. **Build** — take all stories sharing a publication date and produce one EPUB from them.

Three further requirements emerged while scoping, and they turn out to be decisive:

- Later scrapes must not re-download or duplicate what is already stored.
- Digests should be buildable from a **particular author's** stories across issues.
- Digests should be buildable from **user-assigned tags**.

Additional constraints:

- Output must ingest cleanly into a Calibre library.
- This is a learning project; the value is in building it, not in having it built.

### Prior art considered

An earlier Laravel prototype reached two working scraper actions plus Author/Issue/Story models, but
never gained an orchestration layer, persistence wiring, or EPUB generation. Its metadata parsing had
already rotted: it recovered title, author, issue, and date by string-splitting one `.post-title`
element, and the live site no longer serves that shape.

More importantly, an established standard practice exists for this exact problem. Calibre's
`BasicNewsRecipe` framework fetches a periodical from the web, cleans it up, builds an EPUB with
correct metadata, and files it in the library. Calibre ships **2,123** builtin recipes, including ones
for *Strange Horizons* and *Lightspeed* — fiction magazines structurally very like BCS. The Strange
Horizons recipe accomplishes the whole webzine-to-EPUB job in **54 mostly-declarative lines**.

Any decision to write substantially more code than that needs to justify itself.

## Decision

Build a standalone Python CLI in which **a local database is the system of record and EPUBs are
derived artifacts**.

Concretely:

1. **Per-site parsers behind a single protocol.** Parsers are pure functions of HTML to dataclasses —
   they neither fetch nor touch the database, which makes them testable offline against committed
   HTML fixtures.
2. **SQLAlchemy over SQLite as the durable store.** Story URL is the natural key (enabling idempotent
   re-scrapes); `content_hash` distinguishes "already stored" from "changed upstream"; story-to-author
   is many-to-many; tags are a local vocabulary.
3. **A selection layer** that turns a query — by date, issue, author, or tag — into a `CollectionSpec`
   describing both the story set and the resulting book's metadata.
4. **Hand-rolled, conforming EPUB 3.3 output with no vendor-specific metadata**, validated by
   `epubcheck`. Calibre is treated as one consumer to test against, not as the specification.
5. **Generation is not delegated to Calibre.**

## Consequences

### Accepted benefits

- The archive outlives any individual book, which is what makes dedup, author digests, tag digests,
  and later full-text search possible at all.
- Parsers are testable with no network. Site drift becomes a failing test rather than a silent wrong
  result — the precise failure mode that killed the prototype.
- Standard EPUB 3 output works in any reader and is checkable against a published spec rather than
  against one application's tolerances.
- No runtime or build-time dependency on Calibre.
- Story text is preserved as sanitised HTML — paragraphs, emphasis, and scene breaks intact — rather
  than flattened to plain text as the prototype did.

### Accepted costs

- Substantially more code than a 54-line recipe, and the fetching and HTML-cleanup machinery
  duplicates what Calibre already provides.
- EPUB correctness becomes our responsibility. Mitigated by making `epubcheck` a gate rather than
  relying on "it opens in Calibre" — notably, EPUB 3 requires `dcterms:modified`, which Calibre
  silently forgives and `epubcheck` does not.
- Per-site parser maintenance is ours. Each new site is a new parser, though the protocol confines the
  change to one module.
- A local database is one more thing to migrate and back up. Alembic is adopted from the first schema
  commit for this reason.

## Alternatives considered

### 1. A Calibre recipe (`BasicNewsRecipe`) — rejected

The standard practice, and genuinely cheap. Rejected because recipes are feed-driven and
recency-oriented (`oldest_article` measured in days) and **keep no store**. They cannot answer "every
story by this author across all issues," which is a stated requirement.

A recipe reading a database was investigated in detail. The hooks exist and were verified —
`parse_index`, `articles_are_obfuscated` with `get_obfuscated_article`, and
`recipe_specific_options` driven by `--recipe-specific-option=name:value`. It still fails: a recipe
executes inside Calibre's own bundled interpreter (Python 3.14.2, frozen in the app bundle) and cannot
import this project or SQLAlchemy. It would have to re-query the schema in raw `sqlite3`, making the
database a contract between two runtimes with nothing checking it. And a recipe's value *is* its
fetching machinery, which is redundant once the stories are already stored.

**Revisit if** the archive requirement is ever dropped — at that point a ~54-line recipe replaces this
entire project, and should.

### 2. A recipe plus a side database — rejected

Two sources of truth that drift, and the recipe's fetch/parse output is not reusable by the CLI.

### 3. Generate via `ebook-convert` with metadata flags — rejected

Would work: `--title`, `--authors`, `--series`, `--series-index` all exist. Rejected because it makes
Calibre a hard build-time dependency for no gain over emitting the standard directly.

### 4. Continue the Laravel prototype — rejected

Stale parsing plus an unbuilt orchestration layer meant most of the work remained regardless.

### 5. EPUB metadata specialised toward Calibre — rejected

The initial plan called for emitting `calibre:series`, `calibre:series_index`, and the EPUB 2-era
`<meta name="cover">`, on the belief that Calibre required them. **This was tested and found false.**

Two minimal EPUB 3 files were built — one carrying only standard metadata, one additionally carrying
the vendor tags — and read back with `ebook-meta`. Output was identical, including
`Series : Beneath Ceaseless Skies #463`, author sort, tags, and cover extraction at the same byte
count. Modern Calibre reads standard EPUB 3 `belongs-to-collection` and `properties="cover-image"`
natively; the vendor tags are pure redundancy. They were historically necessary, which is the origin
of the folklore.

Series is therefore expressed as standard `belongs-to-collection` refined by `collection-type` and
`group-position`; the cover as a manifest item with `properties="cover-image"`.

**Re-verify if** a future Calibre release appears to miss series metadata. The experiment is cheap:
build standard-only against vendor-tagged and diff `ebook-meta` output.

## Notes

Deriving `dc:identifier` deterministically from source plus selector means rebuilding the same
collection yields the same UUID, so re-importing updates rather than duplicates. This is a standard
EPUB mechanism, not a Calibre one.

This project scrapes copyrighted fiction for personal library use. The `copyright_notice` field is
populated and carried into the generated book rather than stripped.

## Related

Full implementation plan, build sequence, and the running decision log live in the Obsidian vault
workspace at `~/code/Claudeville/Projects/story-scraper/` (`Plan`, `Decisions`, `Progress Log`,
`Open Threads`). This ADR records the top-level architectural decision only.
