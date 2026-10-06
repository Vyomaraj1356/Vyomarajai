# ShriYantra Owner-Only Authority, Identity and Consent Policy

Status: normative security design. No credentials, biometric templates, passcodes, or personal phone numbers belong in this file or source control.

## 1. Authority root

- The verified system owner is the sole authority for creating/inviting users, approving memberships, granting/revoking roles, granting/revoking agent capabilities, changing the authority policy, enabling external integrations, and authorizing production-impacting actions.
- Vyomaraj/Bharath and Jarvis/Laxman are autonomous operators only within explicitly delegated scopes. They cannot create users, elevate their own permissions, modify the owner's identity, disable owner approval, change authentication factors, or authorize themselves to bypass Harness.
- Arena, LLM providers, MCP servers, agents, scheduled jobs and recovery automation are never owner principals.
- No second administrator is created by default. A break-glass recovery procedure may restore the owner's access but must not silently create a new owner.

## 2. Permission administration

The owner control panel must support add/invite, suspend, revoke, delete where legally and operationally safe, restore, and role/capability changes. It must support per-agent grants for:
- text input and text response;
- voice input, transcription and voice response;
- access to selected tools, projects, data classes and memories;
- task execution, publishing, code changes, deployment and recovery operations.

Permissions are deny-by-default, time-bounded where appropriate, scoped to purpose and environment, revocable immediately, and logged. An agent may request a permission but cannot approve the request. The owner may delegate a narrow task capability without granting user-administration rights. User removal must revoke sessions/tokens, stop queued work where safe, remove access to shared resources and preserve required audit records.

## 3. Strong owner authentication

Preferred owner authentication:
1. A phishing-resistant passkey/WebAuthn security key or device passkey.
2. Local device biometric (fingerprint/face) used to unlock the passkey; biometric templates remain in the device's secure hardware and are not uploaded to ShriYantra, agents, GitHub, or model context.
3. A separate hardware-backed or authenticator-app second factor where supported, plus offline recovery codes stored securely.
4. Step-up reauthentication for adding users, granting permissions, changing authentication/recovery settings, connecting providers, publishing externally, deleting data, production deployment, failover/failback, and changing backup policy.

A phone number or WhatsApp account is a contact/notification/recovery channel, not sufficient proof of identity by itself. WhatsApp OTP can be offered only if an approved, verified authentication provider explicitly supports it, with rate limits, anti-replay, expiry, SIM-swap/account-takeover risk controls and stronger step-up for privileged operations. Never ask an agent to read, store, forward or repeat passcodes. Never put passcodes, recovery codes, access tokens or biometric data in prompts, chat logs, repository files, RAG or MAG.

## 4. Owner command and approval flow

owner authenticates -> ShriYantra verifies passkey/session -> risk engine classifies request -> show exact action, target, scope and consequences -> owner approves or denies -> Harness issues short-lived scoped authorization -> agent/runtime executes -> verify outcome -> immutable audit event -> notify owner.

Voice requests are intent, not authentication alone. For sensitive operations, require a fresh step-up confirmation in the trusted owner interface; a voice clone or recorded phrase must not be enough. The confirmation must bind to the specific action, target and scope, not a generic “yes”.

## 5. Updates, patches and scaling

Agents may discover updates, propose changes, create a branch/PR, run tests, prepare a rollback plan and report risk. They may not independently grant permissions, change owner auth, merge privileged policy changes, push directly to protected production branches, rotate owner factors, or execute destructive migrations. The owner approves production promotion according to risk. Critical security patches may be staged automatically in a sandbox, but production rollout remains governed by explicit policy, health checks, canary and rollback. Keep signed/versioned configuration and immutable pre-change snapshots.

## 6. Emergency and recovery

- Owner can immediately revoke a session, provider token, agent capability or user.
- If the owner account is suspected compromised, freeze privileged mutations, revoke sessions, preserve evidence, and require recovery through an independently secured passkey/recovery process.
- No agent can unfreeze privileged operations or change the owner through a self-approved recovery.
- Backup restore and failover preserve the authority registry and audit trail, but restore must not roll back a newer revocation or resurrect removed access. Reconcile revocation/security epochs before reopening execution.
- If the owner cannot be authenticated, non-privileged health checks and safe read-only diagnostics may continue; user administration, external publishing, destructive actions and authority changes remain blocked.

## 7. Acceptance tests

- Non-owner cannot invite/create users or grant any role.
- Bharath, Jarvis, Hermes and Arena cannot self-elevate or disable the owner gate.
- Voice-only impersonation and replayed approvals fail.
- Lost device/session can be revoked; recovery requires an independent strong factor.
- Owner grants and revokes text/voice/tool scopes independently per agent.
- Revocation blocks new tasks and safely cancels or fences in-flight privileged tasks.
- Every privileged action records actor, authentication strength, approval, target, policy/config version, result and correlation ID without recording secrets.
- Backup/restore cannot resurrect revoked users, tokens or capabilities.
- No biometric template, passcode, OTP, recovery code or phone number is committed to the repository.
