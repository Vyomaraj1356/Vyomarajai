# Communication + Location Integration Readiness

- ShriYantra is the home/authority root.
- Vyomaraj is the center and is addressable as Bharath.
- Jarvis is addressable as Laxman and reports his authenticated current runtime/device location and current activity when asked.
- The UI may display the Hanuman flag asset with **जय श्री राम**.
- Incoming mail to the owner's public contact address is a first-class communication lane. The address is never hardcoded in a public file: the owner publishes it with `ops/vyomaraj-core/handover/set_public_contact.py`, which stores it in `config/public-contact.json` (owner_approved). Until then it stays redacted.
- Vyomaraj/Bharath reasons and coordinates; Jarvis/Laxman executes.
- Routine coordinator/collaborator/user communication can be handled autonomously after verification.
- Abusive/offensive messages are not argued with or amplified; they are quarantined/hidden where platform APIs permit.
- Good feedback and constructive improvement requests become content/product improvement signals.
- Owner escalation is reserved for attention, finance authorization/decisions, legal consultation/decisions, security incidents, and irreversible high-impact actions.
- Every escalation carries a proposed solution and risk/deadline summary.

## Required live adapters

1. Authenticated mailbox connector for the owner mailbox (address held in deployment config / `config/public-contact.json`, never in a public tracked file).
2. Platform-specific social APIs/webhooks for read/reply/moderation.
3. Authenticated runtime location provider for the device currently running Jarvis.
4. Voice/STT/TTS adapter for Bharath and Laxman.
5. Owner WhatsApp notification/approval adapter.
6. Durable state/audit store.

## Verification rule

Repository code/configuration is PRESENT/CONFIGURED, not proof of live operation. A capability becomes VERIFIED only after an authenticated end-to-end test proves it in the target environment.

## Safety rule

No automatic legal conclusion, financial transfer, credential change, destructive action, or unapproved public publication is permitted merely because an email/comment/voice command asks for it.
