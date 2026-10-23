# C5 — Requirement coverage

**Habib Shouman**

No weighted grading rubric was attached. This table maps the supplied brief; it is not an invented points allocation.

| Brief requirement | Identifiable evidence | Status |
|---|---|---|
| Read assigned MCP article | `SUMMARY.md`, references 1–2 | Read |
| Explore one existing server | Fetch README/source critique in `SUMMARY.md` | Source inspected; not run |
| Summary 300–400 words | `SUMMARY.md`, Summary section | Count checked during packaging |
| Explain Host/Client/Server | Summary paragraph 2; README architecture | Supplied |
| Critique single-purpose interfaces and predictable behavior | Summary paragraphs 3–4 | Supplied |
| Choose a coherent theme | README: Campus Study Toolkit | Supplied |
| Exactly three tools, one per category | Three decorators in `server.py`; discovery assertion in `tests/test_mcp.py` | Passed MCP discovery: exactly three tools |
| Data read without mutation | `lookup_space`; read-only tests and no-database assertion | Core check passed |
| Action produces an effect | `save_study_session`; SQLite rows checked independently | Core check passed |
| Orchestration coordinates primitives | `StudyService.plan_session`; server wrapper; sequence and failed-lookup tests | Core check passed |
| Descriptions and typed arguments/outputs | Docstrings, Annotated/Field constraints, Space/SavedSession/Plan models | Input/output schemas checked in passing integration test |
| Predictable failure for each tool | Unknown space; invalid duration/conflicting ID/storage; lookup-before-write stop | Application and protocol failure checks passed |
| FastMCP server | `server.py`, stdio entry point | Server subprocess startup passed in CI |
| OpenAI Agents SDK agent host/client | `host.py`: Agent, Runner, MCPServerStdio | SDK client integration passed; model-selected calls pending |
| Tests or interactive scripts | `check_core.py`, `tests/`, `inspect_sessions.py` | Nine standalone checks and all 16 pytest cases passed in CI |
| Configuration and setup README | `README.md`, requirements and pyproject | Dependencies installed successfully in GitHub Actions |
| 5–7-minute video introduces categories and live round trips | `DEMO_GUIDE.md` supplies timeline/prompts | Actual recording missing |
| Challenges and solutions in demo | Demo timeline: tool boundaries, error handling, retries | Guide supplied; recording pending |
| Share repository and recording | `SUBMISSION_LINKS.md` | Repository linked; video pending |
| Reflection, 1–2 paragraphs | `REFLECTION.md`, two paragraphs | Supplied |

There are no supplied bonus requirements or explicit dependencies on another assignment. This package addresses C5 only.
