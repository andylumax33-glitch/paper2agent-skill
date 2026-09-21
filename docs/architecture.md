# Architecture

The MVP uses a resource-first pipeline:

    source -> parse -> discover -> manifest/provenance -> resource-only MCP

External code is not executed during ingestion or discovery. The resource layer remains useful when code, data, or dependencies are missing. JSON reports make each stage traceable and resumable.
