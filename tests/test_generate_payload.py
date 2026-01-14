import unittest
from scripts.generate_payload import build_payload, PayloadConfig


class TestGeneratePayload(unittest.TestCase):
    def setUp(self):
        self.event = {
            "head_commit": {"message": "feat: update deploy"},
            "sender": {"avatar_url": "https://example.com/avatar.png"},
        }
        self.common = {
            "ref": "refs/heads/main",
            "event_name": "push",
            "server_url": "https://github.com",
            "repository": "forecho/example",
            "run_id": "12345",
            "sha": "abcdef1234567890",
            "actor": "forecho",
            "channel_id": "C123",
        }

    def test_build_payload_en(self):
        config = PayloadConfig(language="en", service_name="Deploy", color="#2eb886")
        payload = build_payload(self.event, self.common, config)
        attachment = payload["attachments"][0]
        self.assertEqual(attachment["fields"][0]["title"], "Ref")
        self.assertIn("Deploy", attachment["fields"][2]["value"])
        self.assertIn("abcdef1", attachment["fields"][3]["value"])

    def test_build_payload_zh(self):
        config = PayloadConfig(language="zh", service_name="Deploy", color="#2eb886")
        payload = build_payload(self.event, self.common, config)
        attachment = payload["attachments"][0]
        self.assertEqual(attachment["fields"][1]["title"], "事件")
        self.assertTrue(attachment["text"].startswith("*消息*"))


if __name__ == "__main__":
    unittest.main()
