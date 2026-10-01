import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_app import LocalAgent


class ModelEventTests(unittest.TestCase):
    def test_secret_event_does_not_echo_or_store_secret(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = LocalAgent(Path(tmp))
            secret = "synthetic-key-do-not-store"
            with patch.object(agent.muse_models, "set_profile_secret", return_value={
                "profile_id": "high-default", "origin": "https://api.example.test:443", "has_secret": True,
            }) as setter:
                result = agent.handle({"type": "model_secret_set", "profile_id": "high-default", "secret": secret})
            self.assertTrue(result["ok"])
            setter.assert_called_once_with("high-default", secret)
            self.assertNotIn(secret, json.dumps(result))
            self.assertFalse(any(secret in file.read_text(encoding="utf-8") for file in Path(tmp).rglob("*.json")))
            self.assertEqual(agent.handle({"type": "model_secret_set", "profile_id": "high-default",
                                           "secret": secret, "extra": "x"})["status"], "REJECTED")

    def test_pricing_events_use_real_gateway_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = LocalAgent(Path(tmp))
            self.assertTrue(agent.handle({"type": "model_pricing_get"})["ok"])
            request = {"type": "model_pricing_set", "profile_id": "high-default",
                       "model": "unknown", "origin": "https://api.example.test:443",
                       "input_cny_per_million": "1", "output_cny_per_million": "2",
                       "source": "synthetic", "confirmed": True}
            invalid = agent.handle(request)
            self.assertFalse(invalid["ok"])
            self.assertEqual(invalid["error"], "model_pricing_not_saved")
            with patch.object(agent.muse_models, "configure_pricing", return_value={
                "profile_id": "high-default", "origin": "https://api.example.test:443", "currency": "CNY",
            }):
                saved = agent.handle(request)
            self.assertTrue(saved["ok"])
            self.assertEqual(saved["profile_id"], "high-default")
            self.assertEqual(saved["origin"], "https://api.example.test:443")

    def test_capability_view_disables_unknown_model_strength(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = LocalAgent(Path(tmp))
            result = agent.handle({"type": "model_capabilities_get", "profile_id": "high-default"})
            self.assertTrue(result["ok"])
            self.assertFalse(result["capabilities"]["reasoning_supported"])
            self.assertEqual(result["capabilities"]["reasoning_efforts"], [])
            self.assertFalse(agent.handle({"type": "model_capabilities_get",
                                           "profile_id": "missing"})["ok"])


if __name__ == "__main__":
    unittest.main()
