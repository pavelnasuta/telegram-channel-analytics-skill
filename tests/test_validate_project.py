"""Tests for the offline Telegram Channel Analytics project validator."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "telegram-channel-analytics" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_project import validate_project


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def make_valid_project(
    project_dir: Path,
    *,
    snapshot_overrides: dict[str, object] | None = None,
    duplicate_snapshot_id: bool = False,
    report_mode: str = "weekly",
    write_watchlist: bool = True,
    report_input: str = "snapshots/posts/post-001-2026-10-01T00-00-00Z.json",
) -> None:
    write_json(
        project_dir / "project.json",
        {
            "project_name": "Synthetic analytics project",
            "timezone": "UTC",
            "primary_channel": "https://t.me/example_channel",
            "measurement_policy": "Record public observations only.",
            "methodology_version": "1.0.0",
            "methodology_effective_at": "2026-10-01T00:00:00Z",
        },
    )
    snapshot = {
        "snapshot_id": "post-001-at-2026-10-01T00:00:00Z",
        "collected_at": "2026-10-01T00:00:00Z",
        "source": "public post page",
        "method": "manual observation",
        "methodology_version": "1.0.0",
        "post_id": "post-001",
        "values": {"views": 100},
        "missing_values": ["reposts"],
    }
    snapshot.update(snapshot_overrides or {})
    write_json(
        project_dir / "snapshots/posts/post-001-2026-10-01T00-00-00Z.json", snapshot
    )
    if duplicate_snapshot_id:
        duplicate = dict(snapshot)
        duplicate["collected_at"] = "2026-10-02T00:00:00Z"
        write_json(
            project_dir / "snapshots/posts/post-001-2026-10-02T00-00-00Z.json", duplicate
        )
    if write_watchlist:
        write_json(
            project_dir / "watchlists/watchlist-v1.json",
            {
                "watchlist_id": "similar-public-channels",
                "version": 1,
                "created_at": "2026-10-01T00:00:00Z",
                "channels": [
                    {
                        "channel": "https://t.me/example_peer",
                        "reason": "Synthetic peer for tests",
                        "topic": "analytics",
                        "language": "en",
                        "size_range": "1k-10k",
                        "formats": ["text"],
                    }
                ],
            },
        )
    write_json(
        project_dir / "reports/weekly/weekly-2026-W40.json",
        {
            "report_mode": report_mode,
            "inputs": [report_input],
            "watchlist": "watchlists/watchlist-v1.json" if report_mode == "comparative" else None,
        },
    )


class ValidateProjectTests(unittest.TestCase):
    def test_valid_project_passes(self) -> None:
        with TemporaryDirectory() as directory:
            project_dir = Path(directory)
            make_valid_project(project_dir)
            self.assertEqual(validate_project(project_dir), [])

    def test_snapshot_without_source_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            project_dir = Path(directory)
            make_valid_project(project_dir, snapshot_overrides={"source": ""})
            self.assertIn("source", "\n".join(validate_project(project_dir)))

    def test_duplicate_snapshot_id_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            project_dir = Path(directory)
            make_valid_project(project_dir, duplicate_snapshot_id=True)
            self.assertIn("duplicate", "\n".join(validate_project(project_dir)).lower())

    def test_comparative_report_requires_versioned_watchlist(self) -> None:
        with TemporaryDirectory() as directory:
            project_dir = Path(directory)
            make_valid_project(
                project_dir, report_mode="comparative", write_watchlist=False
            )
            self.assertIn("watchlist", "\n".join(validate_project(project_dir)).lower())

    def test_report_inputs_must_reference_existing_snapshots(self) -> None:
        with TemporaryDirectory() as directory:
            project_dir = Path(directory)
            make_valid_project(project_dir, report_input="missing.json")
            self.assertIn("input", "\n".join(validate_project(project_dir)).lower())

    def test_comparative_report_rejects_watchlist_with_empty_channel_entry(self) -> None:
        with TemporaryDirectory() as directory:
            project_dir = Path(directory)
            make_valid_project(project_dir, report_mode="comparative")
            write_json(
                project_dir / "watchlists/watchlist-v1.json",
                {
                    "watchlist_id": "similar-public-channels",
                    "version": 1,
                    "created_at": "2026-10-01T00:00:00Z",
                    "channels": [{}],
                },
            )
            self.assertIn("channel", "\n".join(validate_project(project_dir)).lower())

    def test_comparative_report_rejects_boolean_watchlist_version(self) -> None:
        with TemporaryDirectory() as directory:
            project_dir = Path(directory)
            make_valid_project(project_dir, report_mode="comparative")
            write_json(
                project_dir / "watchlists/watchlist-v1.json",
                {
                    "watchlist_id": "similar-public-channels",
                    "version": True,
                    "created_at": "2026-10-01T00:00:00Z",
                    "channels": [
                        {
                            "channel": "https://t.me/example_peer",
                            "reason": "Synthetic peer for tests",
                            "topic": "analytics",
                            "language": "en",
                            "size_range": "1k-10k",
                            "formats": ["text"],
                        }
                    ],
                },
            )
            self.assertIn("version", "\n".join(validate_project(project_dir)).lower())


if __name__ == "__main__":
    unittest.main()
