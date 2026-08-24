# Day 2: Elasticsearch — Analyzers & Mapping Deep-Dive

## Time: ~25 min | Track proficiency target for this day: Level 2

## 1. Learning Objective
Explain what an analyzer does as a concrete three-stage pipeline, and design a mapping
(including multi-fields) that supports both full-text search and exact aggregation on
the same underlying data.

## 2. Core Concept (basics → advanced)

**An analyzer is exactly three stages, always:**
```
"The Quick Brown Fox!"
        │
        ▼  1. Character filters (strip HTML, replace chars, etc. — optional)
"The Quick Brown Fox!"
        │
        ▼  2. Tokenizer (split into tokens — usually on whitespace/punctuation)
["The", "Quick", "Brown", "Fox!"]
        │
        ▼  3. Token filters (lowercase, stemming, stopword removal, synonyms...)
["quick", "brown", "fox"]
```
This exact token list is what actually goes into the inverted index (Day 1). The
built-in `standard` analyzer does steps 2–3 with sensible English-ish defaults; you can
compose your own from any combination of tokenizer + filters.

**Multi-fields — the practical fix for "I need both text search and exact match":**
```json
PUT /products
{
  "mappings": {
    "properties": {
      "name": {
        "type": "text",
        "fields": {
          "keyword": { "type": "keyword", "ignore_above": 256 }
        }
      }
    }
  }
}
```
Now `name` (analyzed, for full-text `match` queries) and `name.keyword` (exact, for
aggregations/sorting/filtering) coexist on the same field, indexed once at write time.
This single pattern resolves the vast majority of "why doesn't my aggregation work on
this field" confusion.

## 3. How It Really Works (Internals)

At index time, ES runs the configured analyzer over each `text` field's value and
writes the resulting tokens into the inverted index for that field — a `keyword` field
skips this entirely and is indexed as one exact token (with `doc_values` enabled by
default, a separate columnar structure optimized for sorting/aggregating, distinct from
the inverted index itself). This is worth sitting with: a `text` field literally cannot
be aggregated on directly by default, not because of an arbitrary restriction, but
because "the quick brown fox" was tokenized into four separate terms — there's no
single value left to aggregate on.

```
text field "Quick Brown Fox"     keyword field "Quick Brown Fox"
        │                                  │
   tokenized: [quick, brown, fox]    stored whole, exact
        │                                  │
   → good for: match queries         → good for: term queries, aggs, sort
```

## 4. Architecture & Design Pattern Spotlight

**Pattern: dual representation for dual access patterns** (analyzed for search, raw for
exact operations). This is a specific instance of a broader idea you'll see again:
ClickHouse's `LowCardinality` + normal column pairing, and even database "generated
column + index" patterns solve conceptually similar dual-access problems.

## 5. Hands-On Lab
```bash
# See exactly what an analyzer produces, without indexing anything:
curl -X POST "localhost:9200/_analyze" -H 'Content-Type: application/json' -d '
{"analyzer": "standard", "text": "The Quick Brown Fox Jumps!"}'
```
Then create an index with the multi-field mapping above, index a few products, and
run: (a) a `match` query on `name` for a partial phrase, and (b) a `terms` aggregation
on `name.keyword` — confirm (a) works with partial/case-different text and (b) gives
you clean exact buckets.

## 6. Real-World Product Comparison

- **E-commerce search** (a very common ES use case) universally needs both: full-text
  "quick brown" search *and* exact faceted filters ("brand: Nike") — the multi-field
  pattern above is close to the default recommended mapping shape for this reason.
- **Algolia** handles this distinction largely automatically/opaquely for you as part
  of its hosted product — a genuine simplicity win, at the cost of the fine control
  ES's explicit mapping gives you (e.g., custom analyzers per language, per field).
- Custom analyzers matter enormously for **non-English or domain-specific text**
  (e.g., product SKUs with embedded punctuation, or multilingual content) — this is a
  real area where Elasticsearch's flexibility clearly beats a one-size-fits-all hosted
  default.

## 7. Common Production Pitfalls
- Trying to aggregate directly on a `text` field and hitting an error (or, in older
  versions, silently expensive `fielddata`) — the fix is almost always "add a
  `.keyword` sub-field," not "force it to work on the text field."
- Using the default `standard` analyzer for genuinely different languages without
  realizing stemming/stopwords are English-tuned by default — search recall/precision
  can quietly suffer for non-English content.
- Changing an analyzer on an existing mapping and expecting old documents to be
  affected — analyzers apply at index time; changing the mapping doesn't retroactively
  re-analyze already-indexed documents. Reindexing is required.

## 8. Review Questions
1. Name the three analyzer stages in order, and give one example of what each could do.
2. Why can't you aggregate directly on a `text` field by default?
3. What problem does a multi-field mapping solve, concretely?
4. Why doesn't changing an analyzer retroactively affect already-indexed data?

## 9. Proficiency Checkpoint
If you can design a mapping with the right multi-field structure for a given "I need
both search and exact filtering" requirement, you're at Level 2, moving into Level 3.

## Next
Day 3 covers the Query DSL — match/term/bool/range — and BM25 relevance scoring, using
the mapping design skills from today.
