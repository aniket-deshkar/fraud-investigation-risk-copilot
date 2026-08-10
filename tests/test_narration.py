import unittest
from unittest.mock import MagicMock, patch

from agentic_core.contracts import Explanation
from agentic_core.narration import Narrator
from agentic_core.settings import AgentSettings


class NarratorTests(unittest.TestCase):
    @patch("langchain_openai.ChatOpenAI")
    def test_openai_credentials_enable_luna_structured_output(self, chat_openai: MagicMock) -> None:
        expected = Explanation(
            summary="Verified explanation",
            rationale="Based only on the supplied deterministic result.",
            next_steps=["Review the evidence"],
        )
        chat_openai.return_value.with_structured_output.return_value.invoke.return_value = expected
        narrator = Narrator(AgentSettings(openai_api_key="test-key", openai_model="gpt-5.6-luna"))

        explanation, mode = narrator.explain(
            "test-domain",
            "Explain this result",
            {"decision": "review"},
            [{"source": "fixture", "fact": "verified", "value": True}],
            expected,
        )

        self.assertEqual(mode, "openai")
        self.assertEqual(explanation, expected)
        chat_openai.assert_called_once_with(model="gpt-5.6-luna", temperature=0, api_key="test-key")
        chat_openai.return_value.with_structured_output.assert_called_once_with(Explanation)


if __name__ == "__main__":
    unittest.main()
