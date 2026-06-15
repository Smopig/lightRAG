# Hybrid Knowledge Wiki Maintainer Rules

You maintain the wiki directory as a long-term knowledge base.

Rules:
1. Never overwrite raw_sources.
2. Every factual claim added to wiki pages must include a source note.
3. Prefer updating existing pages over creating near-duplicate pages.
4. Use full-path [[wikilink]] for related entities, concepts, projects, tools, and decisions.
5. If evidence is insufficient, add the statement under "Open Questions" instead of writing it as fact.
6. Append every ingest/query/lint/update action to wiki/log.md using this format:
   ## [YYYY-MM-DD] action | title
7. When new evidence contradicts old content, do not silently replace it. Add a "Conflict / Revision" section.
8. Use Traditional Chinese for human-facing explanations unless the source title/code/API name is English.
