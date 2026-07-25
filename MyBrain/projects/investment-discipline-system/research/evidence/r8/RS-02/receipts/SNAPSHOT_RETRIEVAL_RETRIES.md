# RS-02 snapshot retrieval retry receipt

## Attempt 1

- UTC immediately before attempt: `2026-07-25T16:21:06Z`
- Target:
  `https://arxiv.org/pdf/2606.27472v1`
- Result: local output failure before a source response was saved
- Exact error: `curl: (23) Failed writing received data to disk/application`
- Cause verified by local inspection: the intended `headers/` and `snapshots/`
  subdirectories did not yet exist.
- Effect on query accounting: none; this was not a search call.

## Attempt 2

- UTC immediately before attempt: `2026-07-25T16:21:34Z`
- Target:
  `https://arxiv.org/pdf/2606.27472v1`
- Result: sandbox DNS failure
- Exact error: `curl: (6) Could not resolve host: arxiv.org`
- Effect on query accounting: none; this was the same direct source retrieval,
  not a new search query.

## Successful retry

- Retrieval completion UTC: `2026-07-25T16:21:53Z`
- Result: success after approved network access
- Saved snapshot:
  `snapshots/RS02-SRC-MEM-SUPERSEDE-arxiv-2606.27472v1.pdf`
- Byte count: `275393`
- SHA-256:
  `ba7175324f30b02ff1967242250d421afdb0a6f1f80c3f48d2576f4f77de7e1b`

Because the exact fixed-version source bytes were ultimately saved and verified,
the memory-failure snapshot-class predicate is not made false by these transient
local/sandbox failures. No selected source remained blocked.
