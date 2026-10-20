"""Integration tests use only isolated temporary Markdown vaults."""

import base64
import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from control.vault import MAX_ATTACHMENT_BYTES, create_vault_router


PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jxZkAAAAASUVORK5CYII="
)
PREFIX = "/control/vault"


class VaultTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.vault = self.base / "Knowledge"
        self.history = self.base / "runtime" / "vault-history"
        app = FastAPI()
        app.include_router(create_vault_router(self.vault, self.history))
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def put(self, path, content, expected=None):
        payload = {"path": path, "content": content}
        if expected is not None:
            payload["expected_sha256"] = expected
        return self.client.put(PREFIX + "/note", json=payload)

    def test_status_does_not_create_or_populate_vault(self):
        response = self.client.get(PREFIX + "/status")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["exists"])
        self.assertEqual(response.json()["note_count"], 0)
        self.assertFalse(self.vault.exists())
        self.assertEqual(self.client.get(PREFIX + "/notes").json(), {"items": [], "total": 0})

    def test_round_trip_retains_frontmatter_and_literal_search(self):
        source = "---\ntitle: 项目资料\nproject: Alpha\nstatus: draft\ntags: [品牌, reference]\ndate: 2026-10-21\n---\n# 一手记录\n检索正文中的关键词 Banana。\n"
        created = self.put("projects/资料.md", source)
        self.assertEqual(created.status_code, 200)
        value = created.json()
        self.assertTrue(value["created"])
        self.assertEqual(value["sha256"], hashlib.sha256(source.encode()).hexdigest())
        fetched = self.client.get(PREFIX + "/note", params={"path": "projects/资料.md"})
        self.assertEqual(fetched.json()["content"], source)
        self.assertEqual(fetched.json()["metadata"]["date"], "2026-10-21")
        self.put("inbox/Other.md", "# Other\nBanana")
        for hidden in [".obsidian/internal.md", "attachments/not-a-note.md"]:
            path = self.vault / hidden
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Banana", encoding="utf-8")
        result = self.client.get(PREFIX + "/notes", params={"query": "BANANA", "folder": "projects"})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["total"], 1)
        item = result.json()["items"][0]
        self.assertEqual(item["title"], "项目资料")
        self.assertEqual(item["project"], "Alpha")
        self.assertEqual(item["tags"], ["品牌", "reference"])
        self.assertEqual(self.client.get(PREFIX + "/status").json()["note_count"], 2)

    def test_optimistic_lock_and_external_history(self):
        initial = self.put("notes/one.md", "# Before\n").json()
        self.assertEqual(self.put("notes/one.md", "bad").status_code, 409)
        self.assertEqual(self.put("notes/one.md", "bad", "0" * 64).status_code, 409)
        saved = self.put("notes/one.md", "# After\n", initial["sha256"])
        self.assertEqual(saved.status_code, 200)
        self.assertFalse(saved.json()["created"])
        backups = list(self.history.rglob("*.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "# Before\n")
        self.assertEqual(self.put("notes/one.md", "stale", initial["sha256"]).status_code, 409)
        self.assertEqual(self.client.get(PREFIX + "/notes", params={"query": "Before"}).json()["total"], 0)
        self.assertEqual(self.put("deleted.md", "stale", "0" * 64).status_code, 409)

    def test_paths_reject_traversal_hidden_windows_and_attachments(self):
        forbidden = [
            "../escape.md", "/tmp/escape.md", "C:/escape.md", "folder\\escape.md",
            "notes/../../escape.md", "notes//escape.md", "notes/./escape.md",
            ".obsidian/config.md", "foo/.private/one.md", "note.md:stream",
            "CON.md", "foo./one.md", "attachments/one.md", "x.html",
        ]
        for path in forbidden:
            with self.subTest(path=path):
                self.assertEqual(self.put(path, "content").status_code, 400)
                self.assertEqual(self.client.get(PREFIX + "/note", params={"path": path}).status_code, 400)
        self.assertFalse((self.base / "escape.md").exists())
        self.assertEqual(self.client.get(PREFIX + "/notes", params={"folder": "../"}).status_code, 400)

    def test_symlink_cannot_escape_or_enter_search(self):
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "secret.md").write_text("secret", encoding="utf-8")
        self.vault.mkdir()
        try:
            os.symlink(outside, self.vault / "linked", target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Creating symlinks is unavailable on this host.")
        self.assertEqual(self.put("linked/secret.md", "overwritten").status_code, 400)
        self.assertEqual(self.client.get(PREFIX + "/note", params={"path": "linked/secret.md"}).status_code, 400)
        self.assertEqual(self.client.get(PREFIX + "/notes", params={"query": "secret"}).json()["total"], 0)
        self.assertEqual((outside / "secret.md").read_text(), "secret")

    def test_attachment_upload_serves_verified_type_and_safe_name(self):
        response = self.client.post(PREFIX + "/attachments", files={"file": ("../../品牌 logo.png", PNG, "image/png")})
        self.assertEqual(response.status_code, 201)
        image = response.json()
        self.assertTrue(image["path"].startswith("attachments/"))
        self.assertNotIn("..", image["path"])
        self.assertEqual(image["markdown"], "![[" + image["path"] + "]]")
        served = self.client.get(image["url"])
        self.assertEqual(served.status_code, 200)
        self.assertEqual(served.content, PNG)
        self.assertEqual(served.headers["content-type"], "image/png")
        self.assertEqual(served.headers["x-content-type-options"], "nosniff")
        self.assertEqual(self.client.get(PREFIX + "/status").json()["attachment_count"], 1)
        duplicate = self.client.post(PREFIX + "/attachments", files={"file": ("品牌 logo.png", PNG, "image/png")})
        self.assertNotEqual(duplicate.json()["path"], image["path"])

    def test_attachment_rejects_spoofing_and_non_attachment_paths(self):
        cases = [("fake.png", b"<html>bad</html>", "image/png"), ("x.svg", b"<svg/>", "image/svg+xml"), ("fake.gif", PNG, "image/gif")]
        for filename, raw, mime in cases:
            with self.subTest(filename=filename):
                response = self.client.post(PREFIX + "/attachments", files={"file": (filename, raw, mime)})
                self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.get(PREFIX + "/attachment", params={"path": "../x.png"}).status_code, 400)
        self.assertEqual(self.client.get(PREFIX + "/attachment", params={"path": "note.md"}).status_code, 400)
        attachments = self.vault / "attachments"
        attachments.mkdir(parents=True, exist_ok=True)
        (attachments / "fake.png").write_bytes(b"<script>bad</script>")
        (attachments / "wrong.gif").write_bytes(PNG)
        self.assertEqual(self.client.get(PREFIX + "/attachment", params={"path": "attachments/fake.png"}).status_code, 400)
        self.assertEqual(self.client.get(PREFIX + "/attachment", params={"path": "attachments/wrong.gif"}).status_code, 400)

    def test_attachment_size_limit(self):
        raw = PNG + b"\0" * (MAX_ATTACHMENT_BYTES + 1 - len(PNG))
        response = self.client.post(PREFIX + "/attachments", files={"file": ("large.png", raw, "image/png")})
        self.assertEqual(response.status_code, 413)
        self.assertFalse((self.vault / "attachments").exists())

    def test_yaml_is_safe_and_cyclic_aliases_do_not_break_response(self):
        unsafe = "---\ntitle: !!python/object/apply:os.system ['echo bad']\n---\n# Safe body"
        saved = self.put("unsafe.md", unsafe)
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.json()["metadata"], {})
        cyclic = self.put("cyclic.md", "---\nitems: &items [*items]\n---\n# Alias")
        self.assertEqual(cyclic.status_code, 200)
        self.assertEqual(cyclic.json()["metadata"], {"items": [None]})

    def test_history_cannot_live_inside_vault(self):
        with self.assertRaises(ValueError):
            create_vault_router(self.vault, self.vault / "history")


if __name__ == "__main__":
    unittest.main()
