import unittest

from app.domain import analyze


class AgentWorkflowTests(unittest.TestCase):
    def test_agent_requires_human_review(self) -> None:
        run = analyze("Investigate the synthetic portfolio scenario.")
        self.assertEqual(run.status, "pending_review")
        self.assertIn("require_human_review", run.trace)
        self.assertIn("review_queue", run.deterministic_result)


if __name__ == "__main__":
    unittest.main()
