# Telegram Channel Analytics Skill

A read-only, evidence-led workflow for weekly Telegram editorial reporting. It keeps append-only observations, remeasures live posts, and builds monthly and yearly comparisons from saved evidence rather than reconstructed history.

## Install

```bash
hermes skills install pavelnasuta/telegram-channel-analytics-skill
```

The canonical workflow lives in `skills/telegram-channel-analytics/SKILL.md`. Thin adapters for Claude Code, Codex, and generic agent instruction files point to the same contract.

## Project configuration

For each channel, choose a public source, measurement method, timezone, report period, project directory, and methodology version. Comparative reporting is optional and begins only after the author declares a versioned watchlist of compatible public channels.

A project stores `project.json`, append-only post and channel snapshots, versioned watchlists, methodology notes, and weekly, monthly, and yearly reports. Every report names the exact input snapshots it uses.

## Privacy

This package contains no real channel data, private editorial material, credentials, tokens, absolute local paths, or personal-account login workflow. It uses only public observations or information the author explicitly supplies.

## Limitations

Public signals can be incomplete or unavailable. Missing values remain missing. The workflow records changes between measurements but does not claim causes, predict growth, rank channels, or access native audience and traffic analytics. It does not publish content or alter channels.

## Tests

The test suite is synthetic and offline:

```bash
python3 -m unittest discover -s tests -v
```

Validate a project structure without network access:

```bash
python3 skills/telegram-channel-analytics/scripts/validate_project.py path/to/project
```

## Support

Report bugs or request improvements through [GitHub Issues](https://github.com/pavelnasuta/telegram-channel-analytics-skill/issues).

## Release notes

### v1.0.0

- First public release of the read-only analytics workflow.
- Immutable evidence model with publication, 24-hour, 7-day, 14-day, and monthly remeasurement.
- Weekly reports with monthly and yearly evidence roll-ups.
- Versioned watchlists for bounded comparative reporting.
