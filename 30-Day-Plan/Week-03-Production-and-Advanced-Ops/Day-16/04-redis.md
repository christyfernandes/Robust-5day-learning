# Day 16: Redis — Memory Optimization: Compact Encodings

## Time: ~25 min | Track proficiency target for this day: Level 3.5

## 1. Learning Objective
Compare `MEMORY USAGE` of a hash under and over the `hash-max-listpack-entries`
threshold, and explain why Redis switches internal encodings automatically.

## 2. Core Concept (basics → advanced)

Redis automatically chooses between different **internal encodings** for its data
structures based on size, entirely transparently to the application — small
collections use compact, memory-efficient encodings (`listpack`, the modern successor
to the older `ziplist`), while larger collections switch to more general-purpose
encodings (a proper hash table, skip list, etc.) that trade some memory efficiency for
better performance at scale.

```
Small hash (few fields, small values):
  encoding: listpack — a compact, contiguous memory blob,
  linear scan for lookups (fine for small N)

Hash exceeds hash-max-listpack-entries OR hash-max-listpack-value:
  encoding AUTOMATICALLY switches to a real hash table —
  more per-entry overhead, but O(1) lookups instead of O(N) scan
  (worth it once N is large enough that linear scan cost exceeds
   the hash table's per-entry memory overhead)
```

## 3. How It Really Works (Internals)

This is a deliberate, size-dependent trade-off: for a **small** number of entries, a
compact, contiguous `listpack` (all entries packed tightly, no per-entry pointer/
hash-table overhead) uses genuinely less total memory than a real hash table would,
even though *accessing* it requires an O(N) linear scan rather than O(1) hash lookup —
for small N, that linear scan is fast enough in absolute terms that it doesn't matter,
and the memory savings are real and significant, especially when you have very many
such small collections (a common pattern — e.g., millions of users, each with a small
hash of a few profile fields). Once a collection grows past the configured threshold,
the linear-scan cost would start to matter, and Redis automatically switches to the
proper hash-table encoding to keep access fast, accepting the additional per-entry
memory overhead as the right trade at that size.

## 4. Architecture & Design Pattern Spotlight

**Pattern: small-collection memory optimization via size-adaptive internal
representation.** This is conceptually related to (though a different mechanism than)
how many systems apply different strategies at different scales — recognizing that
"the right data structure" can genuinely depend on size, not just logical type, is a
transferable systems-design insight, not a Redis-specific quirk.

## 5. Hands-On Lab

```bash
redis-cli CONFIG SET hash-max-listpack-entries 128

# small hash — stays as listpack
redis-cli HSET small_hash f1 v1 f2 v2 f3 v3
redis-cli OBJECT ENCODING small_hash    # should report "listpack"
redis-cli MEMORY USAGE small_hash

# large hash — exceeds threshold, converts to hashtable
for i in $(seq 1 200); do redis-cli HSET large_hash "field$i" "value$i" > /dev/null; done
redis-cli OBJECT ENCODING large_hash    # should report "hashtable"
redis-cli MEMORY USAGE large_hash
```
Compare `MEMORY USAGE` per-entry (total usage ÷ entry count) between the two — the
larger hash should show meaningfully higher per-entry overhead once converted to
`hashtable` encoding, quantifying the trade-off directly.

## 6. Real-World Product Comparison

- This encoding-switch behavior is precisely why **many small hashes** (a common
  pattern for storing per-entity metadata at scale, e.g., millions of small per-user
  profile hashes) can be dramatically more memory-efficient in Redis than a naive
  memory estimate (based on hash-table overhead alone) would predict — worth knowing
  when estimating capacity for such a workload.
- **DragonflyDB and Valkey** (Week 2, Day 13) implement analogous compact-encoding
  optimizations for API compatibility with Redis's observable behavior, though their
  internal implementations differ.

## 7. Common Production Pitfalls

- Estimating memory capacity using hash-table-overhead assumptions for a workload
  that's actually mostly small collections staying in compact encoding — overestimating
  required capacity.
- Setting `hash-max-listpack-entries` too high for a workload with genuinely large
  collections — forcing collections that would benefit from hash-table encoding's
  O(1) access to stay in a slower linear-scan encoding for too long.
- Not checking `OBJECT ENCODING` when diagnosing an unexpected memory or latency
  characteristic — the actual internal representation matters for both dimensions,
  and it's directly observable.

## 8. Review Questions
1. Why does a compact `listpack` encoding use less memory than a hash table for
   small collections, despite O(N) access?
2. What triggers the automatic switch to a more general-purpose encoding?
3. Why might many small hashes be far more memory-efficient than a naive capacity
   estimate would suggest?
4. When would raising `hash-max-listpack-entries` be the wrong tuning direction?

## 9. Proficiency Checkpoint
If you can predict and verify a collection's actual encoding and reason about the
resulting memory/access trade-off, you're at Level 3.5.

## Next
Day 17 covers Redis monitoring — the `INFO` command deep-dive and `LATENCY HISTORY` —
the tools for observing exactly this kind of memory behavior in production.
