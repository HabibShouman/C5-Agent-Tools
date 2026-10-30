# C5 — Verification record

**Author: Habib Shouman | Updated: 31 October 2026**

## Executed checks

- Read the supplied three-page C5 brief and cited materials. No separate rubric, lecture notes or starter files were supplied.
- Nine standalone application checks passed locally on Windows with Python 3.10/Pydantic 2.12.5. Python 3.11.15 syntax compilation also passed. The summary contains 358 whitespace-separated words, excluding references. The original ZIP passed CRC and file-presence checks.
- Published all source, documentation, both test modules and the GitHub workflow: https://github.com/HabibShouman/C5-Agent-Tools.
- GitHub Actions successfully installed current dependencies on Ubuntu 26.04 with CPython 3.11.17. Observed principal versions: FastMCP 4.1.3, OpenAI Agents SDK 0.24.0, MCP 2.3.0, Pydantic 2.14.1, pytest 9.1.1 and pytest-asyncio 1.4.0. See `evidence/installed-versions-ci.txt` and the exact pip-freeze artifact on the run.
- The initial CI run passed 15 application pytest cases but failed on an obsolete camelCase field access in the integration test. Updated the test to current SDK snake_case fields; no core business-logic change was needed.
- The corrected run passed **all 16 pytest cases**, including the subprocess/stdio MCP integration test. The nine standalone checks passed in the same run. These overlap in application behavior and must not be interpreted as 25 independent reliability experiments.
- The integration case confirms server startup, exactly three discovered tools, typed input/output schemas, read-only lookup, all three successful tool calls, unknown-space and validation errors, conflicting/repeated request IDs, and independent database inspection.

**Successful run:** https://github.com/HabibShouman/C5-Agent-Tools/actions/runs/39967092453

**Tested source commit:** d5fa23bc2ab6890d7db5e9dc6eceef3ee72b02d1. A subsequent host update added redacted provider-error diagnostics; the live runs below used that update. It did not alter tool business logic. The initial failing run remains visible as evidence of the corrected compatibility defect.

## Remaining limits

- The user installed dependencies in Windows and supplied pytest output reporting 16 passed in 6.37 seconds. Separate agent-shell DNS restrictions persisted and must not be confused with the successful user-terminal runs. No Colab run was required or performed.
- Live Gemini requests succeeded in the user terminal: the model selected each of the three MCP tools, received results, and generated appropriate final responses. The missing-room lookup returned an MCP error that the model reported correctly. See `evidence/live-run.md`. Exact active model ID was not printed in the supplied successful transcript; the preceding setup selected gemini-3.1-flash-lite. Capture MODEL_NAME in the recording to confirm it. Model latency and cost remain unmeasured.
- No actual 5–7-minute screencast was recorded or uploaded. The recording guide is preparation, not video evidence.
- The fixed teaching catalogue does not represent institutional data, live occupancy or booking availability. Saved sessions are local personal records.

## Before submission

1. Record the working three-tool demonstration and failure within 5–7 minutes, showing the active MODEL_NAME without displaying credentials.
2. Upload the video and add its real link and confirmed recording model to `SUBMISSION_LINKS.md`.

The deterministic checks establish the tested application and MCP behaviors. They do not establish general model reliability. The live demonstration is evidenced, but the required video and its accessible link remain missing.

## Live verification evidence, 31 October 2026

The user supplied terminal output for successful Data, Action and Orchestration tool calls and for a predictable unknown-space failure. The agent also independently executed the read-only `inspect_sessions.py` command against the same local database and confirmed both persisted records. These are development demonstrations, not held-out evaluation. Earlier NotFoundError, HTTP 503 and timeout attempts are preserved in the conversation; they were not counted as successes.
