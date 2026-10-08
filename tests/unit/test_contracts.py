"""Fresh protocol boundary tests using synthetic targets, never live windows."""

import copy
import unittest
from datetime import datetime, timedelta, timezone

from troubleshoot.contracts import (
    ContractError, Observation, RunRequest, Target, fields, parse_action, require_target,
)


def no_arguments(payload):
    return fields(payload, set())


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(timezone.utc)
        self.target = Target(100, 200, self.now.isoformat())
        self.observation = Observation("obs-1", self.now.isoformat(), self.target)
        self.payload = {
            "action_id": "action-1", "operation": "inspect_target", "arguments": {},
            "target": {"handle": 100, "pid": 200, "started": self.now.isoformat()},
            "observation_id": "obs-1",
        }
        self.registry = {"inspect_target": no_arguments}

    def test_local_diagnosis_is_default(self):
        request = RunRequest("Inspect the selected application")
        self.assertEqual((request.mode, request.provider), ("diagnose", "ollama"))

    def test_hosted_text_requires_consent(self):
        with self.assertRaises(ContractError):
            RunRequest("Inspect app", provider="gemma_api")

    def test_hosted_images_require_separate_consent(self):
        with self.assertRaises(ContractError):
            RunRequest("Inspect app", provider="gemma_api", cloud_consent=True, vision_enabled=True)

    def test_consent_is_not_coerced_from_text(self):
        with self.assertRaises(ContractError):
            RunRequest("Inspect app", cloud_consent="false")

    def test_unknown_provider_cannot_be_fallback(self):
        with self.assertRaises(ContractError):
            RunRequest("Inspect app", provider="remote")

    def test_registered_action_round_trip(self):
        action = parse_action(self.payload, self.registry)
        require_target(action, self.observation, self.now)
        self.assertEqual(action.to_dict(), self.payload)

    def test_unknown_operation_rejected(self):
        self.payload["operation"] = "run_shell"
        with self.assertRaises(ContractError):
            parse_action(self.payload, self.registry)

    def test_extra_model_fields_rejected(self):
        self.payload["shell"] = "arbitrary command"
        with self.assertRaises(ContractError):
            parse_action(self.payload, self.registry)

    def test_operation_validator_rejects_arguments(self):
        self.payload["arguments"] = {"command": "arbitrary command"}
        with self.assertRaises(ContractError):
            parse_action(self.payload, self.registry)

    def test_boolean_is_not_a_window_handle(self):
        self.payload["target"]["handle"] = True
        with self.assertRaises(ContractError):
            parse_action(self.payload, self.registry)

    def test_replaced_process_is_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload["target"]["started"] = (self.now - timedelta(seconds=1)).isoformat()
        with self.assertRaises(ContractError):
            require_target(parse_action(payload, self.registry), self.observation, self.now)

    def test_wrong_observation_rejected(self):
        self.payload["observation_id"] = "other-observation"
        with self.assertRaises(ContractError):
            require_target(parse_action(self.payload, self.registry), self.observation, self.now)

    def test_stale_observation_rejected(self):
        with self.assertRaises(ContractError):
            self.observation.require_fresh(self.now + timedelta(seconds=6))

    def test_future_observation_rejected(self):
        with self.assertRaises(ContractError):
            self.observation.require_fresh(self.now - timedelta(seconds=1))

    def test_naive_timestamp_rejected(self):
        with self.assertRaises(ContractError):
            Observation("obs", "2026-10-08T11:00:00", self.target)

    def test_invalid_age_policy_rejected(self):
        for limit in (float("nan"), float("inf"), True, 0, -1):
            with self.subTest(limit=limit), self.assertRaises(ContractError):
                self.observation.require_fresh(self.now, limit)


if __name__ == "__main__":
    unittest.main()
