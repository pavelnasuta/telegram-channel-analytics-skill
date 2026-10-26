---
name: telegram-channel-analytics
description: Use when tracking Telegram channel content performance.
version: 1.0.2
author: Pavel Nasuta, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [telegram, analytics, editorial, measurement]
    related_skills: []
---

# Telegram Channel Analytics

Build a read-only editorial record from observed post-level signals. The workflow preserves evidence before interpretation: a weekly report is a current measurement, not a claim that a live post has finished growing.

## When to Use

- The author needs recurring editorial decisions from a Telegram channel.
- Posts can receive delayed attention from promotion or redistribution.
- The author wants month-to-month and year-to-year comparisons from preserved evidence.
- The author wants an optional, declared group of comparable public channels.

Do not use this workflow to publish content, alter a channel, estimate unavailable metrics, rank channels, or prove why a post changed.

## Prerequisites

Create one project directory per channel. At its first run, record only missing essentials in `project.json`:

- primary channel URL and timezone;
- report period and public source;
- measurement method and methodology version;
- whether the project uses a comparative watchlist.

Never inherit these choices into another channel. Store project data outside this public package.

## Sources and boundaries

Use post-level signals that are publicly visible or explicitly provided by the author. Every snapshot names its source, method, collection time, methodology version, available values, and missing values.

Never request or use personal-account developer credentials, authentication files, MTProto, private data, or access to a native analytics dashboard. A channel bot can confirm only the basic information it actually exposes; it does not establish access to audience, traffic-source, redistribution, or native-growth analytics.

## Evidence model

Use the project layout below. The linked support files are included by a direct Hermes installation:

- [offline validator](scripts/validate_project.py)
- [project contract](templates/project.schema.json)
- [post and channel snapshot contract](templates/snapshot.schema.json)
- [comparative watchlist contract](templates/watchlist.schema.json)
- [weekly editorial report template](templates/weekly-report.template.md)

Keep this layout inside the chosen project directory:

```text
project.json
snapshots/posts/
snapshots/channel/
watchlists/
reports/weekly/
reports/monthly/
reports/yearly/
methodology/
```

Snapshots are **append-only**. Add a new observation instead of changing an old one. A source or methodology change begins a documented, separate series. Every derived report lists exact input snapshot paths.

For a live post, collect an available measurement after publication, after **24 hours**, **7 days**, **14 days**, and at each relevant monthly close. A weekly report must describe a post in an active measurement window as provisional.

## Procedure

1. **Set the project contract.** Write `project.json`; state what source is available and what remains unknown. Completion: the timezone, source, method, and methodology version are present.
2. **Append observations.** Create one JSON snapshot per measurement. Keep unavailable values in `missing_values`, rather than replacing them with estimates. Completion: each snapshot has a unique ID, source, method, collection time, and series version.
3. **Validate before analysis.** Run the offline validator through `terminal`:
   ```bash
   python3 skills/telegram-channel-analytics/scripts/validate_project.py path/to/project
   ```
   Completion: it reports no integrity errors, or its errors are fixed without overwriting old snapshots.
4. **Write the weekly editorial report.** Use `templates/weekly-report.template.md`. Include: period and data completeness; observed facts; comparison with a comparable previous slice; at most two testable editorial hypotheses; unknowns and limits. Completion: the report manifest names every input snapshot.
5. **Roll up without recollecting history.** Build the monthly report from stored weekly and post snapshots. Build yearly comparisons from stored monthly reports. Completion: each roll-up preserves its source inputs and does not rewrite prior values.
6. **Add comparison only when declared.** Create a versioned watchlist before a comparative report. Each peer needs a reason, topic, language, size band, and usual formats. Normalize post age and, only when genuinely available, channel scale. Completion: the report names the watchlist version and frames differences as hypotheses.

## Comparative guardrails

- Compare compatible topic, language, size band, and publication format; label a mismatch rather than silently normalizing it away.
- Show accessible differences in rhythm, format, and post-level signals; do not produce a league table.
- A later view increase is an observation, not proof of promotion, redistribution, or content quality.
- If the comparative source changes, begin a separate series and mark older comparisons as non-comparable.

## Verification

- Validate the project before every new report.
- Confirm every report input exists and every comparative report references a versioned watchlist.
- Separate observed facts, hypotheses, and unavailable data in the visible report.
- Preserve historical snapshots and methodology notes; never backfill an invented value.

## Common mistakes

- Treating first-week views as a post's final result.
- Adding a peer after the comparison has been written without versioning the watchlist.
- Summing cumulative snapshots as though they were interval metrics.
- Calling a correlation with format, timing, or promotion a causal result.
- Representing basic bot confirmation as native analytics access.
