# Security model

The default mode is read-only. The package does not execute downloaded code, install system packages, upload user data, use credentials, or push Git changes.

All generated resource paths are resolved under the workspace and checked before reading. External links are recorded as candidates with evidence and confidence; discovery is not proof that a resource is official or safe. Any future execution adapter must use a separate sandbox, fixed commits, explicit user authorization, resource limits, and a deny-by-default network policy.
