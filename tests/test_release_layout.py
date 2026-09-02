import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReleaseLayoutTests(unittest.TestCase):
    def test_required_release_files_exist(self):
        for relative in [
            "README.md", "README.zh-CN.md", "LICENSE", "THIRD_PARTY_NOTICES.md", ".gitignore",
            "SKILL.md", "config.example.json", "agents/openai.yaml",
            "scripts/radar_cli.py", "scripts/finalize_radar.py", "scripts/render_digest.py", "scripts/send_digest.py",
            "scripts/te_radar/analysis.py", "scripts/te_radar/config.py", "scripts/te_radar/dedupe.py",
            "scripts/te_radar/pipeline.py", "scripts/te_radar/records.py", "scripts/te_radar/scoring.py",
            "scripts/te_radar/state.py", "scripts/te_radar/time_window.py",
            "scripts/te_radar/sources/crossref.py", "scripts/te_radar/sources/openalex.py",
            "scripts/te_radar/sources/arxiv.py", "scripts/te_radar/sources/rss.py",
            "references/scoring-policy.md", "references/analysis-contract.md", "references/source-policy.md",
            "example-output/sample-digest.md", "example-output/sample-final.json",
        ]:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_skill_uses_standalone_paths(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("te-literature-radar/scripts/", text)
        self.assertNotIn("te-literature-radar.config.json", text)
        self.assertIn("python3 scripts/radar_cli.py", text)
        self.assertIn("--config config.json", text)

    def test_no_mixed_repository_directories(self):
        for forbidden in ["paperecho-config", "paperecho-patch", "configs", "docs/superpowers"]:
            self.assertFalse((ROOT / forbidden).exists(), forbidden)

    def test_gitignore_protects_private_runtime_files(self):
        rules = set((ROOT / ".gitignore").read_text(encoding="utf-8").splitlines())
        for required in [
            "config.json", "te-literature-radar.config.json", ".secrets/", ".env", ".env.*",
            "te-literature-radar-output/", "__pycache__/", "*.pyc", ".DS_Store"
        ]:
            self.assertIn(required, rules)

    def test_example_config_does_not_enable_email(self):
        cfg = json.loads((ROOT / "config.example.json").read_text(encoding="utf-8"))
        self.assertFalse(cfg["email"]["enabled"])
        self.assertEqual(cfg["email"]["smtp_username"], "")
        self.assertEqual(cfg["email"]["from"], "")
        self.assertEqual(cfg["email"]["to"], "")
        self.assertEqual(cfg["score_weights"], {
            "te_relevance": 30,
            "research_quality": 30,
            "novelty": 20,
            "research_fit": 10,
            "recency": 10,
        })

    def test_public_readmes_have_required_commands(self):
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        command = "python3 scripts/radar_cli.py fetch --config config.json --mode lookback --lookback-days 7"
        self.assertIn("cp config.example.json config.json", english)
        self.assertIn(command, english)
        self.assertIn("$te-literature-radar", english)
        self.assertIn(command, chinese)
        self.assertIn("README.zh-CN.md", english)
        self.assertIn("953836942-dot/TE-literature-update", english)

    def test_synthetic_examples_are_clearly_labeled(self):
        digest = (ROOT / "example-output/sample-digest.md").read_text(encoding="utf-8")
        final = (ROOT / "example-output/sample-final.json").read_text(encoding="utf-8")
        self.assertIn("SYNTHETIC EXAMPLE", digest)
        self.assertIn("synthetic", final.lower())

    def test_license_and_upstream_notice_exist(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        self.assertIn("MIT License", license_text)
        self.assertIn("Copyright (c) 2026 953836942-dot", license_text)
        self.assertIn("lishn6/daily-econ-literature-radar", notices)
        self.assertIn("Copyright (c) 2026 lishn6", notices)


if __name__ == "__main__":
    unittest.main()
