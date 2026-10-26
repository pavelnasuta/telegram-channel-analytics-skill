"""Contract tests for the public Telegram Channel Analytics skill."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PublicPackageContractTests(unittest.TestCase):
    def test_canonical_skill_declares_read_only_evidence_workflow(self) -> None:
        skill = (ROOT / "skills/telegram-channel-analytics/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("append-only", skill)
        self.assertIn("24 hours", skill)
        self.assertIn("7 days", skill)
        self.assertIn("14 days", skill)
        self.assertIn("watchlist", skill)
        self.assertIn("MTProto", skill)


if __name__ == "__main__":
    unittest.main()
