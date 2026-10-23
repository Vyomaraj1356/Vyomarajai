import unittest

from ops.jarvis.runtime_evidence import ProviderEvidence, RuntimeState


class ProviderEvidenceTests(unittest.TestCase):
    def test_unconfigured_is_not_configured(self):
        self.assertEqual(ProviderEvidence().state(), RuntimeState.NOT_CONFIGURED)

    def test_configuration_without_request_is_unverified(self):
        self.assertEqual(
            ProviderEvidence(configured=True).state(),
            RuntimeState.CONFIGURED_UNVERIFIED,
        )

    def test_attempted_failed_request_is_failed(self):
        self.assertEqual(
            ProviderEvidence(configured=True, request_attempted=True).state(),
            RuntimeState.REQUEST_FAILED,
        )

    def test_success_without_provider_and_model_confirmation_is_unverified(self):
        evidence = ProviderEvidence(
            configured=True, request_attempted=True, request_succeeded=True
        )
        self.assertEqual(evidence.state(), RuntimeState.RESPONSE_UNVERIFIED)

    def test_provider_and_model_confirmation_is_not_runtime_verification(self):
        evidence = ProviderEvidence(
            configured=True,
            request_attempted=True,
            request_succeeded=True,
            provider_confirmed=True,
            model_confirmed=True,
        )
        self.assertEqual(evidence.state(), RuntimeState.PROVIDER_MODEL_VERIFIED)

    def test_runtime_verified_requires_release_and_health_evidence(self):
        evidence = ProviderEvidence(
            configured=True,
            request_attempted=True,
            request_succeeded=True,
            provider_confirmed=True,
            model_confirmed=True,
            runtime_health_confirmed=True,
            release_id="release-123",
        )
        self.assertEqual(evidence.state(), RuntimeState.RUNTIME_VERIFIED)

    def test_success_without_attempt_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "attempted request"):
            ProviderEvidence(configured=True, request_succeeded=True).state()

    def test_attempt_without_configuration_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "configured provider"):
            ProviderEvidence(request_attempted=True).state()

    def test_provider_or_model_confirmation_without_success_is_rejected(self):
        for kwargs in (
            {"provider_confirmed": True},
            {"model_confirmed": True},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaisesRegex(ValueError, "successful request"):
                    ProviderEvidence(configured=True, request_attempted=True, **kwargs).state()

    def test_runtime_health_without_complete_evidence_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "provider, model, and release"):
            ProviderEvidence(
                configured=True,
                request_attempted=True,
                request_succeeded=True,
                provider_confirmed=True,
                model_confirmed=True,
                runtime_health_confirmed=True,
            ).state()

    def test_blocked_state_takes_precedence_and_never_enables_actions(self):
        status = ProviderEvidence(blocked=True, request_succeeded=True).public_status()
        self.assertEqual(status["state"], RuntimeState.BLOCKED.value)
        self.assertIs(status["tool_execution_enabled"], False)
        self.assertIs(status["publishing_enabled"], False)
        self.assertIs(status["dr_ready"], False)

    def test_even_runtime_verified_does_not_grant_action_permissions(self):
        evidence = ProviderEvidence(
            configured=True,
            request_attempted=True,
            request_succeeded=True,
            provider_confirmed=True,
            model_confirmed=True,
            runtime_health_confirmed=True,
            release_id="release-123",
        )
        status = evidence.public_status()
        self.assertEqual(status["state"], RuntimeState.RUNTIME_VERIFIED.value)
        self.assertFalse(status["tool_execution_enabled"])
        self.assertFalse(status["publishing_enabled"])
        self.assertFalse(status["dr_ready"])


if __name__ == "__main__":
    unittest.main()
