import unittest

from fastapi.testclient import TestClient

from app.main import app


class AgentApiTests(unittest.TestCase):
    def test_analysis_can_be_reviewed(self) -> None:
        client = TestClient(app)
        health = client.get("/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["openai_model"], "gpt-5.6-luna")
        created = client.post("/api/v1/analyses", json={"objective": "Investigate the current synthetic portfolio scenario."})
        self.assertEqual(created.status_code, 200)
        run = created.json()
        self.assertEqual(run["status"], "pending_review")
        reviewed = client.post(f"/api/v1/analyses/{run['run_id']}/review", json={"decision": "approved", "note": "Synthetic portfolio review complete."})
        self.assertEqual(reviewed.status_code, 200)
        self.assertEqual(reviewed.json()["status"], "approved")


if __name__ == "__main__":
    unittest.main()
