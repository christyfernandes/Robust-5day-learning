# Day 23: Elasticsearch — Case Studies: GitHub, Uber, Wikipedia

## Time: ~25 min | Track proficiency target for this day: Level 4

## 1. Learning Objective
Extract one concrete takeaway from GitHub's historical code search, Uber's
logging infrastructure, and Wikipedia's CirrusSearch.

## 2. Core Concept (basics → advanced)

- **GitHub's historical code search**: GitHub has publicly discussed the
  significant engineering challenge of full-text code search at massive scale —
  code search has unusual characteristics relative to typical text search (exact
  symbol matching, special characters, code-specific tokenization) that
  stress-tested Elasticsearch's analyzer customization (Week 1, Day 3) in ways
  prose search doesn't.
- **Uber's logging infrastructure**: uses Elasticsearch heavily for operational
  log search and observability — a strong case study in the hot-warm-cold ILM
  tiering (Week 2, Day 11) and cluster architecture (Week 1, Day 5) needed at
  very high log-ingestion volume.
- **Wikipedia's CirrusSearch**: Wikipedia's own search (referenced in Week 1,
  Day 3) runs on Elasticsearch, with extensive public documentation of their
  relevance-tuning approach (BM25 parameters, Week 2 Day 9) for
  encyclopedia-article search specifically.

## 3. How It Really Works (Internals)

GitHub's code-search challenge is a particularly instructive case for
understanding **why generic full-text search analyzers don't automatically
work well for structured, non-prose content** — code has meaningful
tokenization boundaries (identifiers, operators, punctuation) that differ
substantially from natural-language tokenization, requiring custom analyzer
work (an extension of Week 1, Day 3's inverted-index/tokenization material)
rather than relying on Elasticsearch's prose-oriented defaults.

## 4. Architecture & Design Pattern Spotlight

**Pattern: case-study literacy, applied to Elasticsearch — with GitHub's code
search specifically illustrating that "search" is not one undifferentiated
problem, and default configurations tuned for prose can perform poorly on
structurally different content without deliberate customization.**

## 5. Hands-On Lab

Read a primary source on GitHub's code-search architecture (historical
engineering posts document this well), Uber's logging platform, and Wikipedia's
CirrusSearch relevance tuning. For GitHub specifically, identify: what specific
analyzer/tokenization customization (connecting to Week 1, Day 3's inverted-
index material) their code-search challenge required beyond Elasticsearch's
defaults.

## 6. Real-World Product Comparison

This lesson *is* the comparison exercise.

## 7. Common Production Pitfalls

- Assuming default text analyzers work equally well for all content types —
  GitHub's code-search challenge is a clear counter-example.
- Under-investing in relevance tuning (Week 2, Day 9) for a domain-specific
  search use case, assuming out-of-the-box BM25 defaults are sufficient.
- Not distinguishing "high query volume" (Wikipedia) from "high ingestion
  volume" (Uber's logging) as genuinely different scaling challenges requiring
  different architectural emphasis.

## 8. Review Questions
1. Why did GitHub's code search require custom analyzer work beyond
   Elasticsearch's defaults?
2. What tiering strategy does Uber's logging use case rely on most heavily?
3. What relevance-tuning parameters does Wikipedia's CirrusSearch adjust for
   encyclopedia content specifically?
4. Why are "high query volume" and "high ingestion volume" different scaling
   challenges?

## 9. Proficiency Checkpoint
If you can explain why a domain-specific search use case (like code search)
needs deliberate customization beyond defaults, you're at Level 4.

## Next
Day 24 covers when NOT to use Elasticsearch — including the ES-vs-ClickHouse
question directly relevant to your own work.
