---
name: telegram-channel-analytics
description: Build privacy-safe, read-only editorial reports from public Telegram post observations and local snapshots.
version: 1.0.0
---

# Telegram Channel Analytics

## Scope

This workflow is **read-only**. It does not publish posts, alter a channel, create a Telegram user session, or claim access to native Telegram analytics. Never request or use MTProto, `api_id`, `api_hash`, session files, credentials, or private data.

Use only observations that are publicly visible or explicitly supplied by the author. Record the source, method, collection time, methodology version, available values, and missing values for every observation. Treat unavailable data as unavailable; do not infer traffic sources, audience characteristics, repost causes, or causal effects.

## Project evidence model

Store each project locally with `project.json`, immutable post or channel observations under `snapshots/`, optional versioned `watchlists/`, and reports under `reports/`.

Snapshots are **append-only**: add a new measurement instead of changing a prior observation. A changed source or method begins a distinct, documented methodology series. A live post should be remeasured when available after publication, after **24 hours**, **7 days**, **14 days**, and at relevant month close.

A report must include an inputs manifest listing its exact snapshot paths. Comparative reports require a versioned author-declared watchlist. The watchlist records each public peer's reason for comparison, topic, language, size range, and usual formats. Do not compare undeclared channels or present rankings or causal claims.

## Workflow

1. Ask only for missing essentials: primary channel, timezone, report period, confirmed source, project directory, and whether the author wants a watchlist.
2. Write observations as new JSON snapshots using the templates. Preserve missing metrics explicitly.
3. Validate the project offline before producing a report:
   ```bash
   python3 skills/telegram-channel-analytics/scripts/validate_project.py path/to/project
   ```
4. Create a weekly report from the template. Include period, sources and completeness; observed facts; comparison with a comparable earlier slice; no more than two testable editorial hypotheses; and unknowns, gaps, and limitations.
5. For a comparison, reference a specific versioned watchlist and normalize post age before discussing available public signals. Label all interpretations as hypotheses.

If a required source is unavailable, record the gap and name the confirmed source required to extend the analysis. Do not suggest a workaround through a user Telegram session. Regular scheduling and publication are outside this workflow unless separately and explicitly requested.
