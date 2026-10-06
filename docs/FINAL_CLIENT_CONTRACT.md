# FINAL CLIENT CONTRACT

All first-party clients are thin authenticated clients.

## Supported clients

- Web
- Android
- macOS

## Shared contract

```
Client
  -> HTTPS
  -> Vyomaraj API
  -> Auth / Policy
  -> Vyomaraj Core
  -> Jarvis
  -> ShriYantra
  -> Agent Router
  -> Provider / Tool / Data adapters
```

The clients must not implement provider-specific business logic or maintain independent copies of the agent registry.

## Required shared capabilities

- chat/task execution
- streaming task status
- agent selection/routing
- memory and knowledge access
- content workflow
- reports
- health/DR status
- owner settings
- audit events

## Authentication boundary

Authentication is server-enforced. Client credentials/secrets are never embedded in browser/mobile/desktop source.

Voice, biometric and owner-passcode mechanisms remain a final integration/configuration stage.
