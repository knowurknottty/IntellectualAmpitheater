# Evidence directory

Files here are sanitized witnesses for real integration and acceptance runs. They must not contain API keys, bearer tokens, cookies, session secrets, or ambient credentials.

Current witnesses:

- `task4-local-llama.md`: real llama.cpp OpenAI-compatible stream and exact model identity.
- `task5-two-seat-dispatch.md`: two ordinary IntelAMP seats through provider concurrency `1`, with distinct durable run IDs.
- `task6-http-gateway.md`: loopback HTTP API, real local model dispatch, SSE event IDs, and `Last-Event-ID` resume.
- `task10-local-acceptance.md`: one-seat, six-seat, cancel-in-flight, and sibling-isolation real local acceptance.
- `task10-ui-audit.md`: anti-slop counts, contrast checks, attention/accessibility static audit, and explicit unverified items.
- Tranche 0 final acceptance evidence is added by the local acceptance script.

Unit-test fixtures are protocol tests only. They are not integration evidence.
