# RS-01 retrieval failure receipts

These receipts preserve failed attempts to obtain preferred exact bytes. Neither a URL nor a search snippet was substituted for a snapshot.

## RS01-FAIL-01 — Hacker News mutable HTML

- Counted-result locator: `https://news.ycombinator.com/item?id=47289837`
- Attempt UTC: `2026-07-25T16:28:05Z`
- Request: `GET`, redirects enabled, fail on HTTP error.
- Outcome: HTTP `429`, response media type `text/plain; charset=utf-8`, saved byte count `0`.
- Resolution: the exact official Hacker News Firebase API response for the same counted item was saved as `RS01-SRC-06_hacker_news_item_47289837.json`, with its parent story metadata saved separately. The practitioner snapshot class remains satisfied by those exact bytes; this receipt does not establish content.

## RS01-FAIL-02 — NCBI OA package

- NCBI OA API record: `PMC9644550`, citation `Syst Rev. 2022 Nov 9; 11:236`, license `CC BY`, retracted `no`, package updated `2025-08-24 14:25:14`.
- API-returned locator: `ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/6f/42/PMC9644550.tar.gz`
- HTTPS-form attempt UTC: `2026-07-25T16:29:01Z`; outcome HTTP `404`, saved byte count `0`.
- Exact FTP attempt UTC: `2026-07-25T16:29:14Z`; outcome FTP `550`, saved byte count `0`.
- Resolution: the exact full-text XML for the same PMCID/DOI/version-of-record article was saved from the Europe PMC REST endpoint at `2026-07-25T16:29:40Z` as `RS01-SRC-03_PMC9644550_fulltext.xml`. The empirical missed-study snapshot class remains satisfied; this receipt does not establish article content.
