"""Integration checks for the actual upstream service plus local vault."""

import functools
import json
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from control.main import build_app


class ConsoleIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.runtime = self.root / "runtime"
        self.vault = self.root / "vault"
        self.dist = self.root / "dist"
        self.dist.mkdir()
        (self.dist / "index.html").write_text("<html>integration UI</html>", encoding="utf-8")

    def tearDown(self):
        self.directory.cleanup()

    def app(self):
        return build_app(self.runtime, self.vault, self.dist)

    def test_upstream_health_real_agents_and_same_origin_ui(self):
        with TestClient(self.app()) as client:
            self.assertEqual(client.get("/health").json()["status"], "ok")
            status = client.get("/control/status").json()
            self.assertEqual(status["project"], "agent-control-console")
            self.assertEqual(status["model_runtime"], "not-configured")
            self.assertEqual(status["storage"], "SQLite")
            agents = client.get("/agent/").json()
            self.assertEqual(agents["total"], 2)
            self.assertTrue(any(
                item["data"]["chat_config"]["invite_config"]["invitable"]
                for item in agents["agents"]
            ))
            self.assertIn("integration UI", client.get("/").text)
            self.assertIn("integration UI", client.get("/vault").text)
            self.assertEqual(client.get("/assets/missing.js").status_code, 404)

    def test_agent_records_persist_across_service_restarts(self):
        with TestClient(self.app()) as client:
            created = client.post("/agent/", json={"name": "Persistence check"})
            self.assertEqual(created.status_code, 201, created.text)
            agent_id = created.json()["agent_id"]
        with TestClient(self.app()) as client:
            found = client.get("/agent/").json()
            self.assertEqual(found["total"], 3)
            self.assertIn(agent_id, json.dumps(found))

    def test_registered_agent_tools_use_the_same_real_vault(self):
        app = self.app()
        with TestClient(app) as client:
            tools = client.portal.call(app.state.extra_agent_tools, "local", "control-master", "check")
            by_name = {tool.name: tool for tool in tools}
            self.assertEqual(set(by_name), {"VaultSearch", "VaultRead", "VaultWrite"})
            self.assertTrue(by_name["VaultRead"].is_read_only)
            self.assertFalse(by_name["VaultWrite"].is_read_only)
            self.assertFalse(by_name["VaultWrite"].is_concurrency_safe)
            result = client.portal.call(functools.partial(
                by_name["VaultWrite"], path="test.md", content="# Tool result\nunique-knowledge"
            ))
            payload = json.loads(result.content[0].text)
            self.assertEqual(payload["path"], "test.md")
            self.assertEqual((self.vault / "test.md").read_text(encoding="utf-8"), "# Tool result\nunique-knowledge")
            searched = client.portal.call(functools.partial(by_name["VaultSearch"], query="unique-knowledge"))
            self.assertEqual(json.loads(searched.content[0].text)["total"], 1)
            conflict = client.portal.call(functools.partial(
                by_name["VaultWrite"], path="test.md", content="unversioned overwrite"
            ))
            self.assertEqual(json.loads(conflict.content[0].text)["status"], 409)


if __name__ == "__main__":
    unittest.main()
