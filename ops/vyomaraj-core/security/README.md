# ShriYantra Cryptographic Security

This layer defines the inherited cryptographic baseline for Vyomaraj.

## Baseline

- AES-256-GCM authenticated encryption for sensitive data.
- Envelope encryption: per-object/record DEKs wrapped by non-exportable KMS/HSM KEKs.
- TLS 1.3 minimum for network transport.
- mTLS/workload identity for private service-to-service traffic.
- Argon2id for passwords; passwords are never reversibly encrypted.
- Signed release artifacts and hash-chained/signed audit checkpoints.
- Crypto agility with a post-quantum migration path using ML-KEM-768 and ML-DSA-65 hybrid modes only where the exact runtime/library/provider is verified.
- Default-deny ingress/egress and no public control plane.
- Short-lived, least-privilege credentials through the tool broker.

## Operational rule

Repository configuration is not evidence that KMS/HSM, mTLS, certificate rotation, or PQC are live. Those become VERIFIED only after authenticated runtime probes succeed.

Never place keys, tokens, passwords, certificates with private keys, or recovery secrets in this repository.

## Recovery

Cryptographic recovery must preserve key IDs and encrypted DEKs. A recovery copy must not overwrite a healthy copy blindly. Rewrap/restore is performed through the KMS/HSM policy and then verified before traffic is restored.
