# CME DS-45 exact-byte download failure receipt

- Topic: `RS-03`
- URL: `https://www.cmegroup.com/market-data/files/market-data-license-agreement-updates-june-2026.pdf`
- Discovery route: visible result `R8-RS03-S3` backend order 10; no additional search query was issued.
- Attempt 1: direct HTTPS transfer returned curl exit `92` with `HTTP/2 stream 1 was not closed cleanly: INTERNAL_ERROR (err 2)`.
- Attempt 2: same URL over HTTP/1.1 did not complete or create a file and the task-owned transfer process was terminated.
- Verified at UTC: `2026-07-25T16:28:44Z`
- Local snapshot file present: no
- Substitute used: no. The search excerpt and tool-extracted PDF lines are not treated as saved content bytes.
- Closure effect: none for the required provider-license snapshot class because current Tiingo terms bytes were saved separately; CME remains a supporting blocked source.

