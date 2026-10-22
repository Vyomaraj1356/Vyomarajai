"""Evidence-state model for Jarvis runtime status; performs no actions or network I/O."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RuntimeState(str, Enum):
    NOT_CONFIGURED = "not_configured"
    CONFIGURED_UNVERIFIED = "configured_unverified"
    REQUEST_FAILED = "request_failed"
    RESPONSE_UNVERIFIED = "response_unverified"
    PROVIDER_MODEL_VERIFIED = "provider_model_verified"
    RUNTIME_VERIFIED = "runtime_verified"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ProviderEvidence:
    """Evidence collected by a separate verifier; booleans are claims, not authentication."""

    configured: bool = False
    request_attempted: bool = False
    request_succeeded: bool = False
    provider_confirmed: bool = False
    model_confirmed: bool = False
    runtime_health_confirmed: bool = False
    release_id: str = ""
    blocked: bool = False

    def state(self) -> RuntimeState:
        """Resolve the strongest state justified by consistent evidence."""
        if self.blocked:
            return RuntimeState.BLOCKED
        if self.request_succeeded and not self.request_attempted:
            raise ValueError("A successful request requires an attempted request.")
        if (self.provider_confirmed or self.model_confirmed) and not self.request_succeeded:
            raise ValueError("Provider/model confirmation requires a successful request.")
        if self.runtime_health_confirmed and not (
            self.provider_confirmed and self.model_confirmed and self.release_id.strip()
        ):
            raise ValueError("Runtime verification requires provider, model, and release evidence.")
        if not self.configured:
            return RuntimeState.NOT_CONFIGURED
        if not self.request_attempted:
            return RuntimeState.CONFIGURED_UNVERIFIED
        if not self.request_succeeded:
            return RuntimeState.REQUEST_FAILED
        if not (self.provider_confirmed and self.model_confirmed):
            return RuntimeState.RESPONSE_UNVERIFIED
        if not (self.runtime_health_confirmed and self.release_id.strip()):
            return RuntimeState.PROVIDER_MODEL_VERIFIED
        return RuntimeState.RUNTIME_VERIFIED

    def public_status(self) -> dict[str, object]:
        """Return conservative status fields; never infer action or DR permissions."""
        return {
            "state": self.state().value,
            "tool_execution_enabled": False,
            "publishing_enabled": False,
            "dr_ready": False,
        }
