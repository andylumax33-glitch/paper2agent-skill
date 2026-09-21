---
name: paper2agent
description: Convert a research paper and its publicly available materials into a traceable, resource-first MCP agent package.
---

# Paper2Agent Skill

Use this skill when a user asks to understand a paper, locate its code or data, reproduce a method, or apply a paper's method to a project.

## Rules

- Start with the uploaded paper or DOI and create a source report.
- Build a resource layer before attempting execution.
- Treat external code and data as untrusted. Never execute downloaded code without explicit user authorization.
- Preserve provenance for every important claim, resource, tool, and result.
- Label outputs as verified, source-grounded, inferred, missing, conflicting, or unavailable.
- If required evidence is missing, say so instead of inventing it.
- Only expose an executable tool after it has a declared source and validation result.

## Workflow

1. Register and parse the source.
2. Discover and rank public code, data, supplementary materials, and project pages.
3. Build the resource manifest and provenance graph.
4. Ask for authorization before downloading or executing external code.
5. Generate only validated tools; otherwise use resource-only mode.
6. Produce a final report with limitations, evidence, and next actions.
