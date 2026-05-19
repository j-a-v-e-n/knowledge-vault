# PROJECT_BRIEF — Douyin Favorites Pipeline

## Goal
Permanent zero-maintenance pipeline that turns any Douyin video Javen saves on iPhone into a vault markdown note (with Chinese transcript) entirely locally, with no external API or service that can be killed by Douyin.

## User
Javen Cao | personal knowledge ingest workflow

## MVP
- iPhone Shortcut: share Douyin video → save URL to iCloud Drive `DouyinInbox/<timestamp>.txt`
- Mac daemon (launchd): watch iCloud folder → on new .txt → download mp4 (Playwright iesdouyin extractor, fallback yt-dlp) → mlx-whisper Chinese transcription → write `MyBrain/raw/douyin-favorites/<date>_<title>.md`
- Robust against: iCloud sync delay (launchd KeepAlive), partial downloads, multi-format video, Playwright session isolation in headless

## Non-goals
- Not scraping Douyin web/feed (researcher verdict: 6-12 month break cycle, lose)
- Not using cloud APIs (Whisper API, transcription SaaS) — local-only mandate
- Not real-time (1-min video = 3-5 min processing acceptable)
- Not handling TikTok (Douyin specifically per Javen 5/8)

## Definition of Done
- ✅ Phase 2 daemon code complete (8 files, 709 lines, 11 bugs fixed)
- ✅ iOS Shortcut configured per `iOS-Shortcut-setup.md` (5/9)
- ✅ End-to-end test passed: text file → 100s later → vault .md (5/9 17:30)
- ✅ Daemon launchd PID stable with KeepAlive (5/9)
- [ ] Phase 1 backlog: Javen manually share ~30 existing favorites once
- [ ] At least 1 wiki page distilled from transcribed content (closes the loop)

## Status (2026-05-18)
- Daemon production-ready, running since 5/9
- ⚠️ Pending: Javen Phase 1 backlog sharing + first ingest discussion

## Files of interest
- `monitor.py` — watchdog daemon entry
- `process.py` — per-URL pipeline orchestrator
- `transcribe.py` — mlx-whisper primary, faster-whisper fallback
- `generate_md.py` — vault markdown writer
- `douyin_extractor.py` — Playwright iesdouyin mobile-share extractor (the breakthrough)
- `com.javen.douyin-pipeline.plist` — launchd config
- `setup.sh` — one-shot installer
- `iOS-Shortcut-setup.md` — iPhone-side setup tutorial

## Constraints
- $0/month (no external services)
- All processing local (privacy + no API quotas to hit)
- mlx-whisper requires Apple Silicon (auto-fallback to faster-whisper)
- launchd daemon must self-heal (KeepAlive + restart on crash)
- Output path FIXED: `MyBrain/raw/douyin-favorites/` (vault ingest expects this)

## Operational commands
- Status: `launchctl list | grep douyin`
- Restart: `launchctl unload/load ~/Library/LaunchAgents/com.javen.douyin-pipeline.plist`
- Logs: `tail -f ~/Library/Mobile\ Documents/com~apple~CloudDocs/DouyinInbox/logs/monitor.log`

## Related vault entries
- task-board: `task-020`
- output dir: `MyBrain/raw/douyin-favorites/`
