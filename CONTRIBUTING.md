# Contributing

Thanks for helping make paper-to-agent workflows more transparent and reproducible.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[pdf,mcp,dev]'
python -m pytest
```

## Contribution principles

- Keep paper facts, verified results, and inferences explicitly separated.
- Preserve provenance whenever a new report field, resource, or tool is introduced.
- Never make downloading, execution, uploads, or credential use implicit.
- Add tests for changed parsing, discovery, safety, or manifest behavior.
- Do not commit papers, data, generated workspaces, API keys, or credentials.

## Pull requests

Describe the user-facing behavior, safety impact, and test command in each pull request. Small focused changes are preferred. New executable integrations must remain opt-in and document their authorization boundary.
