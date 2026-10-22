# Jarvis provider preflight

The provider preflight is a read-only static configuration check. It must never send a model request, enable tools, publish content, or infer live connectivity from environment variables.

Expected status values:
- `not_configured`: no provider endpoint or model is configured.
- `incomplete`: only part of the minimum configuration is present.
- `invalid`: static validation rejected the selected provider configuration.
- `configured_unverified`: static validation passed, but no live provider request was made.

Use the `--json` option for machine-readable output and `--require-configured` in a release gate when static configuration is required. Keep configuration values out of logs. A live acceptance test remains a separate owner-approved step and must record only sanitized evidence.
