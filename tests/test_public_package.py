"""Contract tests for the public Telegram Channel Analytics skill."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/telegram-channel-analytics/SKILL.md"
ADAPTERS = (
    ROOT / "agents/claude-code/SKILL.md",
    ROOT / "agents/codex/AGENTS.md",
    ROOT / "agents/agents-md/AGENTS.md",
)
PUBLIC_FILES = (SKILL, *ADAPTERS, ROOT / "README.md")


class PublicPackageContractTests(unittest.TestCase):
    def test_canonical_skill_declares_read_only_evidence_workflow(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        self.assertIn("append-only", skill)
        self.assertIn("24 hours", skill)
        self.assertIn("7 days", skill)
        self.assertIn("14 days", skill)
        self.assertIn("watchlist", skill)
        self.assertIn("personal-account", skill)
        self.assertIn("monthly", skill)
        self.assertIn("yearly", skill)

    def test_adapters_point_to_the_canonical_workflow(self) -> None:
        for path in ADAPTERS:
            self.assertTrue(path.is_file(), path)
            self.assertIn(
                "skills/telegram-channel-analytics/SKILL.md",
                path.read_text(encoding="utf-8"),
            )

    def test_public_files_have_no_private_or_local_markers(self) -> None:
        text = "\n".join(path.read_text(encoding="utf-8") for path in PUBLIC_FILES)
        for marker in ("/root/", "api_hash", "api_id", ".session", "t.me/s/"):
            self.assertNotIn(marker, text)

    def test_readme_documents_install_limitations_and_v1_release_notes(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for expected in (
            "v1.0.0",
            "Privacy",
            "Limitations",
            "hermes skills install",
            "pavelnasuta/telegram-channel-analytics-skill",
        ):
            self.assertIn(expected, readme)

    def test_public_package_has_mit_license_and_ignores_user_data(self) -> None:
        self.assertIn("MIT License", (ROOT / "LICENSE").read_text(encoding="utf-8"))
        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("projects/", ignored)
        self.assertIn("__pycache__/", ignored)


if __name__ == "__main__":
    unittest.main()
