# C5 — Verification record

**Author: Habib Shouman | Date: 23 October 2026**

## Executed checks

- Read the supplied three-page C5 brief and cited materials. No separate rubric, lecture notes or starter files were supplied.
- Nine standalone application checks passed locally on Windows with Python 3.10/Pydantic 2.12.5. Python 3.11.15 syntax compilation also passed. The summary contains 358 whitespace-separated words, excluding references. The original ZIP passed CRC and file-presence checks.
- Published all source, documentation, both test modules and the GitHub workflow: https://github.com/HabibShouman/C5-Agent-Tools.
- GitHub Actions successfully installed current dependencies on Ubuntu 26.04 with CPython 3.11.17. Observed principal versions: FastMCP 4.1.3, OpenAI Agents SDK 0.24.0, MCP 2.3.0, Pydantic 2.14.1, pytest 9.1.1 and pytest-asyncio 1.4.0. See `evidence/installed-versions-ci.txt` and the exact pip-freeze artifact on the run.
- The initial CI run passed 15 application pytest cases but failed on an obsolete camelCase field access in the integration test. Updated the test to current SDK snake_case fields; no core business-logic change was needed.
- The corrected run passed **all 16 pytest cases**, including the subprocess/stdio MCP integration test. The nine standalone checks passed in the same run. These overlap in application behavior and must not be interpreted as 25 independent reliability experiments.
- The integration case confirms server startup, exactly three discovered tools, typed input/output schemas, read-only lookup, all three successful tool calls, unknown-space and validation errors, conflicting/repeated request IDs, and independent database inspection.

**Successful run:** https://github.com/HabibShouman/C5-Agent-Tools/actions/runs/39967092453

**Tested source commit:** d5fa23bc2ab6890d7db5e9dc6eceef3ee72b02d1. Later documentation/evidence changes do not change the tested executable source. The initial failing run remains visible as evidence of the corrected compatibility defect.

## Remaining limits

- Local dependency installation remains blocked by DNS/network restrictions in the authoring environment. The successful dependency-backed execution was in GitHub Actions on Linux, not Windows or Colab.
- No live OpenAI, Gemini or local-model request occurred. No provider key was configured in the session. The host and client import successfully, but actual model-selected routing, provider compatibility, model latency and cost remain unmeasured.
- No actual 5–7-minute screencast was recorded or uploaded. The recording guide is preparation, not video evidence.
- The fixed teaching catalogue does not represent institutional data, live occupancy or booking availability. Saved sessions are local personal records.

## Before submission

1. Configure an available tool-calling model and run the three model-selected tool demonstrations plus a failure. Record actual provider/model details.
2. Inspect the resulting database independently, record and upload the 5–7-minute screencast, and add its real link to `SUBMISSION_LINKS.md`.
3. Update documentation after the live run without overstating what it establishes.

The deterministic checks establish the tested application and MCP behaviors. They do not establish general model reliability. The submission is incomplete until the live demonstration and recording are supplied.
