"""Offline validation for a Telegram Channel Analytics evidence project."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_FIELDS = (
    "project_name",
    "timezone",
    "primary_channel",
    "measurement_policy",
    "methodology_version",
    "methodology_effective_at",
)
SNAPSHOT_FIELDS = (
    "snapshot_id",
    "collected_at",
    "source",
    "method",
    "methodology_version",
)
MANIFEST_PATTERN = re.compile(
    r"<!--\s*analytics-manifest\s*(\{.*?\})\s*-->", re.DOTALL
)


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_timestamp(value: Any) -> bool:
    if not _is_nonempty_string(value):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def _load_json(path: Path, errors: list[str], root: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{_relative_path(root, path)} is not valid JSON: {exc}")
        return None


def _project_path(root: Path, value: str) -> Path | None:
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return None
    return resolved


def _validate_project_metadata(root: Path, errors: list[str]) -> None:
    project_path = root / "project.json"
    if not project_path.is_file():
        errors.append("project.json is required")
        return
    project = _load_json(project_path, errors, root)
    if not isinstance(project, dict):
        errors.append("project.json must contain a JSON object")
        return
    for field in PROJECT_FIELDS:
        if not _is_nonempty_string(project.get(field)):
            errors.append(f"project.json requires non-empty {field}")
    if "methodology_effective_at" in project and not _is_timestamp(
        project.get("methodology_effective_at")
    ):
        errors.append("project.json methodology_effective_at must be an ISO-8601 timestamp")


def _validate_snapshots(root: Path, errors: list[str]) -> set[Path]:
    snapshot_files: set[Path] = set()
    snapshot_ids: dict[str, str] = {}
    snapshot_root = root / "snapshots"
    if not snapshot_root.is_dir():
        return snapshot_files

    for path in sorted(snapshot_root.rglob("*.json")):
        resolved_path = path.resolve()
        snapshot_files.add(resolved_path)
        label = _relative_path(root, path)
        snapshot = _load_json(path, errors, root)
        if not isinstance(snapshot, dict):
            errors.append(f"{label} must contain a JSON object")
            continue
        for field in SNAPSHOT_FIELDS:
            if not _is_nonempty_string(snapshot.get(field)):
                errors.append(f"{label} requires non-empty {field}")
        if "collected_at" in snapshot and not _is_timestamp(snapshot.get("collected_at")):
            errors.append(f"{label} collected_at must be an ISO-8601 timestamp")
        if not (
            _is_nonempty_string(snapshot.get("post_id"))
            or _is_nonempty_string(snapshot.get("channel_id"))
        ):
            errors.append(f"{label} requires post_id or channel_id")
        if not isinstance(snapshot.get("values"), dict):
            errors.append(f"{label} requires values to be an object")
        if not isinstance(snapshot.get("missing_values"), list) or not all(
            _is_nonempty_string(value) for value in snapshot.get("missing_values", [])
        ):
            errors.append(f"{label} requires missing_values to be a list of strings")

        snapshot_id = snapshot.get("snapshot_id")
        if isinstance(snapshot_id, str) and _is_nonempty_string(snapshot_id):
            previous = snapshot_ids.get(snapshot_id)
            if previous is not None:
                errors.append(
                    f"duplicate snapshot_id {snapshot_id!r} in {previous} and {label}"
                )
            else:
                snapshot_ids[snapshot_id] = label
    return snapshot_files


def _validate_watchlists(root: Path, errors: list[str]) -> set[Path]:
    valid_watchlists: set[Path] = set()
    watchlist_root = root / "watchlists"
    if not watchlist_root.is_dir():
        return valid_watchlists

    for path in sorted(watchlist_root.rglob("*.json")):
        error_count = len(errors)
        label = _relative_path(root, path)
        watchlist = _load_json(path, errors, root)
        if not isinstance(watchlist, dict):
            errors.append(f"{label} must contain a JSON object")
            continue
        if not _is_nonempty_string(watchlist.get("watchlist_id")):
            errors.append(f"{label} requires non-empty watchlist_id")
        if type(watchlist.get("version")) is not int or watchlist["version"] < 1:
            errors.append(f"{label} requires a positive integer version")
        if not _is_timestamp(watchlist.get("created_at")):
            errors.append(f"{label} requires ISO-8601 created_at")
        channels = watchlist.get("channels")
        if not isinstance(channels, list):
            errors.append(f"{label} requires channels to be a list")
        else:
            for index, channel in enumerate(channels):
                entry_label = f"{label} channels[{index}]"
                if not isinstance(channel, dict):
                    errors.append(f"{entry_label} must be a JSON object")
                    continue
                for field in ("channel", "reason", "topic", "language", "size_range"):
                    if not _is_nonempty_string(channel.get(field)):
                        errors.append(f"{entry_label} requires non-empty {field}")
                if not isinstance(channel.get("formats"), list) or not channel["formats"]:
                    errors.append(f"{entry_label} requires a non-empty formats list")
        if len(errors) == error_count:
            valid_watchlists.add(path.resolve())
    return valid_watchlists


def _manifest_from_report(path: Path, errors: list[str], root: Path) -> dict[str, Any] | None:
    label = _relative_path(root, path)
    if path.suffix == ".json":
        manifest = _load_json(path, errors, root)
    else:
        try:
            match = MANIFEST_PATTERN.search(path.read_text(encoding="utf-8"))
        except OSError as exc:
            errors.append(f"{label} cannot be read: {exc}")
            return None
        if match is None:
            errors.append(f"{label} requires an analytics-manifest")
            return None
        try:
            manifest = json.loads(match.group(1))
        except json.JSONDecodeError as exc:
            errors.append(f"{label} has invalid analytics-manifest JSON: {exc}")
            return None
    if not isinstance(manifest, dict):
        errors.append(f"{label} manifest must be a JSON object")
        return None
    return manifest


def _validate_reports(
    root: Path, snapshot_files: set[Path], valid_watchlists: set[Path], errors: list[str]
) -> None:
    reports_root = root / "reports"
    if not reports_root.is_dir():
        return
    for path in sorted(reports_root.rglob("*")):
        if not path.is_file() or path.suffix not in {".json", ".md"}:
            continue
        label = _relative_path(root, path)
        manifest = _manifest_from_report(path, errors, root)
        if manifest is None:
            continue
        inputs = manifest.get("inputs")
        if not isinstance(inputs, list) or not all(_is_nonempty_string(item) for item in inputs):
            errors.append(f"{label} requires inputs to be a list of snapshot paths")
        else:
            for item in inputs:
                if not isinstance(item, str):
                    continue
                input_path = _project_path(root, item)
                if input_path is None or input_path not in snapshot_files:
                    errors.append(f"{label} input does not reference an existing snapshot: {item}")
        if manifest.get("report_mode") == "comparative":
            watchlist_value = manifest.get("watchlist")
            watchlist_path = (
                _project_path(root, watchlist_value)
                if isinstance(watchlist_value, str) and _is_nonempty_string(watchlist_value)
                else None
            )
            if watchlist_path is None or watchlist_path not in valid_watchlists:
                errors.append(f"{label} comparative report requires a versioned watchlist")


def validate_project(project_dir: Path) -> list[str]:
    """Return invariant violations for an offline analytics project, or [] if valid."""
    root = Path(project_dir).resolve()
    errors: list[str] = []
    if not root.is_dir():
        return ["project directory does not exist"]
    _validate_project_metadata(root, errors)
    snapshot_files = _validate_snapshots(root, errors)
    valid_watchlists = _validate_watchlists(root, errors)
    _validate_reports(root, snapshot_files, valid_watchlists, errors)
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_project.py PROJECT_DIRECTORY", file=sys.stderr)
        return 2
    errors = validate_project(Path(sys.argv[1]))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
