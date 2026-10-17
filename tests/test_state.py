"""Executable regression evidence for the optional, deterministic helper."""
import copy
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "naming_state.py"


class NamingStateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "naming.json"

    def call(self, *args, ok=True):
        run = subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, args)], capture_output=True,
            encoding="utf-8", check=False,
        )
        if ok:
            self.assertEqual(run.returncode, 0, msg=run.stderr)
            return json.loads(run.stdout)
        self.assertNotEqual(run.returncode, 0)
        self.assertTrue(run.stderr.strip())
        return run.stderr.strip()

    def init(self, brief="A method that extracts meaningful mechanisms and creates new outcomes"):
        return self.call("init", self.path, "--brief", brief)

    def add(self, name="sample", parts=None, rev=0, zh=""):
        if parts is None:
            parts = ["Quintess", "o", "poiesis"]
        args = ["add", self.path, "--expect", rev, "--id", name,
                "--parts-json", json.dumps(parts, ensure_ascii=False)]
        if zh:
            args += ["--zh", zh]
        return self.call(*args)

    def test_historical_real_case_and_codepoint_preview(self):
        self.init()
        data = self.add(zh="萃化")
        c = data["candidates"]["sample"]
        self.assertEqual(c["assembled"], "Quintessopoiesis")
        self.assertEqual(c["codepoints"], 16)
        self.assertEqual(c["part_codepoints"], [8, 1, 7])
        self.assertEqual(c["localized"]["zh-CN"]["name"], "萃化")
        self.assertEqual(data["revision"], 1)

    def test_local_edit_changes_only_one_part_and_keeps_localization(self):
        self.init()
        self.add(zh="萃化")
        result = self.call("edit", self.path, "--expect", 1, "--id", "sample", "--index", 2, "--text", "genesis")
        c = result["candidates"]["sample"]
        self.assertEqual(c["parts"], ["Quintess", "o", "genesis"])
        self.assertEqual(c["localized"]["zh-CN"]["name"], "萃化")
        self.assertEqual(result["events"][-1]["details"]["before"], ["Quintess", "o", "poiesis"])

    def test_insert_remove_and_more_than_three_parts(self):
        self.init()
        self.add(parts=["meta", "gene", "sis"])
        a = self.call("insert", self.path, "--expect", 1, "--id", "sample", "--index", 2, "--text", "trans")
        self.assertEqual(a["candidates"]["sample"]["parts"], ["meta", "gene", "trans", "sis"])
        b = self.call("remove", self.path, "--expect", 2, "--id", "sample", "--index", 1)
        self.assertEqual(b["candidates"]["sample"]["assembled"], "metatranssis")

    def test_soft_preference_does_not_hard_block(self):
        self.init()
        state = self.call("preference", self.path, "--expect", 0, "--kind", "avoid", "--value", "long names")
        self.assertEqual(state["preferences"]["avoid"], ["long names"])
        a = self.add(rev=1)
        self.assertEqual(a["candidates"]["sample"]["assembled"], "Quintessopoiesis")
        b = self.call("preference", self.path, "--expect", 2, "--kind", "like", "--value", "古典词根")
        self.assertEqual(b["preferences"]["like"], ["古典词根"])

    def test_literal_ban_rejects_future_edits_without_mutation(self):
        self.init()
        self.add()
        banned = self.call("preference", self.path, "--expect", 1, "--kind", "ban", "--value", "GENESIS")
        self.assertEqual(banned["revision"], 2)
        before = self.path.read_bytes()
        error = self.call("edit", self.path, "--expect", 2, "--id", "sample", "--index", 2, "--text", "genesis", ok=False)
        self.assertIn("banned", error)
        self.assertEqual(self.path.read_bytes(), before)
        c = self.call("edit", self.path, "--expect", 2, "--id", "sample", "--index", 2, "--text", "morphosis")
        self.assertEqual(c["candidates"]["sample"]["assembled"], "Quintessomorphosis")

    def test_ban_marks_old_candidates_not_delete_or_rewrite(self):
        self.init()
        self.add()
        banned = self.call("preference", self.path, "--expect", 1, "--kind", "ban", "--value", "POIESIS")
        self.assertEqual(banned["candidates"]["sample"]["excluded_fragments"], ["POIESIS"])
        self.assertEqual(banned["candidates"]["sample"]["parts"], ["Quintess", "o", "poiesis"])

    def test_withdraw_one_preference_preserves_other_decisions_and_history(self):
        self.init()
        self.add(parts=["Seme", "weave"], zh="意铸")
        self.call("preference", self.path, "--expect", 1, "--kind", "avoid", "--value", "long names")
        self.call("preference", self.path, "--expect", 2, "--kind", "like", "--value", "Seme")
        before = self.call("preference", self.path, "--expect", 3, "--kind", "ban", "--value", "bot")
        after = self.call("preference", self.path, "--expect", 4, "--kind", "avoid",
                          "--value", "LONG NAMES", "--remove")
        self.assertEqual(after["preferences"], {"like": ["Seme"], "avoid": [], "ban_fragments": ["bot"]})
        self.assertEqual(after["candidates"], before["candidates"])
        self.assertEqual(after["events"][:-1], before["events"])
        self.assertEqual(after["events"][-1]["details"]["operation"], "remove")
        self.assertEqual(after["revision"], 5)

    def test_withdraw_ban_releases_candidate_and_guards_revision(self):
        self.init()
        self.add(parts=["Seme", "weave"])
        self.call("preference", self.path, "--expect", 1, "--kind", "ban", "--value", "WEAVE")
        before = self.path.read_bytes()
        self.call("preference", self.path, "--expect", 1, "--kind", "ban", "--value", "weave", "--remove", ok=False)
        self.assertEqual(self.path.read_bytes(), before)
        after = self.call("preference", self.path, "--expect", 2, "--kind", "ban", "--value", "weave", "--remove")
        self.assertEqual(after["candidates"]["sample"]["excluded_fragments"], [])
        edited = self.call("edit", self.path, "--expect", 3, "--id", "sample", "--index", 1, "--text", "weaver")
        self.assertEqual(edited["candidates"]["sample"]["assembled"], "Semeweaver")

    def test_withdraw_absent_preference_does_not_write(self):
        self.init()
        before = self.path.read_bytes()
        self.call("preference", self.path, "--expect", 0, "--kind", "avoid", "--value", "missing", "--remove", ok=False)
        self.assertEqual(self.path.read_bytes(), before)

    def test_refresh_rationale_preserves_names_preferences_status_and_other_candidates(self):
        self.init()
        old_text = "Only replace weave."
        self.call("add", self.path, "--expect", 0, "--id", "a", "--parts-json",
                  json.dumps(["Seme", "o", "morphosis"]), "--zh", "意铸", "--rationale", old_text)
        self.add(name="b", parts=["Root", "loom"], rev=1, zh="词梭")
        self.call("status", self.path, "--expect", 2, "--id", "a", "--value", "chosen")
        before = self.call("preference", self.path, "--expect", 3, "--kind", "ban", "--value", "bot")
        text = "Modern coined name; the old weave explanation no longer applies."
        after = self.call("rationale", self.path, "--expect", 4, "--id", "a", "--text", text)
        expected = copy.deepcopy(before["candidates"])
        expected["a"]["rationale"] = text
        self.assertEqual(after["candidates"], expected)
        self.assertEqual(after["preferences"], before["preferences"])
        self.assertEqual(after["events"][:-1], before["events"])
        self.assertEqual(after["events"][-1]["details"], {"id": "a", "before": old_text, "after": text})
        self.assertEqual(after["revision"], 5)

    def test_invalid_rationale_or_stale_revision_does_not_write(self):
        self.init()
        self.add()
        before = self.path.read_bytes()
        for ident, rev, text in [("sample", 0, "new"), ("missing", 1, "new"),
                                  ("sample", 1, " "), ("sample", 1, "x" * 4001)]:
            with self.subTest(ident=ident, revision=rev, length=len(text)):
                self.call("rationale", self.path, "--expect", rev, "--id", ident, "--text", text, ok=False)
                self.assertEqual(self.path.read_bytes(), before)

    def test_stale_revision_and_create_only(self):
        self.init()
        self.call("init", self.path, "--brief", "overwrite", ok=False)
        self.add()
        before = self.path.read_bytes()
        self.call("status", self.path, "--expect", 0, "--id", "sample", "--value", "chosen", ok=False)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.call("show", self.path)["revision"], 1)

    def test_independent_chinese_localization(self):
        self.init()
        self.add(zh="萃化")
        new = self.call("localize", self.path, "--expect", 1, "--id", "sample",
                        "--lang", "zh-CN", "--name", "萃构", "--reason", "情境生成")
        self.assertEqual(new["candidates"]["sample"]["assembled"], "Quintessopoiesis")
        self.assertEqual(new["candidates"]["sample"]["localized"]["zh-CN"]["name"], "萃构")
        self.assertEqual(new["candidates"]["sample"]["localized"]["zh-CN"]["reason"], "情境生成")

    def test_candidate_status_and_undo_are_explicit(self):
        self.init()
        self.add(name="a")
        self.add(name="b", parts=["Diff", "weave"], rev=1)
        c = self.call("status", self.path, "--expect", 2, "--id", "a", "--value", "chosen")
        self.assertEqual(c["candidates"]["a"]["status"], "chosen")
        self.assertEqual(c["candidates"]["b"]["status"], "draft")
        self.call("status", self.path, "--expect", 3, "--id", "b", "--value", "chosen", ok=False)
        z = self.call("status", self.path, "--expect", 3, "--id", "a", "--value", "shortlisted")
        self.assertEqual(z["candidates"]["a"]["status"], "shortlisted")
        self.call("status", self.path, "--expect", 4, "--id", "b", "--value", "chosen")

    def test_empty_parts_and_invalid_json_rejected(self):
        self.init()
        before = self.path.read_bytes()
        self.call("add", self.path, "--expect", 0, "--id", "a", "--parts-json", "[]", ok=False)
        self.call("add", self.path, "--expect", 0, "--id", "a", "--parts-json", "not-json", ok=False)
        self.assertEqual(self.path.read_bytes(), before)

    def test_no_file_or_directory_overwrites(self):
        self.init()
        new = Path(self.tmp.name) / "link.json"
        new.symlink_to(self.path)
        self.call("show", new, ok=False)
        self.call("init", new, "--brief", "hello", ok=False)
        self.call("init", Path(self.tmp.name) / "not-existing" / "state.json", "--brief", "hello", ok=False)

    def test_local_readout_subset_and_file_permissions(self):
        self.init()
        self.add(name="a")
        self.add(name="b", rev=1, parts=["Code", "trace"])
        result = self.call("show", self.path, "--id", "b")
        self.assertEqual(list(result["candidates"]), ["b"])
        if os.name == "posix":
            self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o600)

    def test_skill_frontmatter_matches_agent_skills_basic_contract(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\n"))
        front = skill.split("---\n", 2)[1]
        self.assertIn("name: tech-concept-naming\n", front)
        self.assertIn("license: MIT\n", front)
        desc = next(v for v in front.splitlines() if v.startswith("description: "))
        self.assertLessEqual(len(desc[len("description: "):]), 1024)
        self.assertTrue(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ROOT.name))
        self.assertLess(len(skill.splitlines()), 500)


if __name__ == "__main__":
    unittest.main()
